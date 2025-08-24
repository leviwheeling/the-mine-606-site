# app/models/site.py
from sqlalchemy import Column, Integer, String, Boolean, Float
from ..db.base import Base

class SiteSetting(Base):
    __tablename__ = "site_settings"

    id        = Column(Integer, primary_key=True)
    site_name = Column(String(120), default="The Mine 606")
    phone     = Column(String(40), default="")
    email     = Column(String(120), default="")
    address   = Column(String(200), default="")
    city      = Column(String(80), default="")
    state     = Column(String(40), default="")
    zip       = Column(String(20), default="")
    lat       = Column(Float, nullable=True)
    lng       = Column(Float, nullable=True)

    hero_title = Column(String(160), default="What’s Mine is Yours")
    hero_sub   = Column(String(240), default="Across from Appalachian Wireless Arena.")
    show_weather = Column(Boolean, default=True)

    facebook = Column(String(200), default="")
    instagram = Column(String(200), default="")
    tiktok = Column(String(200), default="")
    youtube = Column(String(200), default="")

class Hours(Base):
    __tablename__ = "hours"
    id    = Column(Integer, primary_key=True)
    dow   = Column(String(10), unique=True, nullable=False)  # mon..sun
    open  = Column(String(10), default="")  # "11:00"
    close = Column(String(10), default="")  # "22:00"
    closed= Column(Boolean, default=False)

class HolidayOverride(Base):
    __tablename__ = "holiday_overrides"
    id    = Column(Integer, primary_key=True)
    date  = Column(String(10), unique=True, nullable=False)  # "2025-12-24"
    open  = Column(String(10), default="")
    close = Column(String(10), default="")
    closed= Column(Boolean, default=False)
