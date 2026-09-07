from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from google.genai import types
from telegram.ext import MessageHandler, filters
from database import create_table, save_message
from database import get_chat_history
from google.genai.errors import ServerError
from google import genai
import os
import time


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

PHOTO_DIR = "downloads/photos"
VOICE_DIR = "downloads/voice"
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am Nexi AI \n How can I assist you today?",
                                    reply_markup=main_keyboard
                                    )

app = ApplicationBuilder().token(BOT_TOKEN).build()

main_keyboard = ReplyKeyboardMarkup(
    [
        ["💬 Feedback", "ℹ️ About"],
        ["🆘 Help", "⚙️ Menu"]
    ],
    resize_keyboard=True,

) 

print("Bot started successfully!")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    message_from = "user"
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


    conversation = ""

    for sender, message in chat_history:
        conversation += f"{sender}: {message}\n"

    print("===== CONVERSATION =====")
    print(conversation)
    print("========================")

    if user_message == "💬 Feedback":
            context.user_data["awaiting_feedback"] = True
            await update.message.reply_text(
                "Thank you for your feedback! Please how can you rate our service?\n👍 Good\n👎 Bad\n please use any of those emojis to express your opinion."
            )
            return
    if user_message == "👍 Good":
        context.user_data["feedback_rating"] = "👍 Good"
        await update.message.reply_text(
            "Thank you for your positive feedback! We appreciate it."
        )
        await update.message.reply_text("what do you like about our service?")

        return
    
    if user_message == "👎 Bad":
        context.user_data["feedback_rating"] = "👎 Bad"
        await update.message.reply_text(
            "Thank you for your feedback! We will work to improve our service."
        ) 
        await update.message.reply_text(
            "Please what is the issue you are facing?"
        )
        return

    if user_message == "ℹ️ About":
        await update.message.reply_text(
            "Nexi AI is a virtual assistant designed to help you with various tasks and provide information. It can answer questions, provide recommendations, and assist with a wide range of topics. How can I assist you today?"
        )
        return

    if user_message == "🆘 Help":
        await update.message.reply_text(
            "I'm here to help! You can ask me questions, request information, or provide feedback. How can I assist you today?"
        )
        return

    if user_message == "⚙️ Menu":
        await update.message.reply_text(
            "Here are some options you can choose from:\n\n💬 Feedback: Provide feedback on our service.\nℹ️ About: Learn more about Nexi AI.\n🆘 Help: Get assistance and support.\n⚙️ Menu: View the main menu options."
        )
        return
    
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=conversation
        )

        if "your name" in user_message.lower():
            await update.message.reply_text(
            "My name is Nexi AI ! 🤖 I am a virtual assistant designed to help you with various tasks and provide information. How can I assist you today?"
        )
            return

        bot_response = response.text

        await update.message.reply_text(bot_response)
        
        save_message(
            telegram_id,
            "assistant",
            "text",
            None,
            None,
            bot_response
        )

    except ServerError:
        await update.message.reply_text(
            "Nexi server is busy at the moment. Please try again in a few seconds."
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

    status_message = await update.message.reply_text("📷 Photo received. Analyzing...")
    time.sleep(3)
    await status_message.delete()

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

        print("Sending to Nexi...")

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[image_part,"Please describe this image."
        ]
    )

        print("Nexi AI finished")

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
    
    status_message = await update.message.reply_text("Nexi, analyzing response...")
    time.sleep(1)
    await status_message.delete()
    
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
    
            print("Sending to Nexi...")
    
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                    contents=[
                    voice_note,
                        "Listen to this voice note and respond to what the user said."
            ]
            
        )
    
            print("Nexi finished")

            await update.message.reply_text(response.text)

    except Exception as e:
            print("ERROR:", e)

    
            await update.message.reply_text(
            "An unexpected error occurred while processing the voice message."
            ) 

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

create_table()
app.run_polling()
