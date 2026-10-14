import os
import tempfile
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException


from app.ingestion.loaders import (
    extract_pdf_text,
    extract_txt_text,
    extract_docx_text,
)
from app.ingestion.chunking import chunk_pages
from app.ingestion.embeddings import create_embeddings
from app.ingestion.vector_store import (
    store_chunks,
    list_documents,
    get_document,
    delete_document,
)




router = APIRouter()


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename.lower()
    if not filename.endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are currently supported."
        )

    document_id = str(uuid.uuid4())

    file_contents = await file.read()

    file_extension = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
    ) as temp_file:
        temp_file.write(file_contents)
        temp_file_path = temp_file.name

    try:
        if filename.endswith(".pdf"):
            pages = extract_pdf_text(temp_file_path)

        elif filename.endswith(".txt"):
            pages = extract_txt_text(temp_file_path)

        elif filename.endswith(".docx"):
            pages = extract_docx_text(temp_file_path)

        chunks = chunk_pages(pages)

        embeddings = create_embeddings(chunks)

        stored_chunks = store_chunks(
            chunks,
            embeddings,
            file.filename,
            document_id,
        )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "embedding_dimensions": len(embeddings[0]),
            "stored_chunks": stored_chunks,
        }

    finally:
        os.remove(temp_file_path)


@router.get("/documents")
def get_documents():

    documents = list_documents()

    return {
        "documents": documents
    }

@router.get("/documents/{document_id}")
def get_document_by_id(document_id: str):

    document = get_document(document_id)

    if document is None:
        return {
            "error": "Document not found"
        }

    return document


@router.delete("/documents/{document_id}")
def delete_document_by_id(document_id: str):
    deleted = delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }
