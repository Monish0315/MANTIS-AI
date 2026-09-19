from pathlib import Path


def search_files(folder: str, extension: str) -> dict:
    if not folder:
        return {
            "success": False,
            "error": "No folder was specified",
            "files": [],
        }

    if not extension:
        return {
            "success": False,
            "error": "No file extension was specified",
            "files": [],
        }

    root = Path(folder).expanduser()

    if not root.exists():
        return {
            "success": False,
            "error": "Folder does not exist",
            "files": [],
        }

    if not root.is_dir():
        return {
            "success": False,
            "error": "Path is not a folder",
            "files": [],
        }

    if not extension.startswith("."):
        extension = f".{extension}"

    files = [
        str(path)
        for path in root.rglob(f"*{extension}")
        if path.is_file()
    ]

    return {
        "success": True,
        "error": None,
        "files": files,
    }