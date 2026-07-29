from urllib import response
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from telegram.ext import MessageHandler, filters
from database import create_table, save_message
from database import get_chat_history
from google.genai.errors import ServerError
from google import genai
import os


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. How can I assist you today?")
    await update.message.reply_text(response.text)
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = update.message.from_user.id
        message_from = update.message.from_user.username
        user_message = update.message.text
        save_message(telegram_id, message_from, user_message)
        chat_history = get_chat_history(telegram_id)
        print(chat_history)

        try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents = user_message
                    )
            
                await update.message.reply_text(response.text)
        except ServerError:
                await update.message.reply_text(" Germini is busy at the moment. please try again in a few seconds.")
        
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))



create_table()
app.run_polling()
