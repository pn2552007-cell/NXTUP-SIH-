import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings, DEFAULT_DB_PATH

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Handle PostgreSQL dialects for cloud deployment (e.g., Render):
# 1. Render sets DATABASE_URL as 'postgres://...', which SQLAlchemy >=1.4 does not support.
# 2. Ensure consistency with the psycopg (psycopg 3) driver: 'postgresql+psycopg://'.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

if not DATABASE_URL.startswith("sqlite"):
    with engine.connect() as conn:
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
