from pathlib import Path
from typing import List
from uuid import uuid4

from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import chromadb
from pypdf import PdfReader
from llama_index.core import Document
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from app.core.config import settings


class ChromaONNXEmbedding(BaseEmbedding):
    def __init__(self):
        super().__init__(model_name="all-MiniLM-L6-v2")
        self._embedding_function = ONNXMiniLM_L6_V2()

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._embedding_function([text])[0]

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._embedding_function([query])[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)


class DocumentIngestionService:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.chroma_path = Path(settings.chroma_path)

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)

        self.embedding = ChromaONNXEmbedding()

    def delete_document(self, document_id: str, user_id: int):
        client = chromadb.PersistentClient(
            path=str(self.chroma_path)
        )

        collection = client.get_or_create_collection(
            name="documents"
        )

        collection.delete(
            where={
                "$and": [
                    {"document_id": document_id},
                    {"user_id": user_id},
                ]
            }
        )

    def ingest(
        self,
        file_path: str,
        document_id: str | None = None,
        user_id: int | None = None,
    ):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        document_id = document_id or str(uuid4())

        reader = PdfReader(str(path))

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = ""

            images = convert_from_path(
                str(path),
                first_page=page_number,
                last_page=page_number,
                poppler_path=r"C:/poppler/poppler-26.09.0/Library/bin",
                dpi=300,
            )

            text = pytesseract.image_to_string(
                images[0],
                lang="fas+eng",
                config="--psm 6",
            )

            if not text.strip():
                text = page.extract_text() or ""

            if text.strip():
                documents.append(
                    Document(
                        text=text,
                        metadata={
                            "document_id": document_id,
                            "user_id": user_id,
                            "filename": path.name,
                            "page_number": page_number,
                            "page_label": str(page_number),
                        },
                    )
                )

        if not documents:
            raise ValueError(
                "No extractable text found in PDF."
            )

        splitter = SentenceSplitter(
            chunk_size=800,
            chunk_overlap=120,
        )

        ids = []
        texts = []
        metadatas = []
        embeddings = []

        for doc in documents:
            nodes = splitter.get_nodes_from_documents(
                [doc]
            )

            for node in nodes:
                text = node.text.strip()

                if not text:
                    continue

                ids.append(str(uuid4()))

                texts.append(text)

                metadatas.append(
                    {
                        "document_id": document_id,
                        "user_id": user_id,
                        "filename": path.name,
                        "page_number": node.metadata.get(
                            "page_number"
                        ),
                        "page_label": node.metadata.get(
                            "page_label"
                        ),
                    }
                )

                embeddings.append(
                    self.embedding.get_text_embedding(
                        text
                    )
                )

        client = chromadb.PersistentClient(
            path=str(self.chroma_path)
        )

        collection = client.get_or_create_collection(
            name="documents"
        )

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return {
            "document_id": document_id,
            "user_id": user_id,
            "filename": path.name,
            "pages": len(reader.pages),
            "chunks": len(ids),
            "status": "indexed",
        }
