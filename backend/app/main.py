from fastapi import FastAPI
import app.db.import_models
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.auth import router as auth_router
from app.core.config import settings
from app.api.analyzer import router as analyzer_router



app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-oriented intelligent PDF RAG API "
        "with document citations."
    ),
)

app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(analyzer_router)


@app.get("/health")
def health():
    return JSONResponse(
        content={
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "openai_configured": bool(settings.openai_api_key),
        },
        media_type="application/json; charset=utf-8",
    )
