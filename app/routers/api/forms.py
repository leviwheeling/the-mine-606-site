# app/routers/api/forms.py (updated)
from fastapi import APIRouter, Form, UploadFile, File, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from ...services.forms import forward_to_formspree
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

    payload = {
        "name": name, "email": email, "phone": phone or "",
        "genre": genre or "", "link": link or "", "message": message or "",
        "_subject": "New Musician Application — The Mine 606",
        "_replyto": email,
    }
    result = await forward_to_formspree("musician", payload)
    ok = bool(result.get("ok"))
    return JSONResponse({"success": ok, "id": row.id, "detail": result}, status_code=200 if ok else 502)

@router.post("/rental")
async def rental_submit(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    party_size: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
):
    # save to DB
    dt = None
    try:
        if date: dt = datetime.fromisoformat(date)
    except Exception:
        dt = None
    row = Rental(
        name=name.strip(), email=email.strip(),
        phone=(phone or "").strip(), party_size=(party_size or "").strip(),
        date=dt or datetime.utcnow(),
        message=(message or "").strip() or None,
        status="new"
    )
    db.add(row); db.commit(); db.refresh(row)

    payload = {
        "name": name, "email": email, "phone": phone or "",
        "date": date or "", "party_size": party_size or "", "message": message or "",
        "_subject": "New Venue Inquiry — The Mine 606",
        "_replyto": email,
    }
    result = await forward_to_formspree("rental", payload)
    ok = bool(result.get("ok"))
    return JSONResponse({"success": ok, "id": row.id, "detail": result}, status_code=200 if ok else 502)

@router.post("/contact")
async def contact_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
):
    payload = {
        "name": name, "email": email, "message": message,
        "_subject": "New Contact Message — The Mine 606",
        "_replyto": email,
    }
    result = await forward_to_formspree("contact", payload)
    ok = bool(result.get("ok"))
    return JSONResponse({"success": ok, "detail": result}, status_code=200 if ok else 502)
