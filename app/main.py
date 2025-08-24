# app/main.py
from __future__ import annotations

import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .settings import get_settings

# --- NEW: DB imports for dev-only table creation ---
from .db.base import Base
from .db.session import engine, SessionLocal
from .models.site import Hours, SiteSetting
# Import models so SQLAlchemy knows about them before create_all()
from .models import user, menu, events, reviews, musician, rentals, site  # noqa: F401



settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ---------- Static & Templates ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
ASSETS_DIR = os.path.join(os.path.dirname(BASE_DIR), "assets")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.templates = templates
# Serve /static (app-bundled JS/CSS/uploads) and /assets (brand images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# ---------- Middleware ----------
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# gzip responses for speed
app.add_middleware(GZipMiddleware, minimum_size=1024)

# ---------- Template globals ----------
def template_globals(request: Request) -> dict:
    """Values available in all templates."""
    from .services.cache import get_cached_hours, get_cached_site_settings
    return {
        "request": request,
        "APP_NAME": settings.app_name,
        "ENV": settings.environment,
        "CURRENT_YEAR": datetime.now().year,
        # Feature flags / keys (None is fine—templates should guard)
        "GOOGLE_MAPS_API_KEY": settings.google_maps_api_key,
        # Cached values
        "HOURS_HTML": get_cached_hours(),
        "SITE_OBJ": get_cached_site_settings(),
    }

templates.env.globals.update(template_globals=template_globals)

# ---------- Routers (mounted if present) ----------
def _safe_include(prefix: str, router_path: str, router_name: str) -> None:
    """
    Attempt to import and include a router. If the file isn't created yet,
    skip without crashing so we can boot the skeleton.
    """
    try:
        module = __import__(router_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router, prefix=prefix)
    except Exception as e:
        # In debug you can print/log e; in prod we keep quiet
        if settings.debug:
            print(f"[router-skip] {router_path}:{router_name} -> {e}")

def _build_hours_html():
    try:
        db = SessionLocal()
        rows = db.query(Hours).all()
        if not rows:
            return None
        order = ['mon','tue','wed','thu','fri','sat','sun']
        by = {r.dow: r for r in rows}
        parts = []
        for dow in order:
            r = by.get(dow)
            if not r: continue
            label = {'mon':'Mon','tue':'Tue','wed':'Wed','thu':'Thu','fri':'Fri','sat':'Sat','sun':'Sun'}[dow]
            if r.closed:
                parts.append(f"<div>{label}: Closed</div>")
            else:
                open_ = r.open or '—'
                close_ = r.close or '—'
                parts.append(f"<div>{label}: {open_}–{close_}</div>")
        return "".join(parts) if parts else None
    except Exception:
        return None
    finally:
        try:
            db.close()
        except Exception:
            pass

def _get_site_settings():
    try:
        db = SessionLocal()
        site = db.query(SiteSetting).first()
        return site
    except Exception:
        return None
    finally:
        try:
            db.close()
        except Exception:
            pass




# public pages (/)
_safe_include("", "app.routers.public", "router")
# JSON APIs (/api/*)
_safe_include("/api", "app.routers.api.menu", "router")
_safe_include("/api", "app.routers.api.events", "router")
_safe_include("/api", "app.routers.api.uploads", "router")
_safe_include("/api", "app.routers.api.forms", "router")
_safe_include("/api", "app.routers.api.weather", "router")
_safe_include("/api", "app.routers.api.uploads", "router")
# admin (/admin/*)
_safe_include("/admin", "app.routers.admin.auth", "router")
_safe_include("/admin", "app.routers.admin.dashboard", "router")
_safe_include("/admin", "app.routers.admin.menu", "router")
_safe_include("/admin", "app.routers.admin.events", "router")
_safe_include("/admin", "app.routers.admin.musician", "router")
_safe_include("/admin", "app.routers.admin.rentals", "router")
_safe_include("/admin", "app.routers.admin.site", "router")
_safe_include("/admin", "app.routers.admin.reviews", "router")

# ---------- Basic pages & utilities ----------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    from .models.events import Event
    from .models.menu import MenuItem
    from .services.cache import get_cached_site_settings
    from datetime import datetime
    
    events = []
    featured = []
    
    try:
        db = SessionLocal()
        # Use a single transaction for all queries
        now = datetime.utcnow()
        
        # Combine queries using join where possible
        results = db.execute("""
            SELECT 
                'event' as type,
                e.id,
                e.title,
                e.description,
                e.start,
                e.end,
                NULL as price,
                NULL as featured_rank,
                NULL as available
            FROM event e
            WHERE e.start >= :now
                AND e.is_published = true
            ORDER BY e.start ASC
            LIMIT 3
            
            UNION ALL
            
            SELECT 
                'menu' as type,
                m.id,
                m.name as title,
                m.description,
                NULL as start,
                NULL as end,
                m.price,
                m.featured_rank,
                m.available
            FROM menu_item m
            WHERE m.featured_rank > 0
                AND m.available = true
            ORDER BY m.featured_rank ASC
            LIMIT 9
        """, {"now": now})
        
        # Process results
        for row in results:
            if row.type == 'event':
                events.append({
                    'id': row.id,
                    'title': row.title,
                    'description': row.description,
                    'start': row.start,
                    'end': row.end
                })
            elif row.type == 'menu':
                featured.append({
                    'id': row.id,
                    'name': row.title,
                    'description': row.description,
                    'price': row.price,
                    'featured_rank': row.featured_rank
                })
                
    except Exception as e:
        if settings.debug:
            print(f"Error in home route: {e}")
        events = []
        featured = []
    finally:
        try:
            db.close()
        except Exception:
            pass
    
    # Renders templates/public/home.html with events, featured, and site data
    context = template_globals(request)
    context["events"] = events
    context["featured"] = featured
    context["site"] = site
    return templates.TemplateResponse("public/home.html", context)

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz() -> str:
    return "ok"

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots() -> str:
    # Allow indexing, point to sitemap
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap(request: Request) -> Response:
    """
    Minimal dynamic sitemap. We’ll expand this later if you want per-item URLs.
    """
    base = str(request.base_url).rstrip("/")
    urls: List[str] = [
        f"{base}/",
        f"{base}/menu",
        f"{base}/ordering",
        f"{base}/shopify",
        f"{base}/musician",
        f"{base}/rentals",
        f"{base}/reviews",
        f"{base}/location",
    ]
    lastmod = datetime.utcnow().strftime("%Y-%m-%d")
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        body += [
            "  <url>",
            f"    <loc>{u}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            "    <changefreq>weekly</changefreq>",
            "    <priority>0.8</priority>",
            "  </url>",
        ]
    body += ["</urlset>"]
    return Response("\n".join(body), media_type="application/xml")

# ---------- Error handlers ----------
@app.exception_handler(404)
async def not_found(request: Request, exc):
    # Render a friendly 404 if template exists; fallback to text otherwise
    template_path = os.path.join(TEMPLATES_DIR, "public", "404.html")
    if os.path.isfile(template_path):
        return templates.TemplateResponse(
            "public/404.html", template_globals(request), status_code=status.HTTP_404_NOT_FOUND
        )
    return PlainTextResponse("Not Found", status_code=status.HTTP_404_NOT_FOUND)

# ---------- Dev-only table creation ----------
@app.on_event("startup")
async def startup_event():
    if settings.environment and settings.environment.lower() == "development":
        print("[DEV MODE] Creating database tables if not present...")
        Base.metadata.create_all(bind=engine)
