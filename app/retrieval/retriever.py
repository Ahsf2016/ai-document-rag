from app.ingestion.embeddings import get_model
from app.ingestion.vector_store import collection


def retrieve_chunks(
    question: str,
    top_k: int = 5,
    document_id: str | None = None,
    max_distance: float = 1.6,
) -> list[dict]:

    query_embedding = get_model().encode([question]).tolist()

    where_filter = None

    if document_id:
        where_filter = {
            "document_id": document_id
        }

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    print("QUERY:", question)
    print("DISTANCES:", results["distances"])
    print("DOCUMENTS:", results["documents"])

    retrieved_chunks = []

    for i in range(len(results["documents"][0])):

        distance = results["distances"][0][i]

        if distance <= max_distance:
            retrieved_chunks.append(
                {
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": distance,
                }
            )

    return retrieved_chunks