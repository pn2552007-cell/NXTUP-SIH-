from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup without automatic schema mutation (handled by Alembic)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Longitudinal Skilling Outcome Tracking Platform",
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
        "description": "AI-Powered Longitudinal Skilling Outcome Tracking Platform",
        "status": "online",
        "api_docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
