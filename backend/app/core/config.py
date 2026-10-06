from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "RAG Chat with PDF"
    app_version: str = "1.0.0"
    environment: str = "development"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    embedding_model: str = "text-embedding-3-small"

    chroma_path: str = "./data/chroma"
    upload_dir: str = "./data/uploads"

    max_file_size_mb: int = 25
    top_k: int = 5

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    chunk_size: int = 800
    chunk_overlap: int = 120

    tesseract_cmd: str = ""
    poppler_path: str = ""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
