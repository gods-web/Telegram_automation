from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from telegram.ext import MessageHandler, filters
from database import create_table, save_message
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)

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
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))



create_table()
app.run_polling()
