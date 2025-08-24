# app/routers/admin/rentals.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.rentals import Rental
from ...security.auth import admin_required

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request}
    base.update(kw); return base

@router.get("/rentals", response_class=HTMLResponse)
def rentals_list(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    rows = db.query(Rental).order_by(Rental.date.desc()).limit(200).all()
    return request.app.templates.TemplateResponse("admin/rentals.html", ctx(request, rows=rows))

@router.post("/rentals/status")
def rentals_status(request: Request, id: int = Form(...), status: str = Form(...), db: Session = Depends(get_db)):
    admin_required(request)
    row = db.query(Rental).get(id)
    if row:
        row.status = status
        db.commit()
    return RedirectResponse("/admin/rentals", status_code=303)
