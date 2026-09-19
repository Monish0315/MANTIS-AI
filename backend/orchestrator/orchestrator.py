from orchestrator.intent import detect_intent
from orchestrator.planner import create_plan
from orchestrator.capabilities import select_capability
from orchestrator.validator import validate_plan


def orchestrate(message: str) -> dict:
    intent = detect_intent(message)
    plan = create_plan(intent, message)
    capability = select_capability(intent)

    valid = validate_plan(intent, plan, capability)

    return {
        "intent": intent,
        "plan": plan,
        "capability": capability,
        "valid": valid,
    }