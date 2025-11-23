import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

def register_user(username, password_hash):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def verify_user(username, password_hash):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password_hash))
        return cur.fetchone() is not None
