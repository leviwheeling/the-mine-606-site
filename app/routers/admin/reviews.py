# app/routers/admin/reviews.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.reviews import Review
from ...security.auth import admin_required

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request}
    base.update(kw); return base

@router.get("/reviews", response_class=HTMLResponse)
def reviews_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    featured = db.query(Review).filter(Review.is_featured == True).order_by(Review.id.desc()).all()  # noqa: E712
    others   = db.query(Review).filter(Review.is_featured == False).order_by(Review.id.desc()).limit(200).all()  # noqa: E712
    return request.app.templates.TemplateResponse(
        "admin/reviews.html", ctx(request, featured=featured, others=others)
    )

@router.post("/reviews/create")
def create_review(
    request: Request,
    source: str = Form(...),           # yelp|google|facebook|manual
    rating: int = Form(5),
    text: str = Form(""),
    url: str = Form(""),
    reviewer_name: str = Form(""),
    reviewer_avatar: str = Form(""),
    embed_code: str = Form(""),
    is_featured: bool = Form(False),
    db: Session = Depends(get_db),
):
    admin_required(request)
    r = Review(
        source=source.strip(), rating=rating, text=text.strip() or None,
        url=url.strip(), reviewer_name=reviewer_name.strip(), reviewer_avatar=reviewer_avatar.strip(),
        embed_code=embed_code.strip() or None, is_featured=is_featured
    )
    db.add(r); db.commit()
    return RedirectResponse("/admin/reviews", status_code=303)

@router.post("/reviews/feature")
def feature_review(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    admin_required(request)
    row = db.query(Review).get(id)
    if row:
        row.is_featured = not bool(row.is_featured)
        db.commit()
    return RedirectResponse("/admin/reviews", status_code=303)

@router.post("/reviews/delete")
def delete_review(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    admin_required(request)
    row = db.query(Review).get(id)
    if row:
        db.delete(row); db.commit()
    return RedirectResponse("/admin/reviews", status_code=303)
