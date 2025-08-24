# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..settings import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
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
