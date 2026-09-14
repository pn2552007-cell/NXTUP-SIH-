from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.router import api_router

from app.database import engine, Base
import app.models.models  # ensure models are loaded for table creation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables exist on startup
    Base.metadata.create_all(bind=engine)
    from app.services.schema_upgrade import upgrade_outcome_schema
    upgrade_outcome_schema(engine)
    yield

app = FastAPI(
    title=f"{settings.PROJECT_NAME} — {settings.PLATFORM_TITLE}",
    description="AI-Powered Skilling Outcome Platform — Longitudinal tracking from training to verified employment, retention, and wage progression.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include central API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "title": settings.PLATFORM_TITLE,
        "status": "online",
        "api_docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
