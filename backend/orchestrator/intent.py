import re


def detect_intent(message: str) -> str:
    text = message.lower().strip()

    # Local file search
    if re.search(
        r"\b(find|search|locate|list)\b.*\b(files?|documents?|pdfs?|folders?)\b",
        text,
    ):
        return "LOCAL_FILE_SEARCH"

    # Web search
    if re.search(
        r"\b(search the web|web search|google|look online|search online)\b",
        text,
    ):
        return "WEB_SEARCH"

    # Windows actions
    if re.search(
        r"\b(open|close|launch|start|run|shutdown|restart)\b",
        text,
    ):
        return "WINDOWS_ACTION"

    # Default
    return "GENERAL_QUESTION"