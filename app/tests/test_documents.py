from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_document():
    test_content = b"""
    This is a test document for the AI Document RAG Assistant.
    Chroma is used as the vector database.
    """

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test_document.txt",
                test_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "document_id" in data
    assert "filename" in data
    assert "pages" in data
    assert "chunks" in data
    assert "embedding_dimensions" in data
    assert "stored_chunks" in data

    assert data["filename"] == "test_document.txt"
    assert data["pages"] == 1
    assert data["chunks"] > 0
    assert data["embedding_dimensions"] > 0
    assert data["stored_chunks"] > 0


def test_list_documents():
    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_get_document():
    # First upload a document
    test_content = b"""
    This is another test document.
    Chroma is the vector database.
    """

    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "document_lookup_test.txt",
                test_content,
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 200

    upload_data = upload_response.json()
    document_id = upload_data["document_id"]

    # Now retrieve the document
    response = client.get(
        f"/documents/{document_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_id
    assert data["filename"] == "document_lookup_test.txt"