from pathlib import Path


def search_files(folder: str, extension: str) -> list[str]:
    root = Path(folder).expanduser()

    if not root.exists():
        return []

    return [
        str(path)
        for path in root.rglob(f"*{extension}")
        if path.is_file()
    ]