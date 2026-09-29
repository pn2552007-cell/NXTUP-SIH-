import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.router import api_router

from app.database import engine, Base
import app.models.models  # ensure models are loaded for table creation

_logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables exist on startup
    Base.metadata.create_all(bind=engine)
    from app.services.schema_upgrade import upgrade_outcome_schema
    upgrade_outcome_schema(engine)

    # ── Optional one-time seed (never runs unless SEED_DB=1 is set) ───────────
    # To seed the production database:
    #   1. Add env var  SEED_DB=1  in Render → Environment
    #   2. Trigger a Manual Deploy and watch the logs
    #   3. After "seeding complete" appears, DELETE the SEED_DB var and redeploy
    seed_flag = os.environ.get("SEED_DB", "").strip().lower()
    if seed_flag in ("1", "true", "force"):
        _logger.warning("SEED_DB flag detected (%s) — running database seed...", seed_flag)
        if seed_flag == "force":
            os.environ["SEED_FORCE"] = "1"
        try:
            from database.seed import seed_database
            seed_database()
            _logger.warning(
                "✅ Database seeding complete. "
                "IMPORTANT: Remove the SEED_DB environment variable now to prevent re-seeding on next restart."
            )
        except Exception as seed_err:
            _logger.error("❌ Seeding failed: %s", seed_err, exc_info=True)
    # ─────────────────────────────────────────────────────────────────────────

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
