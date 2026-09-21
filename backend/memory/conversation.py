import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# Store the database inside the backend directory.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "mantis.db"


def _get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_memory():
    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                extension TEXT NOT NULL,
                content TEXT NOT NULL,
                characters INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_message(
    role: str,
    content: str,
) -> dict:

    if role not in {
        "user",
        "assistant",
        "system",
    }:
        raise ValueError(
            "Invalid message role"
        )

    if not content or not content.strip():
        raise ValueError(
            "Message content cannot be empty"
        )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    connection = _get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO conversation_messages
            (role, content, timestamp)
            VALUES (?, ?, ?)
            """,
            (
                role,
                content.strip(),
                timestamp,
            ),
        )

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "role": role,
            "content": content.strip(),
            "timestamp": timestamp,
        }

    finally:
        connection.close()


def get_recent_messages(
    limit: int = 20,
) -> list[dict]:

    if limit <= 0:
        return []

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                role,
                content,
                timestamp
            FROM conversation_messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        messages = [
            dict(row)
            for row in rows
        ]

        # Return oldest → newest.
        messages.reverse()

        return messages

    finally:
        connection.close()


def clear_memory():
    connection = _get_connection()

    try:
        connection.execute(
            "DELETE FROM conversation_messages"
        )

        connection.commit()

    finally:
        connection.close()

def build_conversation_context(
    limit: int = 10,
) -> str:
    messages = get_recent_messages(limit)

    if not messages:
        return ""

    lines = []

    for message in messages:
        role = message["role"].upper()
        content = message["content"]

        lines.append(
            f"{role}: {content}"
        )

    return "\n".join(lines)
def save_document(
    path: str,
    filename: str,
    extension: str,
    content: str,
) -> dict:

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    connection = _get_connection()

    try:
        connection.execute(
            """
            INSERT INTO documents
            (
                path,
                filename,
                extension,
                content,
                characters,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(path)
            DO UPDATE SET
                filename = excluded.filename,
                extension = excluded.extension,
                content = excluded.content,
                characters = excluded.characters,
                timestamp = excluded.timestamp
            """,
            (
                path,
                filename,
                extension,
                content,
                len(content),
                timestamp,
            ),
        )

        connection.commit()

        return {
            "success": True,
            "path": path,
            "filename": filename,
            "extension": extension,
            "characters": len(content),
            "timestamp": timestamp,
        }

    finally:
        connection.close()


def get_documents() -> list[dict]:
    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                path,
                filename,
                extension,
                characters,
                timestamp
            FROM documents
            ORDER BY id
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()


def get_document(
    path: str,
) -> dict | None:

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                path,
                filename,
                extension,
                content,
                characters,
                timestamp
            FROM documents
            WHERE path = ?
            """,
            (path,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()