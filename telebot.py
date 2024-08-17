import os
import logging
from telegram import Update, User
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    if user:
        logging.info(f"User ID: {user.id}, First Name: {user.first_name}, Username: @{user.username}")
    await update.message.reply_text(f'Hello {user.first_name}!')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    logging.info("Starting the bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
