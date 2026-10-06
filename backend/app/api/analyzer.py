import hashlib
import json
import traceback
from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.models import User, Document
from app.db.session import get_db
from app.extraction.models import DocumentAnalysis
from app.analyzer.service import DocumentAnalyzerService


router = APIRouter(
    prefix="/analyzer",
    tags=["AI Analyzer"],
)

service = DocumentAnalyzerService()

pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files supported",
        )

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    existing_document = db.scalar(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.file_hash == file_hash,
        )
    )

    if existing_document:
        existing_analysis = db.scalar(
            select(DocumentAnalysis)
            .where(
                DocumentAnalysis.document_id == existing_document.id
            )
            .order_by(DocumentAnalysis.id.desc())
        )

        if existing_analysis:
            return {
                "id": existing_analysis.id,
                "document_id": existing_document.id,
                "filename": existing_document.filename,
                "result": {
                    "detection": {
                        "document_type": existing_analysis.document_type,
                        "confidence": existing_analysis.confidence,
                    },
                    "analysis": json.loads(
                        existing_analysis.extracted_data
                    ),
                },
            }

    reader = PdfReader(BytesIO(content))

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if not page_text.strip():
            images = convert_from_bytes(
                content,
                first_page=page_number,
                last_page=page_number,
                poppler_path=settings.poppler_path or None,
                dpi=300,
            )

            if images:
                page_text = pytesseract.image_to_string(
                    images[0],
                    lang="fas+eng",
                    config="--psm 11",
                )

        text += page_text

    result = service.analyze(text)

    document = Document(
        user_id=current_user.id,
        document_id=str(uuid4()),
        filename=file.filename,
        stored_filename=file.filename,
        file_hash=file_hash,
        file_size=len(content),
        page_count=len(reader.pages),
        status="analyzed",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    saved = service.save_analysis(
        db=db,
        document_id=document.id,
        result=result,
    )

    return {
        "id": saved.id,
        "document_id": document.id,
        "filename": file.filename,
        "result": result,
    }


@router.get("/{document_id}")
def get_analysis(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = db.scalar(
        select(DocumentAnalysis)
        .where(
            DocumentAnalysis.document_id == document.id
        )
        .order_by(DocumentAnalysis.id.desc())
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return {
        "id": analysis.id,
        "document_id": analysis.document_id,
        "document_type": analysis.document_type,
        "confidence": analysis.confidence,
        "analysis": json.loads(
            analysis.extracted_data
        ),
    }


