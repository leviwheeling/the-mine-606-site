from pydantic import BaseModel, Field
from typing import Optional, List

class SiteSettingUpdate(BaseModel):
    site_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    hero_title: Optional[str] = None
    hero_sub: Optional[str] = None
    show_weather: Optional[bool] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None

class HourUpdate(BaseModel):
    dow: str
    open: str = Field("", description="HH:MM")
    close: str = Field("", description="HH:MM")
    closed: bool = False

class HolidayOverrideUpdate(BaseModel):
    date: str  # YYYY-MM-DD
    open: str = ""
    close: str = ""
    closed: bool = False
