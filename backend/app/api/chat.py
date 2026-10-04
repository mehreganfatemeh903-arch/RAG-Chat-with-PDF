from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.rag.query import RAGQueryService
from backend.app.core.dependencies import get_current_user
from backend.app.db.models import User


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

query_service = RAGQueryService()


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )


@router.post("")
def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        return query_service.query(request.question, user_id=current_user.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {exc}",
        ) from exc

