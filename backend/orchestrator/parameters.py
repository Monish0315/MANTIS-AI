from pathlib import Path


def extract_file_search_params(message: str) -> dict:
    text = message.lower()

    extension = ".txt"

    if "pdf" in text:
        extension = ".pdf"
    elif "excel" in text or "xlsx" in text:
        extension = ".xlsx"
    elif "word" in text or "docx" in text:
        extension = ".docx"
    elif "python" in text or ".py" in text:
        extension = ".py"

    home = Path.home()

    folder = None

    if "mantis" in text:
        folder = home / "OneDrive" / "Documents" / "AI Bot" / "MANTIS"
    elif "documents" in text:
        folder = home / "Documents"
    elif "downloads" in text:
        folder = home / "Downloads"
    elif "desktop" in text:
        folder = home / "Desktop"

    return {
        "folder": str(folder) if folder else None,
        "extension": extension,
    }