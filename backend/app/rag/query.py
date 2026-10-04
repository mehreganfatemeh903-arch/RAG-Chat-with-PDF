from pathlib import Path

import chromadb
import requests
from fastapi import HTTPException
from openai import OpenAI

from backend.app.rag.ingestion import ChromaONNXEmbedding
from backend.app.core.config import settings


class RAGQueryService:
    def __init__(self):
        self.chroma_path = Path(settings.chroma_path)
        self.embedding = ChromaONNXEmbedding()
        self.client = None

        if settings.openai_api_key:
            self.client = OpenAI(
                api_key=settings.openai_api_key
            )

    def query(self, question: str, user_id: int):
        client = chromadb.PersistentClient(
            path=str(self.chroma_path)
        )

        collection = client.get_or_create_collection(
            name="documents"
        )

        if collection.count() == 0:
            raise HTTPException(
                status_code=404,
                detail="No indexed documents found.",
            )

        query_embedding = self.embedding.get_query_embedding(question)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=settings.top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
            where={
                "user_id": user_id
            },
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # For small PDFs, use full retrieved content instead of a partial chunk
        if documents and len(documents) == 1:
            all_results = collection.get(
                where={
                    "user_id": user_id
                },
                include=[
                    "documents",
                    "metadatas",
                ],
            )

            if all_results.get("documents"):
                documents = all_results["documents"]
                metadatas = all_results["metadatas"]
                distances = [0] * len(documents)

        if not documents:
            return {
                "answer": "No relevant information found.",
                "sources": [],
            }

        sources = []

        for text, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            metadata = metadata or {}

            sources.append(
                {
                    "filename": metadata.get("filename", "Unknown"),
                    "page": metadata.get("page_number"),
                    "score": distance,
                    "text": text[:1500],
                }
            )

        context = "\n\n---\n\n".join(
            item["text"]
            for item in sources
        )

        context = (
            context
            .replace("â", "")
            .replace("�", "")
            .strip()
        )

        answer = None

        try:
            import requests

            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": (
                        "You are a helpful RAG assistant. ""Answer only using the provided PDF context. ""Answer in the same language as the user question. ""Do not mix languages. "
                        "Give a short direct answer. "
                        "If missing, say not found.\n\n"
                        f"PDF context:\n{context}\n\n"
                        f"Question: {question}"
                    ),
                    "stream": False,
                },
                timeout=120,
            )

            answer = ollama_response.json().get("response")

        except Exception as e:
            print("OLLAMA ERROR:", e)
            answer = None

        # Keep LLM answer if available

        if not answer:
            import re

            lines = [
                line.strip()
                for line in context.splitlines()
                if line.strip()
            ]

            extracted = []

            for line in lines:
                lower = line.lower()

                if any(
                    key in lower
                    for key in [
                        "order number",
                        "order date",
                        "total",
                        "amount",
                        "price",
                        "nikon",
                        "invoice",
                    ]
                ):
                    extracted.append(line)

            if extracted:
                answer = (
                    "Answer from PDF:\n\n"
                    + "\n".join(extracted[:10])
                )
            else:
                answer = (
                    "Relevant text from PDF:\n\n"
                    + context[:2000]
                )

        source_text = "\n\nSources:\n"
        for source in sources:
            source_text += (
                f"- {source.get('filename', 'Unknown')}"
                f" | Page: {source.get('page', 'Unknown')}\n"
            )

        return {
            "answer": answer + source_text,
            "sources": sources,
        }
