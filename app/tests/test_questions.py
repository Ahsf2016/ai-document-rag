from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ask_question():
    response = client.post(
        "/ask",
        params={
            "question": "What vector database does the project use?",
            "document_id": "2ff66a64-2ffe-4162-935a-7af6803abfb0",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "citations" in data

    assert "Chroma" in data["answer"]
    assert len(data["citations"]) > 0

def test_ask_question_not_in_document():
    response = client.post(
        "/ask",
        params={
            "question": "What is the capital of France?",
            "document_id": "2ff66a64-2ffe-4162-935a-7af6803abfb0",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "The information is not present in the uploaded document."
    )

    assert data["citations"] == []