from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

@router.get("", response_class=HTMLResponse)   # mounted at /admin
async def admin_home(request: Request):
    # If you don't have the template yet, just redirect to Menu Manager:
    return RedirectResponse("/admin/menu", status_code=303)
