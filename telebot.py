import os
import io
import json
import tempfile
import logging
import asyncio
import aiohttp
from aiohttp import web
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from GeneratePDF import generate_pdf  # Adjust as per your project structure
from app import process_resume  # Adjust as per your project structure
from json_repair import repair_json
from dotenv import load_dotenv
import aiofiles
import pdfplumber

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your server's webhook URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Conversation states
STATE_JOB_DESCRIPTION, STATE_RESUME = range(2)
user_states = {}

async def send_message(chat_id, text):
    logging.info(f"Sending message to chat_id={chat_id}: {text}")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=payload)
        logging.info(f"Response from sendMessage: {await response.text()}")

async def send_document(chat_id, document_path, filename):
    url = f"{TELEGRAM_API_URL}/sendDocument"
    logging.info(f"Sending document {filename} to chat_id={chat_id}")
    async with aiohttp.ClientSession() as session:
        async with aiofiles.open(document_path, 'rb') as f:
            document = await f.read()
        files = {'document': (filename, document)}
        data = {"chat_id": chat_id}
        response = await session.post(url, data=data, files=files)
        logging.info(f"Response from sendDocument: {await response.text()}")

async def handle_start(chat_id, user_data):
    user_data['state'] = STATE_JOB_DESCRIPTION
    await send_message(chat_id, 'Hello! Please provide the job description.')

async def handle_job_description(chat_id, text, user_data):
    user_data['job_description'] = text
    user_data['state'] = STATE_RESUME
    await send_message(chat_id, 'Got it! Now, please send the resume in PDF format.')

async def handle_resume(chat_id, file_id, user_data):
    try:
        logging.info(f"Handling resume for chat_id={chat_id}, file_id={file_id}")
        async with aiohttp.ClientSession() as session:
            file_info_url = f"{TELEGRAM_API_URL}/getFile?file_id={file_id}"
            file_info = await (await session.get(file_info_url)).json()
            logging.info(f"File info: {file_info}")
            file_path = file_info['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

            resume_pdf = await (await session.get(file_url)).read()

        resume_text = await extract_text_from_pdf(resume_pdf)
        logging.info(f"Extracted text from resume: {resume_text[:100]}...")  # Log the first 100 characters

        job_description = user_data.get('job_description')

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, process_resume, job_description, resume_text)
        result = result._result

        # Access and process the text content
        text_content = result.candidates[0].content.parts[0].text
        text_content = repair_json(text_content.replace("`", "'"))

        if not text_content.strip():
            logging.error("Error: The JSON string is empty.")
            await send_message(chat_id, 'An error occurred while processing the resume.')
            return

        try:
            text_content = json.loads(text_content)
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            await send_message(chat_id, 'An error occurred while processing the resume.')
            return

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_pdf:
            output_pdf_path = output_pdf.name

        await loop.run_in_executor(None, generate_pdf, text_content, output_pdf_path)
        await send_document(chat_id, output_pdf_path, 'processed_resume.pdf')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await send_message(chat_id, 'An error occurred while processing your request.')

async def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

async def handle_webhook(request):
    data = await request.json()
    logging.info(f"Webhook received: {data}")
    chat_id = data['message']['chat']['id']
    user_id = data['message']['from']['id']
    text = data['message'].get('text')
    document = data['message'].get('document')

    user_data = user_states.setdefault(user_id, {})

    if 'state' not in user_data:
        await handle_start(chat_id, user_data)
    elif user_data['state'] == STATE_JOB_DESCRIPTION:
        if text:
            await handle_job_description(chat_id, text, user_data)
        else:
            await send_message(chat_id, 'Please provide the job description.')
    elif user_data['state'] == STATE_RESUME:
        if document and document['mime_type'] == 'application/pdf':
            await handle_resume(chat_id, document['file_id'], user_data)
        else:
            await send_message(chat_id, 'Please upload a PDF file.')

    return web.Response(status=200)

async def set_webhook():
    url = f"{TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}"
    logging.info(f"Setting webhook with URL: {url}")
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        logging.info(f"Response from setWebhook: {await response.text()}")

def main():
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    web.run_app(app, port=8000)

if __name__ == '__main__':
    main()
