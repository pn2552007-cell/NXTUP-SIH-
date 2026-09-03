import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
DEFAULT_DB_PATH = str(ROOT_DIR / "skillpulse.db").replace("\\", "/")

# Explicitly load environment files
load_dotenv(ROOT_DIR / ".env", override=True)
load_dotenv(BACKEND_DIR / ".env", override=True)
load_dotenv(".env", override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillPulse"
    API_V1_STR: str = "/api"
    JWT_SECRET: str = "skillpulse-production-secure-jwt-secret-key-2026"
    SECRET_KEY: str = "skillpulse-production-secure-jwt-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    AI_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "llama-3.3-70b-versatile"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()
