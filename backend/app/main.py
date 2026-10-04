from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend.app.api.chat import router as chat_router
from backend.app.api.documents import router as documents_router
from backend.app.api.auth import router as auth_router
from backend.app.core.config import settings


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
