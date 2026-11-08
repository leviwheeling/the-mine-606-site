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

def event_times(start: str, end: str | None):
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end) if end else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Choose valid start and end times")
    if start_dt.tzinfo or (end_dt and end_dt.tzinfo):
        raise HTTPException(status_code=422, detail="Use Pikeville local times without a timezone")
    if end_dt and end_dt < start_dt:
        raise HTTPException(status_code=422, detail="End time must be after the start time")
    return start_dt, end_dt


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
    venue_area: str = Form("Deck"),
    ticket_url: str = Form(""),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
):
    admin_required(request)
    # Parse HTML datetime-local → ISO (no timezone)
    start_dt, end_dt = event_times(start, end)

    # Handle image upload
    image_url = ""
    if image and image.filename:
        image_url = await save_upload(image, subdir="events")

    e = Event(title=title.strip(), start=start_dt, end=end_dt, description=description or "", image_url=image_url, venue_area=venue_area, ticket_url=ticket_url, is_published=is_published)
    db.add(e)
    db.commit()
    return RedirectResponse("/admin/events?saved=1", status_code=status.HTTP_302_FOUND)

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
    return RedirectResponse("/admin/events?saved=1", status_code=status.HTTP_302_FOUND)

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
    venue_area: str = Form("Deck"),
    ticket_url: str = Form(""),
    is_published: bool = Form(False),
    db: Session = Depends(get_db),
):
    admin_required(request)
    event = db.query(Event).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    start_dt, end_dt = event_times(start, end)

    # Handle image replacement
    if image and image.filename:
        new_image_url = await save_upload(image, subdir="events")
        if new_image_url:
            old_image_url = event.image_url
            event.image_url = new_image_url
            if old_image_url:
                delete_media(old_image_url)

    # Update other fields
    event.title = title.strip()
    event.start = start_dt
    event.end = end_dt
    event.description = (description or "").strip() or None
    event.venue_area = venue_area.strip()
    event.ticket_url = ticket_url.strip()
    event.is_published = is_published

    db.commit()
    return RedirectResponse("/admin/events?saved=1", status_code=status.HTTP_302_FOUND)
