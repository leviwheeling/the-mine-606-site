# app/models/events.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from ..db.base import Base

class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    start       = Column(DateTime, nullable=False)
    end         = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    image_url   = Column(String(255), default="")
    # new
    venue_area  = Column(String(80), default="Deck")   # e.g., Deck, Indoors
    is_published = Column(Boolean, default=True)
    ticket_url  = Column(String(255), default="")      # future-friendly
