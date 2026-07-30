import sqlite3

def create_table():
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            message_from TEXT,
            message_type TEXT,
            file_id TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(
    telegram_id="telegram_id",
    message_from="message_from",
    message_type="text",
    file_id=None,
    file_path=None,
    message="user_message"
):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO messages (telegram_id,message_from, message_type, file_id, file_path, message) VALUES (?, ?, ?, ?, ?, ?)', (telegram_id,message_from, message_type, file_id, file_path, message))
    conn.commit()
    conn.close()

def get_chat_history(telegram_id):
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 10", (telegram_id,))
    chat_history = cursor.fetchall()
    conn.close()

    return chat_history