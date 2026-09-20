from orchestrator.intent import detect_intent
from orchestrator.planner import create_plan
from orchestrator.capabilities import select_capability
from orchestrator.validator import validate_plan
from orchestrator.parameters import (
    extract_file_search_params,
    extract_windows_action_params,
)
from capabilities.file_search import search_files
from capabilities.windows import open_folder
from orchestrator.formatter import format_file_search_result


def orchestrate(message: str) -> dict:
    intent = detect_intent(message)
    plan = create_plan(intent, message)
    capability = select_capability(intent)

    valid = validate_plan(intent, plan, capability)

    result = None
    parameters = None
    response = None

    if valid and capability == "file_search":
        parameters = extract_file_search_params(message)

        if parameters["folder"]:
            result = search_files(
                parameters["folder"],
                parameters["extension"],
            )

            response = format_file_search_result(result)
        else:
            response = "I couldn't identify the folder you want me to search."

    elif valid and capability == "windows":
        parameters = extract_windows_action_params(message)

        if parameters["action"] == "open_folder":
            result = open_folder(parameters["folder"])

            if result["success"]:
                response = f"Opened folder:\n{result['folder']}"
            else:
                response = f"Could not open folder: {result['error']}"

        else:
            response = "I couldn't identify the Windows action you want me to perform."

    return {
        "intent": intent,
        "plan": plan,
        "capability": capability,
        "parameters": parameters,
        "valid": valid,
        "result": result,
        "response": response,
    }