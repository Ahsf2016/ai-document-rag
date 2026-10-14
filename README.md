# DocuMind AI — Document Q&A with Retrieval-Augmented Generation

DocuMind AI is a containerised AI application that allows users to upload documents, ask questions about their contents, and receive AI-generated answers grounded in retrieved document information.

The project combines Retrieval-Augmented Generation (RAG), semantic search, a REST API, and an interactive Streamlit interface to demonstrate how large language models can be used to build practical document question-answering systems.

## Features

- **Document ingestion:** Upload PDF, TXT, and DOCX files.
- **Semantic retrieval:** Generate document embeddings and store them in ChromaDB.
- **AI-powered question answering:** Use the Groq API to generate responses based on retrieved document context.
- **Document citations:** Present supporting document references with answers.
- **Document management:** List, retrieve, and delete uploaded documents.
- **Interactive interface:** Use a Streamlit frontend to interact with the application.
- **REST API:** Expose core functionality through FastAPI endpoints.
- **Containerisation:** Run the backend and frontend using Docker Compose.
- **Persistent storage:** Retain the ChromaDB data in a Docker volume across container recreations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| FastAPI | Backend REST API |
| Streamlit | Interactive frontend |
| ChromaDB | Vector storage and semantic retrieval |
| Sentence Transformers | Text embedding generation |
| Groq API | Large language model inference |
| PyTorch | Machine learning dependencies |
| Docker | Application containerisation |
| Docker Compose | Multi-container orchestration |

## How It Works

1. **Upload:** The user uploads a supported document through the interface.
2. **Extract and chunk:** The backend processes the document into smaller text segments.
3. **Generate embeddings:** Sentence Transformers converts the text segments into vector representations.
4. **Store:** The embeddings, text and associated metadata are stored in ChromaDB.
5. **Ask a question:** The user submits a question through the Streamlit interface.
6. **Retrieve relevant context:** The backend searches the vector database for relevant document segments.
7. **Generate an answer:** The retrieved context is sent to the language model through the Groq API.
8. **Display the response:** The interface presents the generated answer and supporting references.

## Architecture

```text
              User
               |
               v
        Streamlit Frontend
          Port 8501
               |
               v
          FastAPI Backend
          Port 8000
               |
        +------+------+
        |             |
        v             v
   ChromaDB       Groq API
   Vector Store   LLM Inference
        |
        v
   Relevant Document
       Chunks
```

The backend uses Sentence Transformers to generate embeddings. ChromaDB persists the document vectors and metadata through a Docker volume.

## Getting Started

### Prerequisites

Install the following before running the project:

- Git
- Docker Desktop with Docker Compose
- A Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/Ahsf2016/ai-document-rag.git
cd ai-document-rag
```

### 2. Configure environment variables

Create a `.env` file in the project root and add the Groq API key using the variable name expected by the backend configuration.

For example, if the backend reads `GROQ_API_KEY`:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your `.env` file or expose your API key in screenshots, logs, or source code.

### 3. Prepare persistent storage

The Docker Compose configuration expects an existing external Docker volume named `rag-chroma-data`.

If you are setting up a fresh installation and the volume does not exist, create it:

```bash
docker volume create rag-chroma-data
```

Do not remove this volume if it contains documents you want to keep.

### 4. Build and start the application

Build the backend image:

```bash
docker build -t ai-document-rag:latest .
```

Start the services:

```bash
docker compose up -d --build ui
docker compose up -d api
```

### 5. Open the application

- **Streamlit interface:** http://localhost:8501
- **FastAPI Swagger documentation:** http://localhost:8000/docs
- **API health check:** http://localhost:8000/health

The health endpoint should return a healthy status when the backend is running.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/documents/upload` | Upload and process a document |
| GET | `/documents` | List stored documents |
| GET | `/documents/{document_id}` | Retrieve a document by ID |
| DELETE | `/documents/{document_id}` | Delete a document |
| POST | `/ask` | Ask a question about document content |

Interactive endpoint documentation is available at `/docs` while the API is running.

## Example Use Cases

- Ask questions about lecture notes and study materials.
- Retrieve information from technical documentation.
- Search and query reports without manually reading every page.
- Explore how semantic retrieval and large language models can work together.

## Engineering Considerations

The project separates the user interface from the backend API, uses a vector database for retrieval, and stores ChromaDB data in a persistent Docker volume.

The system depends on the quality of document extraction, chunking, retrieval and the language model. Generated answers should be checked against their cited sources, especially when accuracy is important.

## Future Improvements

- Automated tests for API routes and document processing.
- Evaluation of retrieval quality and answer faithfulness.
- Better error handling and document-processing feedback.
- Authentication and access controls.
- Deployment to a publicly accessible hosting environment.
- Performance optimisation and monitoring.

## Author

Developed as a portfolio project exploring Retrieval-Augmented Generation, NLP, API development and containerised AI applications.

**Repository:** https://github.com/Ahsf2016/ai-document-rag
