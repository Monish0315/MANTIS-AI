import json
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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                start_position INTEGER NOT NULL,
                end_position INTEGER NOT NULL,
                FOREIGN KEY(document_id)
                    REFERENCES documents(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunk_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id INTEGER NOT NULL UNIQUE,
                embedding TEXT NOT NULL,
                dimensions INTEGER NOT NULL,
                model TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(chunk_id)
                    REFERENCES document_chunks(id)
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
    conn = _get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE path = ?
        """,
        (path,),
    )

    existing = cursor.fetchone()

    if existing:
        document_id = existing["id"]

        cursor.execute(
            """
            UPDATE documents
            SET filename = ?,
                extension = ?,
                content = ?
            WHERE id = ?
            """,
            (
                filename,
                extension,
                content,
                document_id,
            ),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "document_id": document_id,
            "updated": True,
        }

    cursor.execute(
        """
        INSERT INTO documents (
            path,
            filename,
            extension,
            content
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            path,
            filename,
            extension,
            content,
        ),
    )

    document_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "document_id": document_id,
        "updated": False,
    } 


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

def save_document_chunks(
    document_id: int,
    chunks: list[dict],
) -> int:
    conn = _get_connection()

    cursor = conn.cursor()

    # Remove old chunks for this document.
    cursor.execute(
        """
        DELETE FROM document_chunks
        WHERE document_id = ?
        """,
        (document_id,),
    )

    saved_count = 0

    for chunk in chunks:
        cursor.execute(
            """
            INSERT INTO document_chunks (
                document_id,
                chunk_index,
                content,
                start_position,
                end_position
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                document_id,
                chunk["chunk_index"],
                chunk["content"],
                chunk["start_position"],
                chunk["end_position"],
            ),
        )

        saved_count += 1

    conn.commit()
    conn.close()

    return saved_count       


def get_document_chunks(
    document_id: int,
) -> list[dict]:

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                content,
                start_position,
                end_position
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index
            """,
            (document_id,),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()

def save_chunk_embedding(
    chunk_id: int,
    embedding: list[float],
    model: str,
) -> dict:

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    connection = _get_connection()

    try:
        connection.execute(
            """
            INSERT INTO chunk_embeddings
            (
                chunk_id,
                embedding,
                dimensions,
                model,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chunk_id)
            DO UPDATE SET
                embedding = excluded.embedding,
                dimensions = excluded.dimensions,
                model = excluded.model,
                timestamp = excluded.timestamp
            """,
            (
                chunk_id,
                json.dumps(embedding),
                len(embedding),
                model,
                timestamp,
            ),
        )

        connection.commit()

        return {
            "success": True,
            "chunk_id": chunk_id,
            "dimensions": len(embedding),
            "model": model,
        }

    finally:
        connection.close()


def get_chunk_embedding(
    chunk_id: int,
) -> dict | None:

    connection = _get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                chunk_id,
                embedding,
                dimensions,
                model,
                timestamp
            FROM chunk_embeddings
            WHERE chunk_id = ?
            """,
            (chunk_id,),
        ).fetchone()

        if row is None:
            return None

        result = dict(row)

        result["embedding"] = json.loads(
            result["embedding"]
        )

        return result

    finally:
        connection.close()

def get_all_chunk_embeddings() -> list[dict]:
    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                ce.chunk_id,
                ce.embedding,
                ce.dimensions,
                ce.model,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                d.path,
                d.filename
            FROM chunk_embeddings ce
            JOIN document_chunks dc
                ON ce.chunk_id = dc.id
            JOIN documents d
                ON dc.document_id = d.id
            ORDER BY ce.chunk_id
            """
        ).fetchall()

        results = []

        for row in rows:
            item = dict(row)

            item["embedding"] = json.loads(
                item["embedding"]
            )

            results.append(item)

        return results

    finally:
        connection.close()