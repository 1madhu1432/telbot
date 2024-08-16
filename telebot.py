import os
import json
import asyncio
import pdfplumber
from telegram import Update, Document, User, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters
from flask import Flask, request
from GeneratePDF import generate_pdf  # Adjust the import as per your project structure
from app import process_resume  # Adjust the import as per your project structure
from json_repair import repair_json
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define your Telegram bot token as an environment variable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize the bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)
webhook_url = 'https://telbot-rzzf.onrender.com/post'

# Set up Flask
app = Flask(__name__)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Asynchronous function to set the webhook
async def set_webhook():
    await bot.set_webhook(url=webhook_url)

# Flask route to handle incoming webhook updates
@app.route('/post', methods=['POST'])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Define a function to start the conversation
async def start(update: Update, context: CallbackContext) -> int:
    user: User = update.message.from_user
    if user:
        context.user_data['user_id'] = user.id
        context.user_data['first_name'] = user.first_name
        context.user_data['username'] = user.username
        print(f"User ID: {user.id}, First Name: {user.first_name}, Username: @{user.username}")
    else:
        print("User details not found.")
    await update.message.reply_text(f'Hello {user.first_name}! Please provide the job description.')
    return JOB_DESCRIPTION

# Define a function to handle job description input
async def receive_job_description(update: Update, context: CallbackContext) -> int:
    context.user_data['job_description'] = update.message.text
    await update.message.reply_text('Got it! Now, please send the resume in PDF format.')
    return RESUME

# Define a function to handle the resume file upload
async def receive_resume(update: Update, context: CallbackContext) -> int:
    document: Document = update.message.document
    if document.mime_type == 'application/pdf':
        # Get the file and download it locally
        file = await context.bot.get_file(update.message.document)
        pdf_path = 'resume.pdf'
        await file.download_to_drive(pdf_path)

        # Extract text from the PDF
        resume_text = extract_text_from_pdf(pdf_path)

        # Get job description
        job_description = context.user_data.get('job_description')

        # Process the resume with the job description
        result = process_resume(job_description, resume_text)
        result = result._result

        # Access the text content
        text_content = result.candidates[0].content.parts[0].text

        # Repair and parse the JSON string
        text_content = repair_json(text_content.replace("`", "'"))
        if not text_content.strip():
            print("Error: The JSON string is empty.")
        else:
            try:
                text_content = json.loads(text_content)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        # Generate the PDF from the processed content
        output_pdf_path = "processed_resume.pdf"
        generate_pdf(text_content, output_pdf_path)

        # Send the generated PDF file as a reply
        await update.message.reply_document(document=open(output_pdf_path, 'rb'))

    else:
        await update.message.reply_text('Please upload a PDF file.')

    # Clean up the downloaded resume
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    # End the conversation
    return ConversationHandler.END

# Define a function to handle the /start command
async def start_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Welcome! Use /start to begin the process.')

# Running the webhook setup before starting the Flask app
if __name__ == '__main__':
    # Set the webhook before starting Flask
    asyncio.run(set_webhook())
    app.run(port=5000)
