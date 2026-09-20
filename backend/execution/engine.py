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

    if action in HIGH_RISK_ACTIONS and not authorized:
        return {
            "success": False,
            "error": f"Action '{action}' requires explicit authorization",
        }

    if action == "open_folder":
        from capabilities.windows import open_folder

        return open_folder(parameters.get("folder"))

    if action in HIGH_RISK_ACTIONS:
        return {
            "success": False,
            "error": f"Action '{action}' is not implemented yet",
        }

    return {
        "success": False,
        "error": f"Unsupported action: {action}",
    }