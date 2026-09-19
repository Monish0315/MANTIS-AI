from orchestrator.intent import detect_intent
from orchestrator.planner import create_plan


def orchestrate(message: str) -> dict:
    intent = detect_intent(message)
    plan = create_plan(intent, message)

    return {
        "intent": intent,
        "plan": plan,
    }