from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests


app = FastAPI(title="MANTIS AI Operating Layer")


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
        "message": data["response"]
    }