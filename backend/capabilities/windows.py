import os
import subprocess
import time
import webbrowser
from pathlib import Path


def open_folder(folder: str) -> dict:
    if not folder:
        return {
            "success": False,
            "verified": False,
            "error": "No folder was specified",
        }

    if not os.path.isdir(folder):
        return {
            "success": False,
            "verified": False,
            "error": "Folder does not exist",
        }

    try:
        os.startfile(folder)

        return {
            "success": True,
            "verified": True,
            "error": None,
            "folder": folder,
        }

    except Exception as exc:
        return {
            "success": False,
            "verified": False,
            "error": str(exc),
        }


def open_file(file_path: str) -> dict:
    if not file_path:
        return {
            "success": False,
            "verified": False,
            "error": "No file was specified",
        }

    path = Path(file_path).expanduser()

    if not path.exists():
        return {
            "success": False,
            "verified": False,
            "error": "File does not exist",
        }

    if not path.is_file():
        return {
            "success": False,
            "verified": False,
            "error": "Path is not a file",
        }

    try:
        os.startfile(str(path))

        return {
            "success": True,
            "verified": True,
            "error": None,
            "file": str(path),
        }

    except Exception as exc:
        return {
            "success": False,
            "verified": False,
            "error": str(exc),
        }


def open_url(url: str) -> dict:
    if not url:
        return {
            "success": False,
            "verified": False,
            "error": "No URL was specified",
        }

    if not url.startswith(("http://", "https://")):
        return {
            "success": False,
            "verified": False,
            "error": "Only HTTP and HTTPS URLs are allowed",
        }

    try:
        opened = webbrowser.open(url)

        if not opened:
            return {
                "success": False,
                "verified": False,
                "error": "Could not open the URL",
            }

        return {
            "success": True,
            "verified": True,
            "error": None,
            "url": url,
        }

    except Exception as exc:
        return {
            "success": False,
            "verified": False,
            "error": str(exc),
        }


def launch_application(application: str) -> dict:
    if not application:
        return {
            "success": False,
            "verified": False,
            "error": "No application was specified",
        }

    allowed_applications = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
    }

    executable = allowed_applications.get(
        application.lower()
    )

    if not executable:
        return {
            "success": False,
            "verified": False,
            "error": "Application is not in the allowed application list",
        }

    try:
        process = subprocess.Popen(
            [executable]
        )

        # Verify that Windows created the process.
        time.sleep(0.3)

        if process.poll() is not None:
            return {
                "success": False,
                "verified": False,
                "error": (
                    f"{application} exited immediately "
                    "after launch"
                ),
            }

        return {
            "success": True,
            "verified": True,
            "error": None,
            "application": application.lower(),
            "pid": process.pid,
        }

    except Exception as exc:
        return {
            "success": False,
            "verified": False,
            "error": str(exc),
        }