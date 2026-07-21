import sqlite3

def create_table():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       telegram_id INTEGER,
                       message TEXT)''')
    conn.commit()
    conn.close()



def save_message( telegram_id, user_message):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO messages (telegram_id, message) VALUES (?, ?)', (telegram_id, user_message))
    conn.commit()
    conn.close()




