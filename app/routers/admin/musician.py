# app/routers/admin/musician.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.musician import MusicianApp
from ...security.auth import admin_required

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request}
    base.update(kw); return base

@router.get("/musician", response_class=HTMLResponse)
def musician_list(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    apps = (
        db.query(MusicianApp)
        .order_by(MusicianApp.submitted_at.desc())
        .limit(200)
        .all()
    )
    return request.app.templates.TemplateResponse("admin/musician.html", ctx(request, apps=apps))

@router.post("/musician/status")
def musician_status(request: Request, id: int = Form(...), status: str = Form(...), db: Session = Depends(get_db)):
    admin_required(request)
    row = db.query(MusicianApp).get(id)
    if row:
        row.status = status
        db.commit()
    return RedirectResponse("/admin/musician", status_code=303)
