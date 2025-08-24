from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EventCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    start: datetime
    end: Optional[datetime] = None
    description: Optional[str] = None
    image_url: Optional[str] = ""
    venue_area: Optional[str] = "Deck"
    is_published: bool = True
    ticket_url: Optional[str] = ""

class EventUpdate(EventCreate):
    pass

class EventOut(BaseModel):
    id: int
    title: str
    start: datetime
    end: Optional[datetime]
    description: Optional[str]
    image_url: Optional[str]
    venue_area: Optional[str]
    is_published: bool
    ticket_url: Optional[str]
    class Config:
        from_attributes = True
