import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="nexi_bot",
        user="postgres",
        password="7900"
    )

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            message_from VARCHAR(20),
            message_type VARCHAR(50),
            file_id TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def save_message(
    telegram_id,
    message_from,
    message_type="text",
    file_id=None,
    file_path=None,
    message=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages
        (telegram_id, message_from, message_type, file_id, file_path, message)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        telegram_id,
        message_from,
        message_type,
        file_id,
        file_path,
        message
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_chat_history(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message_from, message
        FROM messages
        WHERE telegram_id = %s
        ORDER BY created_at DESC
        LIMIT 10
    """, (telegram_id,))

    chat_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return chat_history[::-1]

def save_feedback(telegram_id, rating, comment=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback
        (telegram_id, rating, comment)
        VALUES (%s, %s, %s)
    """, (
        telegram_id,
        rating,
        comment
    ))

    conn.commit()
    cursor.close()
    conn.close()

def admin_get_feedback():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id, rating, comment, created_at
        FROM feedback
        ORDER BY created_at DESC
    """)

    feedback_messages = cursor.fetchall()

    cursor.close()
    conn.close()

    return feedback_messages

if __name__ == "__main__":
    save_feedback(
        telegram_id=8012739322,
        rating="👍 Good",
        comment="PostgreSQL feedback test"
    )

    print("Feedback saved successfully!")