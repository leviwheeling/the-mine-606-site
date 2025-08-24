# app/models/menu.py
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from ..db.base import Base

# Your original MenuItem with minimal extensions (desc, available, featured_rank, category fk)
class MenuCategory(Base):
    __tablename__ = "menu_categories"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(80), nullable=False, unique=True)
    slug       = Column(String(80), nullable=False, unique=True)
    sort_order = Column(Integer, default=0)

    items = relationship("MenuItem", back_populates="category_rel", cascade="all, delete")

class MenuTag(Base):
    __tablename__ = "menu_tags"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String(50), nullable=False, unique=True)     # e.g. vegetarian
    slug  = Column(String(50), nullable=False, unique=True)     # vegetarian
    type  = Column(String(20), nullable=False, default="dietary")  # dietary|allergen|spice|other
    icon  = Column(String(80), nullable=True)

class MenuItemTag(Base):
    __tablename__ = "menu_item_tags"
    id          = Column(Integer, primary_key=True)
    item_id     = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id      = Column(Integer, ForeignKey("menu_tags.id", ondelete="CASCADE"), nullable=False, index=True)
    __table_args__ = (UniqueConstraint("item_id", "tag_id", name="uq_item_tag"),)

class MenuItem(Base):
    __tablename__ = "menu_items"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    # original "category" string kept for backward compat, but use FK going forward
    category      = Column(String(50), nullable=False, default="")  # legacy
    category_id   = Column(Integer, ForeignKey("menu_categories.id", ondelete="SET NULL"), nullable=True)
    price         = Column(Numeric(8, 2), nullable=False)  # a bit wider than 5,2
    allergens     = Column(String(200), default="")        # legacy (tags recommended)
    image_url     = Column(String(255), default="")
    is_favorite   = Column(Boolean, default=False)         # legacy favorite flag
    # new fields:
    description   = Column(Text, nullable=True)
    available     = Column(Boolean, default=True)
    featured_rank = Column(Integer, default=0)             # 1..3 for homepage carousel (0=not featured)

    category_rel  = relationship("MenuCategory", back_populates="items")
    tags          = relationship("MenuTag", secondary="menu_item_tags", lazy="selectin")
