import re


def detect_intent(message: str) -> str:
    text = message.lower().strip()

    # ---------------------------------
    # Explicit URL opening
    # ---------------------------------

    if re.search(
        r"\b(open|launch|start)\b.*https?://",
        text,
    ):
        return "WINDOWS_ACTION"

    # ---------------------------------
    # Local file search
    # ---------------------------------

    if re.search(
        r"\b(find|search|locate|list)\b.*\b(files?|documents?|pdfs?|folders?)\b",
        text,
    ):
        return "LOCAL_FILE_SEARCH"

    # ---------------------------------
    # Web search
    # ---------------------------------

    if re.search(
        r"\b(search the web|web search|look online|search online)\b",
        text,
    ):
        return "WEB_SEARCH"

    # "Search Google for..."
    if re.search(
        r"\b(search|google)\b.*\b(for|about)\b",
        text,
    ):
        return "WEB_SEARCH"

    # ---------------------------------
    # Windows actions
    # ---------------------------------

    if re.search(
        r"\b(open|close|launch|start|run|shutdown|restart)\b",
        text,
    ):
        return "WINDOWS_ACTION"

    return "GENERAL_QUESTION"