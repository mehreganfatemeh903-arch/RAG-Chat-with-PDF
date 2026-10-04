import json
from sqlalchemy import select
from app.extraction.models import DocumentAnalysis
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from io import BytesIO
from uuid import uuid4
from pypdf import PdfReader

from app.db.session import get_db
from app.db.models import Document
from app.analyzer.service import DocumentAnalyzerService


router = APIRouter(
    prefix="/analyzer",
    tags=["AI Analyzer"]
)


service = DocumentAnalyzerService()


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files supported"
        )

    content = await file.read()

    reader = PdfReader(
        BytesIO(content)
    )

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""


    result = service.analyze(text)


    document = Document(
        user_id=1,
        document_id=str(uuid4()),
        filename=file.filename,
        stored_filename=file.filename,
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
        result=result
    )


    return {
        "id": saved.id,
        "document_id": document.id,
        "filename": file.filename,
        "result": result
    }
@router.get("/{document_id}")
def get_analysis(
    document_id: int,
    db: Session = Depends(get_db)
):

    analysis = db.scalar(
        select(DocumentAnalysis)
        .where(
            DocumentAnalysis.document_id == document_id
        )
        .order_by(DocumentAnalysis.id.desc())
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    return {
        "id": analysis.id,
        "document_id": analysis.document_id,
        "document_type": analysis.document_type,
        "confidence": analysis.confidence,
        "analysis": json.loads(
            analysis.extracted_data
        )
    }