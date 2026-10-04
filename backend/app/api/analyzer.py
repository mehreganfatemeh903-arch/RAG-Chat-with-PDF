from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from io import BytesIO
from pypdf import PdfReader

from app.db.session import get_db
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


    saved = service.save_analysis(
        db=db,
        document_id=0,
        result=result
    )


    return {
        "id": saved.id,
        "filename": file.filename,
        "result": result
    }