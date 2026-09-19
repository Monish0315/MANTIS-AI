def format_file_search_result(result: dict) -> str:
    if not result:
        return "No execution result was produced."

    if not result["success"]:
        return f"File search failed: {result['error']}"

    files = result["files"]

    if not files:
        return "No matching files were found."

    if len(files) == 1:
        return f"Found 1 matching file:\n{files[0]}"

    lines = [f"Found {len(files)} matching files:"]

    for file in files:
        lines.append(file)

    return "\n".join(lines)