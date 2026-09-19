def create_plan(intent: str, message: str) -> list[str]:
    if intent == "LOCAL_FILE_SEARCH":
        return [
            "Identify the target folder",
            "Search for matching files",
            "Return the matching files",
        ]

    if intent == "WEB_SEARCH":
        return [
            "Create a web search query",
            "Search the web",
            "Return relevant results",
        ]

    if intent == "WINDOWS_ACTION":
        return [
            "Identify the requested Windows action",
            "Check whether confirmation is required",
            "Execute the action",
        ]

    return [
        "Understand the user's question",
        "Generate an answer",
    ]