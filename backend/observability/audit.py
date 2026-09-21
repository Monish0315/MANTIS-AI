from datetime import datetime, timezone


_audit_log: list[dict] = []


def record_execution(
    action: str,
    parameters: dict | None,
    result: dict,
) -> dict:
    entry = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "action": action,
        "parameters": parameters or {},
        "success": result.get("success", False),
        "verified": result.get("verified", False),
        "error_code": result.get("error_code"),
        "error": result.get("error"),
    }

    _audit_log.append(entry)

    return entry


def get_execution_history() -> list[dict]:
    return list(_audit_log)


def clear_execution_history() -> None:
    _audit_log.clear()