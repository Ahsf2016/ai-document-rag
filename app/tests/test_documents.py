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




def test_delete_document():
    # Create a temporary test document
    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "document_delete_test.txt",
                b"This is a temporary document created to test deletion.",
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 200
    document_id = upload_response.json()["document_id"]

    # Delete the document
    delete_response = client.delete(
        f"/documents/{document_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["document_id"] == document_id

    # Verify the document no longer exists
    get_response = client.get(
        f"/documents/{document_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json().get("error") == "Document not found"

    # Verify it no longer appears in the document list
    list_response = client.get("/documents")
    remaining_ids = [
        doc["document_id"]
        for doc in list_response.json()["documents"]
    ]

    assert document_id not in remaining_ids


def test_delete_nonexistent_document():
    response = client.delete(
        "/documents/nonexistent-document-id"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
