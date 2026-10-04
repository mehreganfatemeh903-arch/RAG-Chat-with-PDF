from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.dependencies import get_current_user
from backend.app.db.models import User, Document
from backend.app.db.session import get_db
from backend.app.rag.ingestion import DocumentIngestionService



router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

ingestion_service = DocumentIngestionService()

@router.get("")
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = db.scalars(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    ).all()

    return documents


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(
            Document.document_id == document_id,
            Document.user_id == current_user.id,
        )
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = Path(settings.upload_dir) / document.stored_filename

    ingestion_service.delete_document(
        document_id=document.document_id,
        user_id=current_user.id,
    )

    db.delete(document)
    db.commit()

    file_path.unlink(missing_ok=True)

    return {
        "status": "deleted",
        "document_id": document_id,
    }

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    content = await file.read()

    max_size = settings.max_file_size_mb * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Maximum file size is {settings.max_file_size_mb} MB.",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_filename = Path(file.filename).name
    stored_filename = f"{uuid4().hex}_{original_filename}"
    file_path = upload_dir / stored_filename
    document_id = str(uuid4())

    file_path.write_bytes(content)

    try:
        result = ingestion_service.ingest(
            str(file_path),
            document_id=document_id,
            user_id=current_user.id,
        )

        document = Document(
            user_id=current_user.id,
            document_id=document_id,
            filename=original_filename,
            stored_filename=stored_filename,
            file_size=len(content),
            page_count=result["pages"],
            status="indexed",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            **result,
            "id": document.id,
            "user_id": document.user_id,
            "filename": document.filename,
            "status": document.status,
        }

    except Exception as exc:
        db.rollback()
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Document indexing failed: {exc}",
        ) from exc



