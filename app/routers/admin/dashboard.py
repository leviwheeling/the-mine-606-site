from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.rentals import Rental
from ...models.menu import MenuItem
from ...models.events import Event
from ...security.auth import admin_required

router = APIRouter()

def ctx(request: Request, **kw):
    base = {
        "request": request,
        "page_title": "Admin Dashboard",
        "user": request.cookies.get("mine606_admin")
    }
    base.update(kw)
    return base

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    
    # Get dashboard stats
    try:
        # Count new rentals
        new_rentals = db.query(Rental).filter(Rental.status == "new").count()
        total_rentals = db.query(Rental).count()
        
        # Count menu items
        total_menu_items = db.query(MenuItem).count()
        featured_items = db.query(MenuItem).filter(MenuItem.featured_rank > 0).count()
        
        # Count events
        total_events = db.query(Event).count()
        
        stats = {
            'new_rentals': new_rentals,
            'total_rentals': total_rentals,
            'total_menu_items': total_menu_items,
            'featured_items': featured_items,
            'total_events': total_events
        }
    except Exception:
        stats = {
            'new_rentals': 0,
            'total_rentals': 0,
            'total_menu_items': 0,
            'featured_items': 0,
            'total_events': 0
        }
    
    return request.app.templates.TemplateResponse(
        "admin/dashboard.html",
        ctx(request, stats=stats)
    )
