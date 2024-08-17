import os
import io
import json
import tempfile
import asyncio
from aiohttp import ClientSession
from telegram import Update, Document, User
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from GeneratePDF import generate_pdf  # Adjust the import as per your project structure
from app import process_resume  # Adjust the import as per your project structure
from json_repair import repair_json
from dotenv import load_dotenv
import aiofiles
import pdfplumber
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables from a .env file
load_dotenv()

# Define your Telegram bot token as an environment variable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# States for the conversation handler
JOB_DESCRIPTION, RESUME = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user: User = update.message.from_user
    if user:
        context.user_data['user_id'] = user.id
        context.user_data['first_name'] = user.first_name
        context.user_data['username'] = user.username
        logging.info(f"User ID: {user.id}, First Name: {user.first_name}, Username: @{user.username}")
    else:
        logging.warning("User details not found.")
    await update.message.reply_text(f'Hello {user.first_name}! Please provide the job description.')
    return JOB_DESCRIPTION

async def receive_job_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['job_description'] = update.message.text
    await update.message.reply_text('Got it! Now, please send the resume in PDF format.')
    return RESUME

async def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

async def receive_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    document: Document = update.message.document
    if document.mime_type == 'application/pdf':
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, 'resume.pdf')
                output_pdf_path = os.path.join(temp_dir, 'processed_resume.pdf')

                file = await context.bot.get_file(document.file_id)
                await file.download_to_drive(custom_path=pdf_path)

                async with aiofiles.open(pdf_path, 'rb') as f:
                    pdf_bytes = await f.read()

                resume_text = await extract_text_from_pdf(pdf_bytes)

                job_description = context.user_data.get('job_description')

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, process_resume, job_description, resume_text)
                
                result = result._result

                # Access the text content
                text_content = result.candidates[0].content.parts[0].text

                text_content = repair_json(text_content.replace("`", "'"))
                if not text_content.strip():
                    logging.error("Error: The JSON string is empty.")
                    await update.message.reply_text('An error occurred while processing the resume.')
                    return ConversationHandler.END
                else:
                    try:
                        text_content = json.loads(text_content)
                    except json.JSONDecodeError as e:
                        logging.error(f"JSONDecodeError: {e}")
                        await update.message.reply_text('An error occurred while processing the resume.')
                        return ConversationHandler.END
                    except Exception as e:
                        logging.error(f"An unexpected error occurred: {e}")
                        await update.message.reply_text('An unexpected error occurred.')
                        return ConversationHandler.END

                await loop.run_in_executor(None, generate_pdf, text_content, output_pdf_path)

                async with aiofiles.open(output_pdf_path, 'rb') as f:
                    await update.message.reply_document(document=await f.read(), filename='processed_resume.pdf')

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            await update.message.reply_text('An error occurred while processing your request.')
            return ConversationHandler.END

    else:
        await update.message.reply_text('Please upload a PDF file.')
        return RESUME

    await update.message.reply_text('Your processed resume has been generated and sent back to you.')
    return ConversationHandler.END

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            JOB_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_job_description)],
            RESUME: [MessageHandler(filters.Document.PDF, receive_resume)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
