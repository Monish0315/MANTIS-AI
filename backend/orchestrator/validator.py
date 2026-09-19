def validate_plan(intent: str, plan: list[str], capability: str) -> bool:
    if not intent:
        return False

    if not plan:
        return False

    if not capability:
        return False

    return True