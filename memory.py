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
            tool_call_id TEXT,
            tool_calls TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(
    role,
    content=None,
    tool_call_id=None,
    tool_calls=None
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if tool_calls:
        tool_calls = json.dumps(tool_calls)

    cursor.execute("""
        INSERT INTO messages
        (role, content, tool_call_id, tool_calls)
        VALUES (?, ?, ?, ?)
    """, (
        role,
        content,
        tool_call_id,
        tool_calls
    ))

    conn.commit()
    conn.close()


def load_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, tool_call_id, tool_calls
        FROM messages
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()

    messages = []

    for role, content, tool_call_id, tool_calls in rows:

        message = {
            "role": role,
            "content": content
        }

        if tool_call_id:
            message["tool_call_id"] = tool_call_id

        if tool_calls:
            message["tool_calls"] = json.loads(tool_calls)

        messages.append(message)

    return messages