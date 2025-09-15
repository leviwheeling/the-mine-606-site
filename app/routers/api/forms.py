# app/routers/api/forms.py (updated)
from fastapi import APIRouter, Form, UploadFile, File, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.musician import MusicianApp
from ...models.rentals import Rental
from datetime import datetime

router = APIRouter()

@router.post("/musician")
async def musician_submit(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    presskit: Optional[UploadFile] = File(None),  # reserved
):
    # save to DB
    row = MusicianApp(
        name=name.strip(), email=email.strip(),
        phone=(phone or "").strip(), genre=(genre or "").strip(),
        link=(link or "").strip(), message=(message or "").strip() or None,
        submitted_at=datetime.utcnow(), status="new"
    )
    db.add(row); db.commit(); db.refresh(row)

    # Successfully saved to database
    return JSONResponse({"success": True, "id": row.id, "message": "Musician application submitted successfully"}, status_code=200)

@router.post("/rental")
async def rental_submit(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    event_date: Optional[str] = Form(None),  # Support both field names
    party_size: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
):
    # save to DB - use whichever date field was provided
    date_str = date or event_date
    dt = None
    try:
        if date_str: dt = datetime.fromisoformat(date_str)
    except Exception:
        dt = None
    
    row = Rental(
        name=name.strip(), email=email.strip(),
        phone=(phone or "").strip(), party_size=(party_size or "").strip(),
        date=dt or datetime.utcnow(),
        message=(message or "").strip() or None,
        submitted_at=datetime.utcnow(),  # Add this missing field
        status="new"
    )
    db.add(row); db.commit(); db.refresh(row)

    # Successfully saved to database
    return JSONResponse({"success": True, "id": row.id, "message": "Venue rental request submitted successfully"}, status_code=200)

@router.post("/contact")
async def contact_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
):
    # For now, just return success since there's no contact model
    # You might want to add a Contact model later or handle this differently
    return JSONResponse({"success": True, "message": "Contact message received"}, status_code=200)
