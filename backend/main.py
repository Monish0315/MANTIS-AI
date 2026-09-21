from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Optional
from memory.conversation import initialize_memory
from orchestrator.orchestrator import orchestrate
from memory.conversation import (
    initialize_memory,
    save_message,
)
from memory.conversation import (
    initialize_memory,
    save_message,
    build_conversation_context,
)

app = FastAPI(title="MANTIS AI Operating Layer")
initialize_memory()
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
    save_message(
    "user",
    request.message,
)
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

        assistant_message = result["response"]

        save_message(
            "assistant",
            assistant_message,
        )

        return {
            "message": assistant_message,
            "intent": result["intent"],
            "result": result["result"],
            "requires_confirmation": (
                intent == "WINDOWS_ACTION"
                and result["parameters"]
                and result["parameters"].get("action") in {
                    "shutdown",
                    "restart",
                    "close_application",
                }
            ),
            "action": (
                result["parameters"].get("action")
                if result["parameters"]
                else None
            ),
        }

    conversation_context = build_conversation_context(
        limit=10
    )

    system_prompt = (
        "You are MANTIS, a Windows AI assistant. "
        "You are running locally through Ollama. "
        "Answer the user's request clearly and helpfully."
    )

    if conversation_context:
        system_prompt += (
            "\n\nHere is the recent conversation history. "
            "Use it to understand references such as "
            "'it', 'that', 'the previous one', or "
            "'what I just said'.\n\n"
            + conversation_context
        )

    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "qwen3:4b",
            "prompt": request.message,
            "system": system_prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    assistant_message = data["response"]

    save_message(
        "assistant",
        assistant_message,
    )

    return {
        "message": assistant_message,
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

    from execution.engine import execute_action

    result = execute_action(
        action,
        authorized=True,
    )

    if result["success"]:
        return {
            "success": True,
            "message": f"Action '{action}' was executed successfully.",
            "action": action,
            "result": result,
        }

    return {
        "success": False,
        "message": result["error"],
        "action": action,
        "result": result,
    }
@app.get("/memory")
def memory():
    from memory.conversation import get_recent_messages

    return {
        "messages": get_recent_messages(20)
    }
@app.post("/ingest")
def ingest(path: str):
    from memory.ingestion import ingest_document

    return ingest_document(path)
@app.get("/documents")
def documents():
    from memory.conversation import get_documents

    return {
        "documents": get_documents()
    }