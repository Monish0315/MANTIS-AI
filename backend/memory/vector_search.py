import math

from memory.embeddings import generate_embedding
from memory.conversation import (
    get_all_chunk_embeddings,
)


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same dimensions"
        )

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return (
        dot_product
        / (magnitude_a * magnitude_b)
    )


def search_similar_chunks(
    query: str,
    top_k: int = 5,
) -> list[dict]:

    if not query or not query.strip():
        return []

    if top_k <= 0:
        return []

    query_embedding = generate_embedding(
        query
    )

    stored_chunks = (
        get_all_chunk_embeddings()
    )

    results = []

    for chunk in stored_chunks:
        similarity = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "filename": chunk["filename"],
                "path": chunk["path"],
                "content": chunk["content"],
                "similarity": similarity,
            }
        )

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return results[:top_k]