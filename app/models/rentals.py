# app/models/rentals.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from ..db.base import Base

class Rental(Base):
    __tablename__ = "rentals"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), nullable=False)
    email        = Column(String(100), nullable=False)
    date         = Column(DateTime, nullable=False)
    package      = Column(String(100), default="")
    message      = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # new
    phone        = Column(String(40), default="")
    venue_area   = Column(String(80), default="Deck")
    party_size   = Column(String(20), default="")
    status       = Column(String(30), default="new")   # new|pending|approved|closed
