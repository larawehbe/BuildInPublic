# db.py
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path("chat.db")


def get_connection():
    """Return a SQLite connection."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    """Create the users table if it does not exist."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES users(session_id)
            );
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                session_id TEXT NOT NULL,
                plan_type TEXT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
                FOREIGN KEY (session_id) REFERENCES users(session_id),
                FOREIGN KEY (username) REFERENCES users(username)
            );
            CREATE TABLE IF NOT EXISTS user_preferences (
                username TEXT PRIMARY KEY,
                preferences_json TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            );
            """)
        conn.commit()


# CRUD helpers
def create_user(username: str, session_id: str):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, session_id) VALUES (?, ?)",
            (username, session_id))
        conn.commit()


def get_user(username: str):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, session_id FROM users WHERE username = ?",
            (username, ))
        return cursor.fetchone()


def update_session_id(username: str, session_id: str):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET session_id = ? WHERE username = ?",
                       (session_id, username))
        conn.commit()
