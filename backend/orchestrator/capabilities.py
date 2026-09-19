def select_capability(intent: str) -> str:
    capabilities = {
        "LOCAL_FILE_SEARCH": "file_search",
        "WEB_SEARCH": "web_search",
        "WINDOWS_ACTION": "windows",
        "GENERAL_QUESTION": "llm",
    }

    return capabilities.get(intent, "llm")