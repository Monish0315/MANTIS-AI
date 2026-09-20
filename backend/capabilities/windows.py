import os


def open_folder(folder: str) -> dict:
    if not folder:
        return {
            "success": False,
            "error": "No folder was specified",
        }

    if not os.path.isdir(folder):
        return {
            "success": False,
            "error": "Folder does not exist",
        }

    try:
        os.startfile(folder)

        return {
            "success": True,
            "error": None,
            "folder": folder,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }