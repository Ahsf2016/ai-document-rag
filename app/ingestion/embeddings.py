from sentence_transformers import SentenceTransformer


model = None


def get_model():
    global model

    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")

    return model


def create_embeddings(chunks: list[dict]) -> list[list[float]]:
    texts = [chunk["text"] for chunk in chunks]

    embeddings = get_model().encode(texts)

    return embeddings.tolist()