from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.site import SiteSetting, Hours, HolidayOverride
from ...security.auth import admin_required

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request}
    base.update(kw); return base

def _get_singleton_settings(db: Session) -> SiteSetting:
    s = db.query(SiteSetting).first()
    if not s:
        s = SiteSetting()
        db.add(s); db.commit(); db.refresh(s)
    return s

@router.get("/site", response_class=HTMLResponse)
def site_settings(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    s = _get_singleton_settings(db)
    hours = db.query(Hours).order_by(Hours.id.asc()).all()
    holidays = db.query(HolidayOverride).order_by(HolidayOverride.date.asc()).all()
    return request.app.templates.TemplateResponse(
        "admin/site.html", ctx(request, s=s, hours=hours, holidays=holidays)
    )

@router.post("/site/basic")
def update_basic(
    request: Request,
    site_name: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip: str = Form(None),
    hero_title: str = Form(None),
    hero_sub: str = Form(None),
    show_weather: str = Form(None),
    facebook: str = Form(None),
    instagram: str = Form(None),
    tiktok: str = Form(None),
    youtube: str = Form(None),
    db: Session = Depends(get_db),
):
    admin_required(request)
    s = _get_singleton_settings(db)
    s.site_name = site_name or s.site_name
    s.phone = phone or ""
    s.email = email or ""
    s.address = address or ""
    s.city = city or ""
    s.state = state or ""
    s.zip = zip or ""
    s.hero_title = hero_title or s.hero_title
    s.hero_sub = hero_sub or s.hero_sub
    s.show_weather = bool(show_weather)  # checkbox
    s.facebook = facebook or ""
    s.instagram = instagram or ""
    s.tiktok = tiktok or ""
    s.youtube = youtube or ""
    db.commit()
    return RedirectResponse("/admin/site", status_code=303)

@router.post("/site/hours")
def set_hours(
    request: Request,
    dow: str = Form(...), open: str = Form(""), close: str = Form(""), closed: str = Form(""),
    db: Session = Depends(get_db),
):
    admin_required(request)
    row = db.query(Hours).filter(Hours.dow==dow).first()
    if not row:
        row = Hours(dow=dow)
        db.add(row)
    row.open = open
    row.close = close
    row.closed = bool(closed)
    db.commit()
    return RedirectResponse("/admin/site", status_code=303)

@router.post("/site/holiday")
def set_holiday(
    request: Request,
    date: str = Form(...), open: str = Form(""), close: str = Form(""), closed: str = Form(""),
    db: Session = Depends(get_db),
):
    admin_required(request)
    row = db.query(HolidayOverride).filter(HolidayOverride.date==date).first()
    if not row:
        row = HolidayOverride(date=date)
        db.add(row)
    row.open = open
    row.close = close
    row.closed = bool(closed)
    db.commit()
    return RedirectResponse("/admin/site", status_code=303)

@router.post("/site/holiday/delete")
def delete_holiday(request: Request, date: str = Form(...), db: Session = Depends(get_db)):
    admin_required(request)
    row = db.query(HolidayOverride).filter(HolidayOverride.date==date).first()
    if row:
        db.delete(row); db.commit()
    return RedirectResponse("/admin/site", status_code=303)
