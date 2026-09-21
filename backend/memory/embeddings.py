import requests


OLLAMA_EMBED_URL = (
    "http://127.0.0.1:11434/api/embed"
)

EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(
    text: str,
) -> list[float]:

    if not text or not text.strip():
        raise ValueError(
            "Cannot generate an embedding "
            "for empty text"
        )

    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    embeddings = data.get(
        "embeddings"
    )

    if not embeddings:
        raise RuntimeError(
            "Ollama returned no embeddings"
        )

    vector = embeddings[0]

    if not isinstance(vector, list):
        raise RuntimeError(
            "Invalid embedding returned by Ollama"
        )

    return vector