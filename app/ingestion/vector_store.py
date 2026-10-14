import chromadb


client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
    filename: str,
    document_id: str,
) -> int:

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(f"{document_id}_{index}")

        documents.append(chunk["text"])

        metadatas.append(
            {
                "filename": filename,
                "document_id": document_id,
                "page_number": chunk["page_number"],
                "chunk_index": index,
            }
        )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def list_documents() -> list[dict]:

    results = collection.get(
        include=["metadatas"]
    )

    documents = {}

    for metadata in results["metadatas"]:

        document_id = metadata["document_id"]

        if document_id not in documents:

            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata["filename"],
            }

    return list(documents.values())

def get_document(document_id: str) -> dict | None:

    results = collection.get(
        include=["metadatas"]
    )

    for metadata in results["metadatas"]:

        if metadata["document_id"] == document_id:

            return {
                "document_id": metadata["document_id"],
                "filename": metadata["filename"],
                "chunks": sum(
                    1
                    for item in results["metadatas"]
                    if item["document_id"] == document_id
                ),
            }

    return None


def delete_document(document_id: str) -> bool:
    # Check whether the document exists
    document = get_document(document_id)

    if document is None:
        return False

    # Delete only chunks belonging to this document
    collection.delete(
        where={"document_id": document_id}
    )

    return True
