from pathlib import Path

import lancedb

from memory.embeddings import generate_embedding
from memory.conversation import get_all_chunk_embeddings


LANCEDB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "lancedb"
)


def get_database():
    return lancedb.connect(str(LANCEDB_PATH))


def get_table():
    db = get_database()
    try:
        return db.open_table("document_chunks")
    except Exception as e:
        raise RuntimeError("LanceDB document_chunks table does not exist.") from e


def rebuild_vector_table():
    """
    Rebuild the LanceDB vector table from the
    embeddings currently stored in SQLite.
    """

    db = get_database()

    stored_chunks = get_all_chunk_embeddings()

    if not stored_chunks:
        raise RuntimeError(
            "No stored chunk embeddings were found in SQLite."
        )

    data = [
        {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "chunk_index": chunk["chunk_index"],
            "filename": chunk["filename"],
            "path": chunk["path"],
            "content": chunk["content"],
            "vector": chunk["embedding"],
        }
        for chunk in stored_chunks
    ]

    # mode="overwrite" drops/replaces the existing table cleanly
    table = db.create_table(
        "document_chunks",
        data=data,
        mode="overwrite",
    )

    return table

def search_vectors(
    query: str,
    top_k: int = 5,
) -> list[dict]:

    if not query or not query.strip():
        return []

    if top_k <= 0:
        return []

    query_embedding = generate_embedding(query)

    table = get_table()

    results = (
        table.search(query_embedding)
        .limit(top_k)
        .to_list()
    )

    return results

def add_chunk(
    chunk_id: int,
    document_id: int,
    chunk_index: int,
    filename: str,
    path: str,
    content: str,
    vector: list[float],
):
    db = get_database()

    data = [
        {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_index": chunk_index,
            "filename": filename,
            "path": path,
            "content": content,
            "vector": vector,
        }
    ]

    try:
        table = db.open_table("document_chunks")
    except Exception:
        db.create_table(
            "document_chunks",
            data=data,
        )
        return

    # Remove any previous version of this logical chunk.
    #
    # chunk_id can change when a document is re-ingested,
    # so use document_id + chunk_index instead.
    table.delete(
        f"document_id = {document_id} AND "
        f"chunk_index = {chunk_index}"
    )

    # Insert the latest version.
    table.add(data)


if __name__ == "__main__":
    table = rebuild_vector_table()

    print("LanceDB vector table rebuilt successfully.")
    print("Rows:", table.count_rows())

    results = search_vectors(
        "What is MANTIS?",
        5,
    )

    print("\nSearch results:\n")

    for result in results:
        print(
            result.get("_distance"),
            "|",
            result["filename"],
            "|",
            result["content"][:150],
        )