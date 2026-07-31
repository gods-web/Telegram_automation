# from multiprocessing import context
# from turtle import update

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from google.genai import types
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

PHOTO_DIR = "downloads/photos"
VOICE_DIR = "downloads/voice"

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. How can I assist you today?")
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    message_from = update.message.from_user.username
    user_message = update.message.text

    save_message(
        telegram_id,
        message_from,
        "text",
        None,
        None,
        user_message
    )

    chat_history = get_chat_history(telegram_id)
    print(chat_history)

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_message
        )

        await update.message.reply_text(response.text)

    except ServerError:
        await update.message.reply_text(
            "Gemini is busy at the moment. Please try again in a few seconds."
        )
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    message_from = update.message.from_user.username

    photo_file = await update.message.photo[-1].get_file()
    file_id = photo_file.file_id

    file_path = os.path.join(PHOTO_DIR, f"{file_id}.jpg")
    await photo_file.download_to_drive(file_path)
    print("Photo received")
    print("File downloaded")
    save_message(
        telegram_id,
        message_from,
        "photo",
        file_id,
        file_path,
        None
    )
    await update.message.reply_text("📷 Photo received. Analyzing...")

    try:
        print("Opening image...")

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        print("Image loaded")

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg",
        )

        print("Image converted")

        print("Sending to Gemini...")

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[image_part,"Please describe this image."
        ]
    )

        print("Gemini finished")

        await update.message.reply_text(response.text)

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text(
    "An unexpected error occurred while processing the image."
    )        

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    message_from = update.message.from_user.username

    file_id = update.message.voice.file_id
    voice_file = await context.bot.get_file(file_id)

    file_path = os.path.join(VOICE_DIR, f"{file_id}.ogg")
    await voice_file.download_to_drive(file_path)

    save_message(
        telegram_id,
        message_from,
        "voice",
        file_id,
        file_path,
        None
    )
    
    await update.message.reply_text("analyzing response...")
    
    try:
            print("analyzing voice_note...")
    
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
    
            print("Voice note loaded")
    
            voice_note = types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/ogg",
            )
    
            print("Voice note converted")
    
            print("Sending to Gemini...")
    
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                    contents=[
                    voice_note,
                        "Listen to this voice note and respond to what the user said."
            ]
            
        )
    
            print("Gemini finished")

            await update.message.reply_text(response.text)


    
    except Exception as e:
            print("ERROR:", e)

    
            await update.message.reply_text(
            "An unexpected error occurred while processing the voice message."
            ) 

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

create_table()
app.run_polling()
