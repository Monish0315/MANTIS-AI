from memory.lancedb_store import search_vectors


results = search_vectors(
    "How does MANTIS store vector memory?",
    5,
)

for result in results:
    print(
        result["_distance"],
        "|",
        result["filename"],
        "|",
        result["content"][:150],
    )