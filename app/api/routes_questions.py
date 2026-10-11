from fastapi import APIRouter

from app.retrieval.retriever import retrieve_chunks
from app.generation.llm import generate_answer


router = APIRouter()


@router.post("/ask")
def ask_question(
    question: str,
    top_k: int = 5,
    document_id: str | None = None,
):
    retrieved_chunks = retrieve_chunks(
        question,
        top_k=top_k,
        document_id=document_id,
    )

    if not retrieved_chunks:
        return {
            "question": question,
            "answer": "The information is not present in the uploaded document.",
            "citations": [],
        }

    context = "\n\n".join(
        chunk["text"]
        for chunk in retrieved_chunks
    )

    answer = generate_answer(
        question,
        context,
    )

    citations = []

    seen = set()

    for chunk in retrieved_chunks:
        filename = chunk["metadata"]["filename"]
        page = chunk["metadata"]["page_number"]

        citation_key = (filename, page)

        if citation_key not in seen:
            citations.append(
                {
                    "filename": filename,
                    "page": page,
                }
            )

            seen.add(citation_key)

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
    }