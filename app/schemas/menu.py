from typing import List, Optional
from pydantic import BaseModel, Field, condecimal

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    slug: str = Field(..., min_length=2, max_length=80)
    sort_order: int = 0

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    sort_order: int
    class Config: from_attributes = True

class TagCreate(BaseModel):
    name: str
    slug: str
    type: str = "dietary"  # dietary|allergen|spice|other
    icon: Optional[str] = None

class TagOut(BaseModel):
    id: int
    name: str
    slug: str
    type: str
    icon: Optional[str] = None
    class Config: from_attributes = True

class ItemCreate(BaseModel):
    name: str
    price: condecimal(max_digits=8, decimal_places=2)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    available: bool = True
    featured_rank: int = 0
    tag_ids: List[int] = []

class ItemUpdate(ItemCreate):
    pass

class ItemOut(BaseModel):
    id: int
    name: str
    price: condecimal(max_digits=8, decimal_places=2)
    description: Optional[str]
    image_url: Optional[str]
    category_id: Optional[int]
    available: bool
    featured_rank: int
    is_favorite: Optional[bool] = None  # legacy
    class Config: from_attributes = True
