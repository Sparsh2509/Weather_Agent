import sqlite3

DB_NAME = "conversation.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_message(role, content):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (role, content)
        VALUES (?, ?)
    """, (role, content))

    conn.commit()
    conn.close()


def load_messages():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    messages = []

    for role, content in rows:
        messages.append({
            "role": role,
            "content": content
        })

    return messages

def save_summary(summary):
    conn = sqlite3.connect("conversation.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_summary (
            id INTEGER PRIMARY KEY,
            summary TEXT
        )
    """)

    cursor.execute("""
        INSERT OR REPLACE INTO memory_summary (id, summary)
        VALUES (1, ?)
    """, (summary,))

    conn.commit()
    conn.close()


def load_summary():
    conn = sqlite3.connect("conversation.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_summary (
            id INTEGER PRIMARY KEY,
            summary TEXT
        )
    """)

    cursor.execute("""
        SELECT summary
        FROM memory_summary
        WHERE id = 1
    """)

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return ""