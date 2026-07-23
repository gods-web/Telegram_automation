from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from telegram.ext import MessageHandler, filters
from database import create_table, save_message
from google.genai.errors import ServerError
from google import genai
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. How can I assist you today?")
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = update.message.from_user.id
        user_message = update.message.text
        save_message(telegram_id, user_message)
        if user_message.lower() == "hello":
            await update.message.reply_text("I'm doing great! How about you?")
        elif user_message.lower() == "i'm fine, how about you?":
            await update.message.reply_text("I'm glad to hear that! I'm doing well too.")
        elif user_message.lower() == "how was your day?":
            await update.message.reply_text("It was good, thanks for asking!")
        else:
            try:
                response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents = user_message
                )
        
                await update.message.reply_text(response.text)
            except ServerError:
                 await update.message.reply_text(" Germini is busy at the moment. please try again in a few seconds.")
            except Exception as e:
                print("Gemini Error:", repr(e))
                await update.message.reply_text("Sorry, I couldn't generate a response.")
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))



create_table()
app.run_polling()
