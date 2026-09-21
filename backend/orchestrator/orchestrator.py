from orchestrator.intent import detect_intent
from orchestrator.planner import create_plan
from orchestrator.capabilities import select_capability
from orchestrator.validator import validate_plan
from orchestrator.parameters import (
    extract_file_search_params,
    extract_windows_action_params,
)

from capabilities.file_search import search_files
from execution.engine import execute_action
from orchestrator.formatter import format_file_search_result
from permissions.manager import requires_confirmation


def orchestrate(message: str) -> dict:
    intent = detect_intent(message)
    plan = create_plan(intent, message)
    capability = select_capability(intent)

    valid = validate_plan(
        intent,
        plan,
        capability,
    )

    result = None
    parameters = None
    response = None

    # ---------------------------------
    # File search
    # ---------------------------------

    if valid and capability == "file_search":
        parameters = extract_file_search_params(message)

        if parameters["folder"]:
            result = search_files(
                parameters["folder"],
                parameters["extension"],
            )

            response = format_file_search_result(result)

        else:
            response = (
                "I couldn't identify the folder "
                "you want me to search."
            )
    # ---------------------------------
    # Windows actions
    # ---------------------------------

    elif valid and capability == "windows":
        parameters = extract_windows_action_params(message)

        action = parameters.get("action")

        if not action:
            response = (
                "I couldn't identify the Windows action "
                "you want me to perform."
            )

        elif requires_confirmation(action):
            response = (
                f"Confirmation required before performing: "
                f"{action}"
            )

        else:
            result = execute_action(
                action,
                parameters,
            )

            if result["success"] and result.get("verified"):
                if action == "open_folder":
                    response = (
                        f"Opened folder successfully:\n"
                        f"{result['folder']}"
                    )

                elif action == "open_file":
                    response = (
                        f"Opened file successfully:\n"
                        f"{result['file']}"
                    )

                elif action == "open_url":
                    response = (
                        f"Opened URL successfully:\n"
                        f"{result['url']}"
                    )

                elif action == "launch_application":
                    response = (
                        f"Launched "
                        f"{result['application']} "
                        f"successfully."
                    )

                else:
                    response = (
                        f"Action '{action}' "
                        "completed successfully."
                    )

            elif result["success"]:
                response = (
                    f"Action '{action}' completed, "
                    "but MANTIS could not verify the result."
                )

            else:
                response = (
                    f"Could not perform "
                    f"'{action}': "
                    f"{result['error']}"
                )
    return {
        "intent": intent,
        "plan": plan,
        "capability": capability,
        "parameters": parameters,
        "valid": valid,
        "result": result,
        "response": response,
    }