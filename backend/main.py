from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Optional

from orchestrator.orchestrator import orchestrate


app = FastAPI(title="MANTIS AI Operating Layer")
pending_confirmation: Optional[str] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    intent = None

    try:
        from orchestrator.intent import detect_intent
        intent = detect_intent(request.message)
    except Exception:
        intent = "GENERAL_QUESTION"

    if intent in ["LOCAL_FILE_SEARCH", "WINDOWS_ACTION"]:
        result = orchestrate(request.message)

        if (
            intent == "WINDOWS_ACTION"
            and result["parameters"]
            and result["parameters"].get("action") in {
                "shutdown",
                "restart",
                "close_application",
            }
        ):
            global pending_confirmation
            pending_confirmation = result["parameters"]["action"]

        requires_confirmation = (
            intent == "WINDOWS_ACTION"
            and result["parameters"]
            and result["parameters"].get("action") in {
                "shutdown",
                "restart",
                "close_application",
            }
        )

        return {
            "message": result["response"],
            "intent": result["intent"],
            "result": result["result"],
            "requires_confirmation": requires_confirmation,
            "action": (
                result["parameters"].get("action")
                if result["parameters"]
                else None
            ),
        }

    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "qwen3:4b",
            "prompt": request.message,
            "system": (
                "You are MANTIS, a Windows AI assistant. "
                "You are running locally through Ollama. "
                "Answer the user's request clearly and helpfully."
            ),
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "message": data["response"],
        "intent": "GENERAL_QUESTION",
    }
class ConfirmationRequest(BaseModel):
    action: str


@app.post("/confirm")
def confirm_action(request: ConfirmationRequest):
    global pending_confirmation

    if pending_confirmation is None:
        return {
            "success": False,
            "message": "There is no pending action to confirm.",
        }

    if request.action != pending_confirmation:
        return {
            "success": False,
            "message": "The confirmation does not match the pending action.",
        }

    action = pending_confirmation
    pending_confirmation = None

    return {
        "success": True,
        "message": f"Action '{action}' was explicitly confirmed.",
        "action": action,
    }