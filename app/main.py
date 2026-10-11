from fastapi import FastAPI

from app.api.routes_documents import router as documents_router
from app.api.routes_questions import router as questions_router


app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(documents_router)
app.include_router(questions_router)