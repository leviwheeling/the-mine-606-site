# app/models/musician.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from ..db.base import Base

class MusicianApp(Base):
    __tablename__ = "musician_applications"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), nullable=False)
    email        = Column(String(100), nullable=False)
    link         = Column(String(255), default="")      # YouTube/IG/TikTok
    message      = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # new
    phone        = Column(String(40), default="")
    genre        = Column(String(80), default="")
    socials_json = Column(JSONB, nullable=True)         # {"instagram":"...", "tiktok":"..."}
    file_url     = Column(String(255), default="")      # if later we store EPK uploads
    status       = Column(String(30), default="new")    # new|contacted|booked|closed
