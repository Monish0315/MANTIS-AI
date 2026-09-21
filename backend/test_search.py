from memory.vector_search import search_similar_chunks


results = search_similar_chunks(
    "What is MANTIS",
    10,
)

for result in results:
    print(
        result["similarity"],
        "|",
        result["filename"],
        "|",
        result["content"][:100],
    )