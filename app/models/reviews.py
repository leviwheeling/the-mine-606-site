# app/models/reviews.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from ..db.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id             = Column(Integer, primary_key=True, index=True)
    source         = Column(String(20), nullable=False)   # 'yelp'|'google'|'facebook'|'manual'
    embed_code     = Column(Text, nullable=True)          # optional raw widget
    # new structured fields for native rendering
    rating         = Column(Integer, default=5)           # 1..5
    text           = Column(Text, nullable=True)
    url            = Column(String(255), default="")
    reviewer_name  = Column(String(100), default="")
    reviewer_avatar= Column(String(255), default="")
    review_time    = Column(String(40), default="")       # store as string or ISO if needed
    is_featured    = Column(Boolean, default=False)
