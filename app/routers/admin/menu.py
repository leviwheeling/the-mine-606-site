from __future__ import annotations

from typing import List, Optional
from datetime import datetime
import os

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload

from ...db.session import get_db
from ...models.menu import MenuItem, MenuCategory, MenuTag, MenuItemTag
from ...security.auth import admin_required
from ...services.media import save_upload

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request, "page_title": "Admin • Menu"}
    base.update(kw); return base

@router.get("/menu", response_class=HTMLResponse)
def menu_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_required(request)

    q = (request.query_params.get("q") or "").strip()
    categories = db.query(MenuCategory).order_by(MenuCategory.sort_order.asc(), MenuCategory.name.asc()).all()
    tags = db.query(MenuTag).order_by(MenuTag.type.asc(), MenuTag.name.asc()).all()

    query = db.query(MenuItem).options(
        joinedload(MenuItem.tags),
        joinedload(MenuItem.category_rel)
    )
    if q:
        query = query.filter(MenuItem.name.ilike(f"%{q}%"))
    items = query.order_by(MenuItem.name.asc()).all()

    featured = (
        db.query(MenuItem)
        .filter(MenuItem.featured_rank > 0, MenuItem.available == True)  # noqa: E712
        .order_by(MenuItem.featured_rank.asc())
        .limit(9).all()
    )
    return request.app.templates.TemplateResponse(
        "admin/menu.html",
        ctx(request, categories=categories, tags=tags, items=items, featured=featured)
    )

@router.get("/menu/edit/{item_id}", response_class=HTMLResponse)
def edit_item_form(request: Request, item_id: int, db: Session = Depends(get_db)):
    admin_required(request)
    
    item = db.query(MenuItem).options(
        joinedload(MenuItem.tags),
        joinedload(MenuItem.category_rel)
    ).filter(MenuItem.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    categories = db.query(MenuCategory).order_by(MenuCategory.sort_order.asc(), MenuCategory.name.asc()).all()
    tags = db.query(MenuTag).order_by(MenuTag.type.asc(), MenuTag.name.asc()).all()
    
    # Get current tag IDs for pre-selection
    current_tag_ids = [t.id for t in item.tags]
    
    return request.app.templates.TemplateResponse(
        "admin/menu_edit.html",
        ctx(request, item=item, categories=categories, tags=tags, current_tag_ids=current_tag_ids)
    )

@router.post("/menu/edit/{item_id}")
async def update_item(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db),
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    featured_rank: int = Form(0),
    available: Optional[bool] = Form(False),
    image: Optional[UploadFile] = File(None),
):
    admin_required(request)
    
    item = db.query(MenuItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Handle image replacement
    if image and image.filename:
        # Clean up old image if it exists
        if item.image_url and item.image_url.startswith("/static/media/"):
            old_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", item.image_url[1:])
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass  # Don't fail if cleanup fails
        
        # Upload new image
        new_image_url = await save_upload(image, subdir="menu")
        item.image_url = new_image_url
    
    # Update other fields
    item.name = name.strip()
    item.price = price
    item.category_id = category_id
    item.description = (description or "").strip() or None
    item.featured_rank = max(0, min(int(featured_rank or 0), 9))
    item.available = bool(available)
    
    # Update tags
    form = await request.form()
    new_tag_ids = []
    for key, value in form.items():
        if key == "tag_ids":
            try:
                new_tag_ids.append(int(value))
            except ValueError:
                continue
    
    # Remove old tag associations
    db.query(MenuItemTag).filter(MenuItemTag.item_id == item_id).delete()
    
    # Add new tag associations
    if new_tag_ids:
        tag_ids_clean = list({int(t) for t in new_tag_ids})
        existing = db.query(MenuTag).filter(MenuTag.id.in_(tag_ids_clean)).all()
        for t in existing:
            db.add(MenuItemTag(item_id=item.id, tag_id=t.id))
    
    db.commit()
    return RedirectResponse("/admin/menu", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/menu/feature")
async def update_featured(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    form = await request.form()
    # pattern: rank_<id> = number
    changed = 0
    for key, val in form.items():
        if not key.startswith("rank_"):
            continue
        try:
            item_id = int(key.split("_", 1)[1])
            rank = int(val or 0)
        except ValueError:
            continue
        item = db.query(MenuItem).get(item_id)
        if item:
            item.featured_rank = max(0, min(rank, 9))
            changed += 1
    if changed:
        db.commit()
    return RedirectResponse("/admin/menu", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/menu/create")
async def create_item(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    featured_rank: int = Form(0),
    available: Optional[bool] = Form(False),
    image: Optional[UploadFile] = File(None),
):
    admin_required(request)

    # Upload image if provided
    image_url = None
    if image and image.filename:
        image_url = await save_upload(image, subdir="menu")

    item = MenuItem(
        name=name.strip(),
        price=price,
        category_id=category_id,
        description=(description or "").strip() or None,
        featured_rank=max(0, min(int(featured_rank or 0), 9)),
        available=bool(available),
        image_url=image_url or "",
    )
    db.add(item)
    db.flush()  # get id

    # attach tags from form data
    form = await request.form()
    tag_ids = []
    for key, value in form.items():
        if key == "tag_ids":
            try:
                tag_ids.append(int(value))
            except ValueError:
                continue
    
    if tag_ids:
        # de-dup and validate
        tag_ids_clean = list({int(t) for t in tag_ids})
        existing = db.query(MenuTag).filter(MenuTag.id.in_(tag_ids_clean)).all()
        for t in existing:
            db.add(MenuItemTag(item_id=item.id, tag_id=t.id))

    db.commit()
    return RedirectResponse("/admin/menu", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/menu/toggle/{item_id}")
def toggle_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    admin_required(request)
    item = db.query(MenuItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.available = not bool(item.available)
    db.commit()
    return RedirectResponse("/admin/menu", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/menu/delete/{item_id}")
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    admin_required(request)
    item = db.query(MenuItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Clean up image file if it exists
    if item.image_url and item.image_url.startswith("/static/media/"):
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", item.image_url[1:])
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass  # Don't fail if cleanup fails
    
    # delete tag links first (if not configured cascade)
    db.query(MenuItemTag).filter(MenuItemTag.item_id == item_id).delete()
    db.delete(item)
    db.commit()
    return RedirectResponse("/admin/menu", status_code=status.HTTP_303_SEE_OTHER)

# Keep existing category and tag creation routes
@router.post("/menu/category/create")
def create_category(request: Request,
                    name: str = Form(...),
                    slug: str = Form(...),
                    sort_order: int = Form(0),
                    db: Session = Depends(get_db)):
    admin_required(request)
    c = MenuCategory(name=name.strip(), slug=slug.strip(), sort_order=sort_order)
    db.add(c); db.commit()
    return RedirectResponse("/admin/menu", status_code=303)

@router.post("/menu/tag/create")
def create_tag(request: Request,
               name: str = Form(...),
               slug: str = Form(...),
               type: str = Form("dietary"),
               db: Session = Depends(get_db)):
    admin_required(request)
    t = MenuTag(name=name.strip(), slug=slug.strip(), type=type)
    db.add(t); db.commit()
    return RedirectResponse("/admin/menu", status_code=303)

# Dedicated tag management routes
@router.get("/tags", response_class=HTMLResponse)
def tags_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    
    tags = db.query(MenuTag).order_by(MenuTag.type.asc(), MenuTag.name.asc()).all()
    return request.app.templates.TemplateResponse(
        "admin/tags.html",
        ctx(request, tags=tags)
    )

@router.post("/tags/create")
def create_tag_dedicated(request: Request,
                        name: str = Form(...),
                        slug: str = Form(...),
                        type: str = Form("dietary"),
                        icon: str = Form(""),
                        db: Session = Depends(get_db)):
    admin_required(request)
    t = MenuTag(name=name.strip(), slug=slug.strip(), type=type, icon=icon.strip() or None)
    db.add(t)
    db.commit()
    return RedirectResponse("/admin/tags", status_code=303)

@router.post("/tags/edit/{tag_id}")
def update_tag(request: Request,
               tag_id: int,
               name: str = Form(...),
               slug: str = Form(...),
               type: str = Form("dietary"),
               icon: str = Form(""),
               db: Session = Depends(get_db)):
    admin_required(request)
    
    tag = db.query(MenuTag).get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    tag.name = name.strip()
    tag.slug = slug.strip()
    tag.type = type
    tag.icon = icon.strip() or None
    
    db.commit()
    return RedirectResponse("/admin/tags", status_code=303)

@router.post("/tags/delete/{tag_id}")
def delete_tag(request: Request, tag_id: int, db: Session = Depends(get_db)):
    admin_required(request)
    
    tag = db.query(MenuTag).get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if tag is used by any items
    usage_count = db.query(MenuItemTag).filter(MenuItemTag.tag_id == tag_id).count()
    if usage_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete tag used by {usage_count} menu items")
    
    db.delete(tag)
    db.commit()
    return RedirectResponse("/admin/tags", status_code=303)

# Dedicated category management routes
@router.get("/categories", response_class=HTMLResponse)
def categories_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    
    categories = db.query(MenuCategory).order_by(MenuCategory.sort_order.asc(), MenuCategory.name.asc()).all()
    return request.app.templates.TemplateResponse(
        "admin/categories.html",
        ctx(request, categories=categories)
    )

@router.post("/categories/create")
def create_category_dedicated(request: Request,
                            name: str = Form(...),
                            slug: str = Form(...),
                            sort_order: int = Form(0),
                            db: Session = Depends(get_db)):
    admin_required(request)
    c = MenuCategory(name=name.strip(), slug=slug.strip(), sort_order=sort_order)
    db.add(c)
    db.commit()
    return RedirectResponse("/admin/categories", status_code=303)

@router.post("/categories/edit/{category_id}")
def update_category(request: Request,
                   category_id: int,
                   name: str = Form(...),
                   slug: str = Form(...),
                   sort_order: int = Form(0),
                   db: Session = Depends(get_db)):
    admin_required(request)
    
    category = db.query(MenuCategory).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.name = name.strip()
    category.slug = slug.strip()
    category.sort_order = sort_order
    
    db.commit()
    return RedirectResponse("/admin/categories", status_code=303)

@router.post("/categories/delete/{category_id}")
def delete_category(request: Request, category_id: int, db: Session = Depends(get_db)):
    admin_required(request)
    
    category = db.query(MenuCategory).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category is used by any items
    usage_count = db.query(MenuItem).filter(MenuItem.category_id == category_id).count()
    if usage_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete category used by {usage_count} menu items")
    
    db.delete(category)
    db.commit()
    return RedirectResponse("/admin/categories", status_code=303)
