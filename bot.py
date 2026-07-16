from turtle import update

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from telegram.ext import MessageHandler, filters
# import update
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. How can I assist you today?")
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))



async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        if user_message.upper() == "Hello" or user_message.lower() == "hello":
          await update.message.reply_text("I'm doing great! How about you?")
        elif user_message.upper() == "How was your day?":
            await update.message.reply_text("It was good, thanks for asking!")
        else:
            await update.message.reply_text("I'm sorry, I didn't understand that. Can you please rephrase?")
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))


app.run_polling()