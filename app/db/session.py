# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..settings import get_settings

settings = get_settings()

# Convert postgresql:// to postgresql+psycopg2:// for psycopg2 compatibility
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Dependency (for FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
