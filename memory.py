import sqlite3
import json

DB_NAME = "conversation.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT,
            tool_call_id TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(role, content, tool_call_id=None):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (role, content, tool_call_id)
        VALUES (?, ?, ?)
        """,
        (role, content, tool_call_id)
    )

    conn.commit()
    conn.close()


def load_messages():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, tool_call_id
        FROM messages
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    messages = []

    for role, content, tool_call_id in rows:

        message = {
            "role": role,
            "content": content
        }

        if tool_call_id:
            message["tool_call_id"] = tool_call_id

        messages.append(message)

    return messages