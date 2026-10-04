# RAG Chat with PDF

A Retrieval-Augmented Generation (RAG) application for uploading PDF documents, indexing their content, retrieving relevant passages, and answering questions about uploaded documents.

## Features

- PDF upload through Streamlit
- PDF text extraction with pypdf
- ChromaDB vector storage
- Local ONNX embeddings using all-MiniLM-L6-v2
- Semantic document retrieval
- Source filename and page metadata
- FastAPI backend
- Streamlit frontend
- OpenAI LLM support
- Ollama local LLM support
- Persian and English document/question support

## Architecture

Streamlit
    |
    v
FastAPI
    |
    +-- PDF Upload -> pypdf -> Chunking -> ChromaDB
    |
    +-- Question -> Local Embedding -> ChromaDB -> LLM -> Answer + Sources

## Project Structure

RAG-Chat-with-PDF/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   └── documents.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   ├── rag/
│   │   │   ├── ingestion.py
│   │   │   └── query.py
│   │   └── main.py
│   └── tests/
│       └── test_health.py
├── frontend/
│   └── app.py
├── data/
│   ├── chroma/
│   └── uploads/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── requirements-current.txt

## Requirements

- Python 3.12+
- FastAPI
- Uvicorn
- ChromaDB
- pypdf
- Streamlit
- OpenAI API or local LLM such as Ollama

## Run Backend

uvicorn backend.app.main:app --reload --port 8000

Health endpoint:

http://127.0.0.1:8000/health

## Run Frontend

streamlit run frontend/app.py

## API

GET /health

POST /documents/upload

POST /chat

Example:

{
  "question": "What projects are listed in the document?"
}

The response contains the answer and retrieved sources.

## RAG Pipeline

1. Upload PDF.
2. Extract text with pypdf.
3. Create document chunks.
4. Split text into chunks.
5. Generate local embeddings.
6. Store embeddings in ChromaDB.
7. Embed the user's question.
8. Retrieve relevant passages.
9. Send context to the configured LLM.
10. Return answer and sources.

## Current Status

FastAPI: working
PDF upload: working
PDF extraction: working
ChromaDB: working
Local embeddings: working
Document retrieval: working
Persian retrieval: working
Source metadata: working
Streamlit frontend: working
UTF-8 encoding: fixed
Health test: passed

OpenAI configuration is detected, but the current OpenAI account has no remaining API credit.

Ollama is supported as the local LLM option.

## Testing

If pytest is installed:

python -m pytest .\backend\tests -q

The health test is located at:

backend/tests/test_health.py

## Data

Uploaded PDFs:

data/uploads/

ChromaDB:

data/chroma/

These directories are excluded from Git.

## License

For personal, educational, and development use.
