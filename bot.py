from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from google.genai import types
from telegram.ext import MessageHandler, filters
from database import admin_get_feedback, create_table, save_message, save_feedback,save_user,get_user,get_today_photo_count
from database import get_chat_history
from google.genai.errors import ServerError
from google import genai
import os
import asyncio
from tts import generate_audio
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from http import HTTPStatus


load_dotenv()
@asynccontextmanager
async def lifespan(app_lifespan: FastAPI):
    await app.initialize()

    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/webhook",
        allowed_updates=Update.ALL_TYPES
    )

    await app.start()

    yield

    await app.stop()
    await app.shutdown()


web_app = FastAPI(lifespan=lifespan)


@web_app.get("/")
async def health_check():
    return {"status": "Nexi AI is running"}


@web_app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)

    print(data)

    return Response(status_code=HTTPStatus.OK)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

client = genai.Client(api_key=GEMINI_API_KEY)

PHOTO_DIR = "downloads/photos"
VOICE_DIR = "downloads/voice"
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

# Admin feedback command to view all feedback messages from users. Only accessible by the admin with the specified ADMIN_ID.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    # Save user information to the database
    save_user(telegram_id, first_name, username)

    welcome_text = (
    f"Hello {first_name}! 👋 I'm Nexi AI, your intelligent virtual assistant.\n"
    "It's lovely to meet you! I'm here to help you find information, "
    "answer your questions, and make your tasks a little easier.\n"
    "So, what would you like us to work on today? 🤖✨"
)
    await update.message.reply_text(welcome_text, 
                                reply_markup=main_keyboard
                                )

    await generate_audio(welcome_text)

    await update.message.reply_voice(voice=open("output.mp3", "rb")
                                     )
    
                                
async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if telegram_id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ You are not authorized to view feedback."
        )
        return

    feedback_messages = admin_get_feedback()

    if not feedback_messages:
        await update.message.reply_text(
            "📭 No feedback has been received yet."
        )
        return

    response = "📊 Nexi AI Feedback\n\n"

    for user_id, rating, comment, created_at in feedback_messages:
        response += (
            f"👤 User: {user_id}\n"
            f"⭐ Rating: {rating}\n"
            f"💬 Comment: {comment}\n"
            f"🕒 Date: {created_at}\n"
            f"--------------------\n"
        )

    await update.message.reply_text(response)

    feedback_messages = admin_get_feedback()

    if not feedback_messages:
        await update.message.reply_text(
            "📭 No feedback has been received yet."
        )
        return

    response = "📊 Nexi AI Feedback\n\n"

    for telegram_id, rating, comment, created_at in feedback_messages:
        response += (
            f"👤 User: {telegram_id}\n"
            f"⭐ Rating: {rating}\n"
            f"💬 Comment: {comment}\n"
            f"🕒 Date: {created_at}\n"
            f"--------------------\n"
        )

    await update.message.reply_text(response)

# Handler for the /feedback command to allow the admin to view feedback messages.
# and inline keyboard for feedback, about, help, and menu options.

app = ApplicationBuilder().token(BOT_TOKEN).updater(None).build()

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

    # Save feedback comment to PostgreSQL
    if context.user_data.get("feedback_rating"):
        rating = context.user_data["feedback_rating"]

        save_feedback(
            telegram_id=telegram_id,
            rating=rating,
            comment=user_message
        )

        context.user_data.pop("feedback_rating", None)
        context.user_data.pop("awaiting_feedback", None)

        await update.message.reply_text(
            "Thank you! ❤️ Your feedback has been saved successfully."
        )
        return

    # Feedback button
    if user_message == "💬 Feedback":
        context.user_data["awaiting_feedback"] = True

        await update.message.reply_text(
            "Thank you for your feedback! ❤️\n"
            "Please rate our service:\n"
            "👍 Good\n"
            "👎 Bad"
        )
        return

    # Good feedback
    if user_message == "👍 Good":
        context.user_data["feedback_rating"] = 1
        context.user_data["awaiting_feedback"] = True

        await update.message.reply_text(
            "Thank you for your positive feedback! We appreciate it.\n"
            "What do you like about our service?"
        )
        return

    # Bad feedback
    if user_message == "👎 Bad":
        context.user_data["feedback_rating"] = 0
        context.user_data["awaiting_feedback"] = True

        await update.message.reply_text(
            "Thank you for your feedback! We will work to improve our service.\n"
            "Please, what is the issue you are facing?"
        )
        return

    # About
    if user_message == "ℹ️ About":
        await update.message.reply_text(
            "Nexi AI is a virtual assistant designed to help you "
            "with various tasks and provide information."
        )
        return

    # Help
    if user_message == "🆘 Help":
        await update.message.reply_text(
            """🆘 Need some help?
            "I'm Nexi AI, and I'm here to assist you."

            You can:
            • 💬 Ask me questions or start a conversation
            • 📚 Ask me to explain a topic
            • 💡 Ask for ideas or suggestions
            • 🔎 Ask me to help you find information
            • 📝 Ask me to write, rewrite, or improve text

            Just type your request in the chat and I'll do my best to help.

            If you're not sure what to ask, simply say:
            "Hello Nexi, what can you help me with?"""
            
        )
        return

    # Menu
    if user_message == "⚙️ Menu":
        await update.message.reply_text(
            "Here are some options:\n\n"
            "💬 Feedback: Provide feedback\n"
            "ℹ️ About: Learn about Nexi AI\n"
            "🆘 Help: Get assistance\n"
            "⚙️ Menu: View menu options"
        )
        return

    # Save normal user message to PostgreSQL
    save_message(
        telegram_id,
        message_from,
        "text",
        None,
        None,
        user_message
    )

    # Get conversation history
    chat_history = get_chat_history(telegram_id)

    conversation = ""

    for sender, message in chat_history:
        conversation += f"{sender}: {message}\n"

    print("===== CONVERSATION =====")
    print(conversation)
    print("========================")

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=conversation
        )
        bot_response = response.text

        if "your name" in user_message.lower() or "who are you" in user_message.lower():
            bot_response = (
                "I'm Nexi AI! 🤖 I'm your virtual assistant, here to answer "
                "your questions, explain things, help with tasks, share ideas, "
                "and have useful conversations with you."
            )

        elif "hey nexi" in user_message.lower():
            bot_response = "Hey! 👋 What's up? What can I help you with today?"

       # Respond when a user asks who created Nexi AI
        elif "who created you" in user_message.lower() or "who made you" in user_message.lower():
            bot_response = (
                "I was created by Godswill, a developer and AI enthusiast. "
                "I was designed to be your helpful virtual assistant!"
            )
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

#This is the for photo handler that receives a photo from the user, saves it, and sends it to Nexi AI for analysis. The response from Nexi AI is then sent back to the user.


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    message_from = update.message.from_user.username

    if telegram_id != int(os.getenv("ADMIN_ID")):
        photo_count = get_today_photo_count(telegram_id)
        if photo_count >= 3:
            await update.message.reply_text(
                "You have reached the daily limit of 3 photos. "
                "Please try again tomorrow."
            )
            return

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
    await asyncio.sleep(3)
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

#This is the for voice handler that receives a voice message from the user, saves it, and sends it to Nexi AI for analysis. The response from Nexi AI is then sent back to the user. 

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
    await asyncio.sleep(1)
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


    except ServerError:
            await update.message.reply_text(
                "Nexi server is busy at the moment. Please try again in a few seconds."
            )
    except Exception as e:
            print("ERROR:", e)

    
            await update.message.reply_text(
            "An unexpected error occurred while processing the voice message."
            )

#This is the main part of the bot that sets up the command handlers and message handlers for the bot. It includes handlers for the /start command, /feedback command, text messages, photo messages, and voice messages.

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("feedback", feedback_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))


create_table()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
