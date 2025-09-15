# app/routers/admin/auth.py
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from ...security.auth import set_session, clear_session, admin_required, verify_password
from ...settings import get_settings

router = APIRouter()

def ctx(request: Request, **kw):
    base = {"request": request, "page_title": "Admin Login"}
    base.update(kw); return base

# ✅ Read from Settings (Pydantic loads .env here)
_settings = get_settings()
ADMIN_USER = _settings.admin_username or "admin"
ADMIN_HASH = _settings.admin_password_hash      # bcrypt hash (preferred)
TEMP_PLAIN = _settings.temp_admin_password      # dev fallback

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return request.app.templates.TemplateResponse("admin/login.html", ctx(request))

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    ok = False
    if ADMIN_HASH:
        ok = (username == ADMIN_USER) and verify_password(password, ADMIN_HASH)
    elif TEMP_PLAIN:
        ok = (username == ADMIN_USER) and (password == TEMP_PLAIN)
    if not ok:
        return request.app.templates.TemplateResponse(
            "admin/login.html", ctx(request, error="Invalid credentials"), status_code=400
        )
    resp = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    set_session(resp, username)
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    clear_session(resp)
    return resp


