# app/routers/public.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from zoneinfo import ZoneInfo

from ..db.session import get_db
from ..models.menu import MenuItem, MenuCategory
from ..models.events import Event
from ..models.site import SiteSetting
from ..seo.schema import local_business, events as events_schema
from ..services.menu_edition import EDITION

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

MENU_PAGES = {
    "food": {"url": "/menu", "label": "Food", "number": "01", "hero": "03"},
    "lunch": {"url": "/menu/lunch", "label": "$7 Lunch", "number": "02", "hero": "01"},
    "drinks": {"url": "/drinks", "label": "Drinks", "number": "03", "hero": "05"},
}


def render_menu(request: Request, menu_type: str, sections: list):
    page = MENU_PAGES[menu_type]
    tags = sorted({tag for section in sections for item in section["items"] for tag in item.get("tags", [])})
    return request.app.templates.TemplateResponse(
        "public/menu.html",
        ctx(
            request,
            menu_type=menu_type,
            menu_page=page,
            menu_pages=MENU_PAGES,
            sections=sections,
            tags=tags,
            item_count=sum(len(section["items"]) for section in sections),
            meta_desc=f"Explore {page['label'].lower()} at The Mine 606 in Pikeville, Kentucky.",
        ),
    )


@router.get("/menu", response_class=HTMLResponse)
async def menu(request: Request, db: Session = Depends(get_db)):
    items = (
        db.query(MenuItem)
        .options(joinedload(MenuItem.category_rel))
        .filter(MenuItem.available.is_(True))
        .order_by(MenuItem.name, MenuItem.id)
        .all()
    )
    edition_sections = {section["slug"]: section for section in EDITION["food"]}
    sections = {}
    for item in items:
        category = item.category_rel
        slug = (category.slug if category else item.category) or "other"
        if slug in {"drinks", "cocktails", "draft", "bottle-can", "shots", "liquor", "soft-drinks"}:
            continue
        entry = edition_sections.get(slug, {})
        section = sections.setdefault(slug, {
            **entry,
            "slug": slug,
            "title": entry.get("title", category.name if category else "More from the kitchen"),
            "items": [],
            "sort_order": category.sort_order if category else 0,
        })
        section["items"].append({
            "name": item.name,
            "description": item.description or "",
            "price": item.price,
            "image": item.image_url if item.image_url and "placeholder" not in item.image_url else None,
            "tags": [tag.slug for tag in item.tags],
        })

    order = {slug: index for index, slug in enumerate(edition_sections)}
    for slug, section in sections.items():
        if slug in edition_sections:
            item_order = {item["name"]: index for index, item in enumerate(edition_sections[slug]["items"])}
            section["items"].sort(key=lambda item: item_order.get(item["name"], len(item_order)))
    return render_menu(request, "food", sorted(sections.values(), key=lambda section: (
        order.get(section["slug"], len(order)), section["sort_order"] or 0, section["title"],
    )))


@router.get("/menu/lunch", response_class=HTMLResponse)
async def lunch_menu(request: Request):
    descriptions = {
        item["name"]: item.get("description", "")
        for section in EDITION["food"]
        for item in section["items"]
    }
    sections = [
        {**section, "items": [{"name": name, "description": descriptions[name]} for name in section["items"]]}
        for section in EDITION["lunch"]
    ]
    return render_menu(request, "lunch", sections)


@router.get("/drinks", response_class=HTMLResponse)
async def drinks_menu(request: Request, db: Session = Depends(get_db)):
    sections = [
        {
            **section,
            "items": [
                {"name": name, "description": section.get("descriptions", {}).get(name, "")}
                for name in section["items"]
            ],
        }
        for section in EDITION["drinks"]
    ]
    soft_drinks = sections[-1]
    extras = (
        db.query(MenuItem)
        .join(MenuItem.category_rel)
        .filter(MenuCategory.slug == "drinks", MenuItem.available.is_(True))
        .order_by(MenuItem.name)
        .all()
    )
    for item in extras:
        if item.name == soft_drinks["title"]:
            soft_drinks["price"] = item.price
        else:
            soft_drinks["items"].append({
                "name": item.name,
                "price": item.price,
                "description": item.description,
            })
    return render_menu(request, "drinks", sections)


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    return request.app.templates.TemplateResponse(
        "public/privacy.html", ctx(request, meta_desc="How The Mine 606 handles information submitted through this website.")
    )


@router.get("/terms", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    return request.app.templates.TemplateResponse(
        "public/terms.html", ctx(request, meta_desc="Terms of use for The Mine 606 website.")
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
