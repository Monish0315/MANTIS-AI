import re
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

    windows_path = re.search(
        r"[a-zA-Z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*",
        message,
    )

    if windows_path:
        folder = windows_path.group(0)

        return {
            "folder": folder,
            "extension": extension,
        }

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


def extract_windows_action_params(message: str) -> dict:
    text = message.lower()

    windows_path = re.search(
        r"[a-zA-Z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*",
        message,
    )

    if windows_path:
        return {
            "action": "open_folder",
            "folder": windows_path.group(0),
        }

    home = Path.home()

    if "downloads" in text:
        return {
            "action": "open_folder",
            "folder": str(home / "Downloads"),
        }

    if "documents" in text:
        return {
            "action": "open_folder",
            "folder": str(home / "Documents"),
        }

    if "desktop" in text:
        return {
            "action": "open_folder",
            "folder": str(home / "Desktop"),
        }

    if "mantis" in text:
        return {
            "action": "open_folder",
            "folder": str(
                home / "OneDrive" / "Documents" / "AI Bot" / "MANTIS"
            ),
        }

    return {
        "action": None,
        "folder": None,
    }