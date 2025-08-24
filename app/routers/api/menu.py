from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.session import get_db
from ...models.menu import MenuItem, MenuCategory, MenuTag, MenuItemTag
from ...schemas.menu import (
    CategoryCreate, CategoryOut,
    TagCreate, TagOut,
    ItemCreate, ItemUpdate, ItemOut
)

router = APIRouter(tags=["Menu API"])

# ---------- Categories ----------
@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(MenuCategory).order_by(MenuCategory.sort_order, MenuCategory.name).all()

@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    if db.query(MenuCategory).filter((MenuCategory.slug==payload.slug) | (MenuCategory.name==payload.name)).first():
        raise HTTPException(status_code=400, detail="Category with same name or slug exists")
    c = MenuCategory(**payload.dict())
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    c = db.query(MenuCategory).get(cat_id)
    if not c: raise HTTPException(404)
    db.delete(c); db.commit()
    return

# ---------- Tags ----------
@router.get("/tags", response_model=List[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return db.query(MenuTag).order_by(MenuTag.type, MenuTag.name).all()

@router.post("/tags", response_model=TagOut, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    if db.query(MenuTag).filter((MenuTag.slug==payload.slug) | (MenuTag.name==payload.name)).first():
        raise HTTPException(status_code=400, detail="Tag with same name or slug exists")
    t = MenuTag(**payload.dict())
    db.add(t); db.commit(); db.refresh(t)
    return t

@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    t = db.query(MenuTag).get(tag_id)
    if not t: raise HTTPException(404)
    db.delete(t); db.commit(); return

# ---------- Items ----------
@router.get("/items", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).order_by(MenuItem.featured_rank.desc(), MenuItem.name).all()

@router.post("/items", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = MenuItem(
        name=payload.name,
        price=payload.price,
        description=payload.description,
        image_url=payload.image_url or "",
        category_id=payload.category_id,
        available=payload.available,
        featured_rank=payload.featured_rank,
    )
    db.add(item); db.flush()
    # tags
    for tag_id in payload.tag_ids:
        db.add(MenuItemTag(item_id=item.id, tag_id=tag_id))
    db.commit(); db.refresh(item)
    return item

@router.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(MenuItem).get(item_id)
    if not item: raise HTTPException(404)
    for k, v in payload.dict().items():
        if k == "tag_ids": continue
        setattr(item, k, v)
    # replace tags
    db.query(MenuItemTag).filter(MenuItemTag.item_id==item_id).delete()
    for tag_id in payload.tag_ids:
        db.add(MenuItemTag(item_id=item_id, tag_id=tag_id))
    db.commit(); db.refresh(item)
    return item

@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).get(item_id)
    if not item: raise HTTPException(404)
    db.delete(item); db.commit(); return

# ---------- Featured reorder (limit 3) ----------
@router.post("/items/featured")
def set_featured(item_ids: List[int], db: Session = Depends(get_db)):
    # clear all ranks
    db.query(MenuItem).update({MenuItem.featured_rank: 0})
    # set 1..3
    for rank, iid in enumerate(item_ids[:3], start=1):
        db.query(MenuItem).filter(MenuItem.id==iid).update({MenuItem.featured_rank: rank})
    db.commit()
    return {"ok": True, "set": item_ids[:3]}
