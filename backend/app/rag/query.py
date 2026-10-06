from pathlib import Path

import chromadb
import requests
from fastapi import HTTPException
from openai import OpenAI

from app.rag.ingestion import ChromaONNXEmbedding
from app.rag.invoice_extractor import extract_invoice_fields
from app.core.config import settings


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

        user_documents = collection.get(
            where={"user_id": user_id},
            include=["metadatas"],
        )

        if not user_documents.get("metadatas"):
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
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": (
                        "You are a strict document assistant. "
                        "Answer only using the provided PDF context. "
                        "Never guess, infer, invent, or substitute values. "
                        "Answer in the same language as the user question. "
                        "Do not mix languages. "
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

        import re

        q = question.lower()

        order_match = re.search(
            r"Order\s+Number\s*:\s*([^\s]+)",
            context,
            re.IGNORECASE,
        )

        invoice_fields = extract_invoice_fields(context)
        total_match = invoice_fields.get("total")

        wants_total = any(
            key in q
            for key in [
                "total",
                "amount",
                "مبلغ",
                "جمع",
                "کل",
            ]
        )

        wants_order = (
            "order number" in q
            or "شماره سفارش" in q
        )

        if wants_total or wants_order:
            parts = []

            if wants_order and order_match:
                parts.append(
                    f"شماره سفارش: {order_match.group(1)}"
                )

            if wants_total and total_match:
                parts.append(
                    f"مبلغ کل: {total_match}"
                )

            if parts:
                answer = "\n".join(parts)

        if not answer:
            answer = "No relevant information found."

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










