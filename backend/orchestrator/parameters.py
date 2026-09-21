import re
from pathlib import Path


WINDOWS_PATH_PATTERN = (
    r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*'
    r'[^\\/:*?"<>|\r\n]*'
)


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
        WINDOWS_PATH_PATTERN,
        message,
    )

    if windows_path:
        return {
            "folder": windows_path.group(0),
            "extension": extension,
        }

    home = Path.home()

    folder = None

    if "mantis" in text:
        folder = (
            home
            / "OneDrive"
            / "Documents"
            / "AI Bot"
            / "MANTIS"
        )
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
    text = message.lower().strip()

    # ---------------------------------
    # High-risk actions
    # ---------------------------------

    if "shutdown" in text:
        return {
            "action": "shutdown",
            "folder": None,
        }

    if "restart" in text:
        return {
            "action": "restart",
            "folder": None,
        }

    # ---------------------------------
    # URLs
    # ---------------------------------

    url_match = re.search(
        r"https?://[^\s]+",
        message,
        re.IGNORECASE,
    )

    if url_match:
        return {
            "action": "open_url",
            "url": url_match.group(0),
        }

    # ---------------------------------
    # Windows file/folder paths
    # ---------------------------------

    windows_path = re.search(
        WINDOWS_PATH_PATTERN,
        message,
    )

    if windows_path:
        path = windows_path.group(0)

        if Path(path).is_file():
            return {
                "action": "open_file",
                "file": path,
            }

        return {
            "action": "open_folder",
            "folder": path,
        }

    # ---------------------------------
    # Common Windows folders
    # ---------------------------------

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
                home
                / "OneDrive"
                / "Documents"
                / "AI Bot"
                / "MANTIS"
            ),
        }

    # ---------------------------------
    # Allowlisted applications
    # ---------------------------------

    applications = {
        "notepad": "notepad",
        "calculator": "calculator",
        "calc": "calculator",
        "paint": "paint",
        "mspaint": "paint",
    }

    for name, application in applications.items():
        if re.search(
            rf"\b{re.escape(name)}\b",
            text,
        ):
            if re.search(
                r"\b(launch|open|start|run)\b",
                text,
            ):
                return {
                    "action": "launch_application",
                    "application": application,
                }

    return {
        "action": None,
        "folder": None,
    }