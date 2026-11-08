# app/routers/public.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json

from ..db.session import get_db
from ..models.menu import MenuItem, MenuCategory, MenuTag
from ..models.events import Event
from ..models.site import SiteSetting
from ..seo.schema import local_business, events as events_schema

router = APIRouter()

def ctx(request: Request, **kw):
    from ..services.cache import get_cached_hours, get_cached_site_settings
    from ..settings import get_settings
    from datetime import datetime

    settings = get_settings()

    base = {
        "request": request,
        "page_title": "The Mine 606",
        "meta_desc": "Modern rustic bar & kitchen across from Appalachian Wireless Arena.",
        # Template globals
        "APP_NAME": settings.app_name,
        "ENV": settings.environment,
        "CURRENT_YEAR": datetime.now().year,
        "GOOGLE_MAPS_API_KEY": settings.google_maps_api_key,
        "HOURS_HTML": get_cached_hours(),
        "SITE_OBJ": get_cached_site_settings(),
    }
    base.update(kw)
    return base

def get_template_name(base_name: str, request: Request) -> str:
    """Use one consistent document shell for direct and legacy HTMX requests."""
    return f"public/{base_name}"

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    featured = (
        db.query(MenuItem)
        .filter(MenuItem.featured_rank > 0, MenuItem.available == True)  # noqa: E712
        .order_by(MenuItem.featured_rank.asc()).limit(6).all()
    )
    events = (
        db.query(Event)
        .filter(Event.is_published == True, Event.start >= datetime.now(ZoneInfo('America/New_York')).replace(tzinfo=None))  # noqa: E712
        .order_by(Event.start.asc()).limit(3).all()
    )
    site = db.query(SiteSetting).first()
    lb = local_business(site or SiteSetting())
    ev = events_schema(events)

    return request.app.templates.TemplateResponse(
        get_template_name("home.html", request),
        ctx(request, featured=featured, events=events, site=site, jsonld_local=lb, jsonld_events=ev)
    )

@router.get("/menu", response_class=HTMLResponse)
async def menu(request: Request, db: Session = Depends(get_db)):
    categories = db.query(MenuCategory).order_by(MenuCategory.sort_order.asc(), MenuCategory.name.asc()).all()
    tags = db.query(MenuTag).order_by(MenuTag.type.asc(), MenuTag.name.asc()).all()
    items = db.query(MenuItem).options(joinedload(MenuItem.tags)).filter(MenuItem.available.is_(True)).order_by(MenuItem.name.asc()).all()

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
            "img": it.image_url or "/static/media/menu/placeholder.svg",
            "description": it.description or "",
        })

    return request.app.templates.TemplateResponse(
        get_template_name("menu.html", request),
        ctx(request, categories=cat_payload, tags=tag_payload, items=item_payload)
    )

@router.get("/ordering", response_class=HTMLResponse)
async def ordering(request: Request):
    return request.app.templates.TemplateResponse(get_template_name("ordering.html", request), ctx(request))

@router.get("/shopify", include_in_schema=False)
async def former_shop():
    return RedirectResponse("/", status_code=301)

@router.get("/musician", response_class=HTMLResponse)
async def musician(request: Request):
    return request.app.templates.TemplateResponse(get_template_name("musician.html", request), ctx(request))

@router.get("/rentals", response_class=HTMLResponse)
async def rentals(request: Request):
    return request.app.templates.TemplateResponse(get_template_name("rentals.html", request), ctx(request))

@router.get("/location", response_class=HTMLResponse)
async def location(request: Request, db: Session = Depends(get_db)):
    site = db.query(SiteSetting).first()
    return request.app.templates.TemplateResponse(get_template_name("location.html", request), ctx(request, site=site))


@router.get("/events", response_class=HTMLResponse)
async def event_list(request: Request, db: Session = Depends(get_db)):
    now = datetime.now(ZoneInfo("America/New_York")).replace(tzinfo=None)
    events = db.query(Event).filter(Event.is_published.is_(True), Event.start >= now).order_by(Event.start.asc()).all()
    return request.app.templates.TemplateResponse("public/events.html", ctx(request, events=events))
