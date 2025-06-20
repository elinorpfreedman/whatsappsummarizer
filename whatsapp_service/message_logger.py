import sqlite3
from datetime import datetime

DB_PATH = "messages.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender TEXT,
            chat_name TEXT,
            content TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_message(message_id, sender, chat_name, content, timestamp=None):
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO messages (id, sender, chat_name, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_id, sender, chat_name, content, timestamp))
        conn.commit()
    except sqlite3.IntegrityError:
        # Ignore duplicate message
        pass
    finally:
        conn.close()
