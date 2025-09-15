from fastapi import APIRouter, Request, Form, status, Depends, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from ...db.session import get_db
from ...models.events import Event
from ...security.auth import admin_required
from ...services.media import save_upload, delete_media
import os

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request, "page_title": "Admin • Events"}
    base.update(kw)
    return base

@router.get("/events", response_class=HTMLResponse)
def events_page(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    events = db.query(Event).order_by(Event.start.desc()).all()
    return request.app.templates.TemplateResponse("admin/events.html", ctx(request, events=events))

@router.post("/events/create")
async def create_event(
    request: Request,
    title: str = Form(...),
    start: str = Form(...),  # datetime-local
    end: str | None = Form(None),  # datetime-local
    description: str | None = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    admin_required(request)
    # Parse HTML datetime-local → ISO (no timezone)
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end) if end else None

    # Handle image upload
    image_url = ""
    if image and image.filename:
        image_url = await save_upload(image, subdir="events")

    e = Event(title=title, start=start_dt, end=end_dt, description=description or "", image_url=image_url)
    db.add(e)
    db.commit()
    return RedirectResponse("/admin/events", status_code=status.HTTP_302_FOUND)

@router.post("/events/delete")
def delete_event(
    request: Request,
    event_id: int = Form(...),
    db: Session = Depends(get_db),
):
    admin_required(request)
    e = db.get(Event, event_id)
    if e:
        # Clean up associated image file (both local and cloud)
        if e.image_url:
            delete_media(e.image_url)
        db.delete(e)
        db.commit()
    return RedirectResponse("/admin/events", status_code=status.HTTP_302_FOUND)

@router.get("/events/edit/{event_id}", response_class=HTMLResponse)
def edit_event_form(request: Request, event_id: int, db: Session = Depends(get_db)):
    admin_required(request)
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return request.app.templates.TemplateResponse("admin/events_edit.html", ctx(request, event=event))

@router.post("/events/edit/{event_id}")
async def update_event(
    request: Request,
    event_id: int,
    title: str = Form(...),
    start: str = Form(...),
    end: str | None = Form(None),
    description: str | None = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    admin_required(request)
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Handle image replacement
    if image and image.filename:
        # Clean up old image file (both local and cloud)
        if event.image_url:
            delete_media(event.image_url)
        # Save new image
        new_image_url = await save_upload(image, subdir="events")
        event.image_url = new_image_url
    
    # Update other fields
    event.title = title.strip()
    event.start = datetime.fromisoformat(start)
    event.end = datetime.fromisoformat(end) if end else None
    event.description = (description or "").strip() or None
    
    db.commit()
    return RedirectResponse("/admin/events", status_code=status.HTTP_302_FOUND)
