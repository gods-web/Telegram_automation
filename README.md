# Telegram Automation

This is a Python automation project that uses the Telegram Bot API to create an intelligent Telegram bot. The bot helps Telegram users perform various tasks directly within Telegram.

## First Step: Create a Telegram Bot

Before writing any code, the first thing you need to do is create a Telegram bot using **BotFather**.

### How to Create the Bot

1. Open the Telegram app and go to the **Search** bar.
2. Search for **@BotFather** and open the verified BotFather account.
3. Start a chat with BotFather. You will see a list of commands such as:

   * `/newbot`
   * `/mybots`
   * `/setname`
   * `/setdescription`
   * and many more.
4. Click or type the `/newbot` command to create a new bot.
5. BotFather will ask you to:

   * Enter a **name** for your bot.
   * Enter a unique **username** that ends with `bot` (for example, `MyAwesomeBot` or `my_awesome_bot`).
6. If both the name and username are available, BotFather will successfully create your bot and provide you with a **bot token**.

> **Important:** Keep your bot token private. Anyone with access to it can control your bot.

You can also watch this tutorial if you need help creating your bot:

* https://www.youtube.com/watch?v=vF7MaDR6zX4

After receiving your bot token, create a `.env` file in your project directory and save your token there.

Example:

```env
BOT_TOKEN=your_bot_token_here
```

---

## Second Step: Create the Project Files

Create the following files in your project directory:

```text
bot.py
database.py
requirements.txt
messages.db
```

These files will be used throughout the project:

* **bot.py** – Contains the main Telegram bot logic.
* **database.py** – Handles all database operations.
* **requirements.txt** – Lists the Python packages required for the project.
* **messages.db** – SQLite database used to store chat history and other bot data.

## Required import   
 Write the following modules befor writing the bot logic

   from telegram import ReplyKeyboardMarkup, Update   
   from telegram import Update
   from telegram.ext import (
      ApplicationBuilder,
      CommandHandler,
      ContextTypes,
      MessageHandler,
      filters,
   )
   from dotenv import load_dotenv
   from google.genai import types
   from database import create_table, save_message, get_chat_history
   from google.genai.errors import ServerError
   from google import genai
   import os
