from pathlib import Path

from pypdf import PdfReader
from docx import Document
from memory.conversation import save_document

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
            "path": str(document_path),
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

    return {
        **result,
        "stored": saved["success"],
    }