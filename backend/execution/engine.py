from observability.audit import record_execution
HIGH_RISK_ACTIONS = {
    "shutdown",
    "restart",
    "close_application",
}


def execute_action(
    action: str,
    parameters: dict | None = None,
    authorized: bool = False,
) -> dict:
    parameters = parameters or {}

    result = _execute_action(
        action,
        parameters,
        authorized,
    )

    record_execution(
        action,
        parameters,
        result,
    )

    return result


def _execute_action(
    action: str,
    parameters: dict,
    authorized: bool,
) -> dict:

    # ---------------------------------
    # Safety gate
    # ---------------------------------

    if action in HIGH_RISK_ACTIONS and not authorized:
        return {
            "success": False,
            "verified": False,
            "error_code": "AUTHORIZATION_REQUIRED",
            "error": (
                f"Action '{action}' requires "
                "explicit authorization"
            ),
        }

    try:

        # ---------------------------------
        # Open folder
        # ---------------------------------

        if action == "open_folder":
            from capabilities.windows import open_folder

            result = open_folder(
                parameters.get("folder")
            )

            return normalize_result(
                result,
                "FOLDER_OPEN_FAILED",
            )

        # ---------------------------------
        # Open file
        # ---------------------------------

        if action == "open_file":
            from capabilities.windows import open_file

            result = open_file(
                parameters.get("file")
            )

            return normalize_result(
                result,
                "FILE_OPEN_FAILED",
            )

        # ---------------------------------
        # Open URL
        # ---------------------------------

        if action == "open_url":
            from capabilities.windows import open_url

            result = open_url(
                parameters.get("url")
            )

            return normalize_result(
                result,
                "URL_OPEN_FAILED",
            )

        # ---------------------------------
        # Launch application
        # ---------------------------------

        if action == "launch_application":
            from capabilities.windows import (
                launch_application
            )

            result = launch_application(
                parameters.get("application")
            )

            return normalize_result(
                result,
                "APPLICATION_LAUNCH_FAILED",
            )

        # ---------------------------------
        # High-risk actions
        # ---------------------------------

        if action in HIGH_RISK_ACTIONS:
            return {
                "success": False,
                "verified": False,
                "error_code": "NOT_IMPLEMENTED",
                "error": (
                    f"Action '{action}' "
                    "is not implemented yet"
                ),
            }

        # ---------------------------------
        # Unknown action
        # ---------------------------------

        return {
            "success": False,
            "verified": False,
            "error_code": "UNSUPPORTED_ACTION",
            "error": (
                f"Unsupported action: {action}"
            ),
        }

    except Exception as exc:
        return {
            "success": False,
            "verified": False,
            "error_code": "EXECUTION_ERROR",
            "error": str(exc),
        }


def normalize_result(
    result: dict,
    default_error_code: str,
) -> dict:

    if result.get("success"):
        return {
            **result,
            "verified": result.get(
                "verified",
                False,
            ),
            "error_code": None,
        }

    return {
        **result,
        "success": False,
        "verified": False,
        "error_code": result.get(
            "error_code",
            default_error_code,
        ),
    }