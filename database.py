import os
import sqlite3

DB_PATH = "data/groups.db"

# Papkani yaratish
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_groups_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY,
            lang TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def set_group_language(chat_id: int, lang: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO groups (chat_id, lang)
        VALUES (?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET lang=excluded.lang
    """, (chat_id, lang))
    conn.commit()
    conn.close()


def get_group_language(chat_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT lang FROM groups WHERE chat_id = ?", (chat_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else "uz"


def init_db():
    return None