HIGH_RISK_ACTIONS = {
    "shutdown",
    "restart",
    "close_application",
}


def requires_confirmation(action: str) -> bool:
    return action.lower() in HIGH_RISK_ACTIONS