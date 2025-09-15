# app/routers/admin/rentals.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.rentals import Rental
from ...security.auth import admin_required
from ...settings import get_settings

router = APIRouter()
settings = get_settings()

def ctx(request: Request, **kw):
    base = {
        "request": request,
        "page_title": "Venue Rentals",
        "user": request.cookies.get("mine606_admin")
    }
    base.update(kw)
    return base

@router.get("/rentals", response_class=HTMLResponse)
async def rentals_list(request: Request, db: Session = Depends(get_db)):
    # Ensure user is authenticated
    admin_required(request)
    
    # Get rentals with sorting and basic filtering
    query = db.query(Rental).order_by(Rental.date.desc())
    
    # Get filter parameters
    status = request.query_params.get("status")
    area = request.query_params.get("area")
    
    if status and status != "all":
        query = query.filter(Rental.status == status)
    if area and area != "all":
        query = query.filter(Rental.venue_area == area)
    
    # Get rentals
    rentals = query.limit(200).all()
    
    # Get unique areas for filter dropdown
    areas = db.query(Rental.venue_area).distinct().all()
    areas = [a[0] for a in areas if a[0]]  # Remove None values
    
    return request.app.templates.TemplateResponse(
        "admin/rentals.html",
        ctx(
            request,
            rows=rentals,
            areas=areas,
            active_status=status or "all",
            active_area=area or "all"
        )
    )

@router.post("/rentals/status")
async def update_status(
    request: Request,
    id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    # Ensure user is authenticated
    admin_required(request)
    
    # Validate status
    valid_statuses = ["new", "pending", "approved", "closed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update rental status
    rental = db.query(Rental).filter(Rental.id == id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    rental.status = status
    db.commit()
    
    # Redirect back to rentals page
    return RedirectResponse(
        url="/admin/rentals",
        status_code=303
    )