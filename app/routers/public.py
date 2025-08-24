# app/routers/public.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import os
import json

from ..db.session import get_db
from ..models.menu import MenuItem, MenuCategory, MenuTag
from ..models.events import Event
from ..models.site import SiteSetting
from ..seo.schema import local_business, events as events_schema

router = APIRouter()

def ctx(request: Request, **kw):
    base = {
        "request": request,
        "page_title": "The Mine 606",
        "meta_desc": "Modern rustic bar & kitchen across from Appalachian Wireless Arena.",
    }
    base.update(kw)
    return base

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    featured = (
        db.query(MenuItem)
        .filter(MenuItem.featured_rank > 0, MenuItem.available == True)  # noqa: E712
        .order_by(MenuItem.featured_rank.asc()).limit(3).all()
    )
    events = (
        db.query(Event)
        .filter(Event.is_published == True, Event.start >= datetime.utcnow())  # noqa: E712
        .order_by(Event.start.asc()).limit(3).all()
    )
    site = db.query(SiteSetting).first()
    lb = json.dumps(local_business(site or SiteSetting()), ensure_ascii=False)
    ev = json.dumps(events_schema(events), ensure_ascii=False)

    return request.app.templates.TemplateResponse(
        "public/home.html",
        ctx(request, featured=featured, events=events, site=site, jsonld_local=lb, jsonld_events=ev)
    )

@router.get("/menu", response_class=HTMLResponse)
async def menu(request: Request, db: Session = Depends(get_db)):
    categories = db.query(MenuCategory).order_by(MenuCategory.sort_order.asc(), MenuCategory.name.asc()).all()
    tags = db.query(MenuTag).order_by(MenuTag.type.asc(), MenuTag.name.asc()).all()
    items = db.query(MenuItem).options(joinedload(MenuItem.tags)).order_by(MenuItem.name.asc()).all()

    cat_payload = [{"id": c.slug or str(c.id), "name": c.name} for c in categories]
    tag_payload = [t.slug for t in tags]
    item_payload = []
    for it in items:
        # use slug for category if present
        cat_slug = next((c.slug for c in categories if c.id == getattr(it, "category_id", None)), getattr(it, "category", "other"))
        item_payload.append({
            "id": it.id,
            "name": it.name,
            "price": float(it.price),
            "category": cat_slug or "other",
            "tags": [t.slug for t in (getattr(it, "tags", []) or [])],
            "img": it.image_url or "/assets/images/placeholders/dish-1.jpg",
        })

    return request.app.templates.TemplateResponse(
        "public/menu.html",
        ctx(request, categories=cat_payload, tags=tag_payload, items=item_payload)
    )

@router.get("/ordering", response_class=HTMLResponse)
async def ordering(request: Request):
    return request.app.templates.TemplateResponse("public/ordering.html", ctx(request))

@router.get("/shopify", response_class=HTMLResponse)
async def shopify(request: Request):
    return request.app.templates.TemplateResponse("public/shopify.html", ctx(request))

@router.get("/musician", response_class=HTMLResponse)
async def musician(request: Request):
    return request.app.templates.TemplateResponse("public/musician.html", ctx(request))

@router.get("/rentals", response_class=HTMLResponse)
async def rentals(request: Request):
    return request.app.templates.TemplateResponse("public/rentals.html", ctx(request))

@router.get("/reviews", response_class=HTMLResponse)
async def reviews(request: Request, db: Session = Depends(get_db)):
    from ..models.reviews import Review
    featured = db.query(Review).filter(Review.is_featured == True).order_by(Review.id.desc()).all()  # noqa: E712
    others   = db.query(Review).filter(Review.is_featured == False).order_by(Review.id.desc()).limit(30).all()  # noqa: E712
    return request.app.templates.TemplateResponse(
        "public/reviews.html", ctx(request, featured=featured, others=others)
    )

@router.get("/location", response_class=HTMLResponse)
async def location(request: Request, db: Session = Depends(get_db)):
    site = db.query(SiteSetting).first()
    return request.app.templates.TemplateResponse("public/location.html", ctx(request, site=site))
