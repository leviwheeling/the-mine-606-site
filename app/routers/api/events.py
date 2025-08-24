# app/routers/api/events.py
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from ...db.session import get_db
from ...models.events import Event

router = APIRouter(tags=["Events"])

def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None

@router.get("/events/data")
def events_data(
    start: str = Query(..., description="ISO date from FullCalendar"),
    end: str   = Query(..., description="ISO date from FullCalendar"),
    db: Session = Depends(get_db),
):
    # Parse ISO strings coming from FullCalendar
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", ""))
        end_dt   = datetime.fromisoformat(end.replace("Z", ""))
    except Exception:
        return JSONResponse({"ok": False, "error": "bad_range"}, status_code=400)

    q = (
        db.query(Event)
          .filter(Event.start <= end_dt)
          .filter((Event.end == None) | (Event.end >= start_dt))
          .order_by(Event.start.asc())
    )
    return [
        {
            "id": e.id,
            "title": e.title,
            "start": _iso(e.start),
            "end": _iso(e.end),
            "description": e.description or "",
        }
        for e in q.all()
    ]

# Keep existing endpoints if they exist
@router.get("/events")
def get_events(db: Session = Depends(get_db)):
    """Get all upcoming events for display on public pages."""
    events = (
        db.query(Event)
        .filter(Event.start >= datetime.now())
        .order_by(Event.start.asc())
        .limit(6)
        .all()
    )
    return events
