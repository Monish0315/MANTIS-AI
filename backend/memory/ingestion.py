from pathlib import Path

from pypdf import PdfReader
from docx import Document

from memory.conversation import (
    save_document,
    get_document,
    save_document_chunks,
    get_document_chunks,
    save_chunk_embedding,
)
from memory.lancedb_store import add_chunk

from memory.embeddings import (
    generate_embedding,
    EMBEDDING_MODEL,
)


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".py",
    ".json",
    ".csv",
    ".pdf",
    ".docx",
}


def read_text_file(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def read_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def read_docx_file(path: Path) -> str:
    document = Document(str(path))

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def read_document(path: str) -> dict:
    document_path = Path(path).expanduser()

    if not document_path.exists():
        return {
            "success": False,
            "error": "File does not exist",
            "path": str(document_path),
            "text": "",
        }

    if not document_path.is_file():
        return {
            "success": False,
            "error": "Path is not a file",
            "text": "",
        }

    extension = document_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        return {
            "success": False,
            "error": (
                f"Unsupported file type: {extension}"
            ),
            "path": str(document_path),
            "text": "",
        }

    try:
        if extension == ".pdf":
            text = read_pdf_file(document_path)

        elif extension == ".docx":
            text = read_docx_file(document_path)

        else:
            text = read_text_file(document_path)

        return {
            "success": True,
            "error": None,
            "path": str(document_path),
            "text": text,
            "characters": len(text),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "path": str(document_path),
            "text": "",
        }


def ingest_document(path: str) -> dict:
    result = read_document(path)

    if not result["success"]:
        return result

    saved = save_document(
        path=result["path"],
        filename=Path(result["path"]).name,
        extension=Path(result["path"]).suffix.lower(),
        content=result["text"],
    )

    document = get_document(
        result["path"]
    )

    if document is None:
        return {
            **result,
            "stored": False,
            "error": "Document was not found after saving",
        }

    chunks = chunk_text(
        result["text"],
        chunk_size=1000,
        overlap=200,
    )

    chunk_records = []

    position = 0

    for index, chunk in enumerate(chunks):
        start_position = result["text"].find(
            chunk,
            position,
        )

        if start_position == -1:
            start_position = position

        end_position = (
            start_position + len(chunk)
        )

        chunk_records.append(
            {
                "chunk_index": index,
                "content": chunk,
                "start_position": start_position,
                "end_position": end_position,
            }
        )

        position = max(
            end_position - 200,
            position,
        )

    saved_chunks = save_document_chunks(
        document["id"],
        chunk_records,
    )
    stored_chunks = get_document_chunks(
        document["id"]
    )

    embedded_count = 0

    for chunk in stored_chunks:
        embedding = generate_embedding(
            chunk["content"]
        )

        save_chunk_embedding(
            chunk_id=chunk["id"],
            embedding=embedding,
            model=EMBEDDING_MODEL,
        )
        add_chunk(
            chunk_id=chunk["id"],
            document_id=document["id"],
            chunk_index=chunk["chunk_index"],
            filename=Path(result["path"]).name,
            path=str(path),
            content=chunk["content"],
            vector=embedding,
        )
        embedded_count += 1

    return {
        **result,
        "stored": saved["success"],
        "document_id": document["id"],
        "chunk_count": saved_chunks,
        "embedded_count": embedded_count,
    }
def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = text.strip()

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks