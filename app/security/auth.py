# app/security/auth.py
import secrets
from datetime import timedelta, datetime
from typing import Optional
from fastapi import HTTPException, status, Request, Response, Depends
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from ..settings import get_settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

def _serializer():
    s = URLSafeTimedSerializer(get_settings().secret_key, salt="mine606-session")
    return s

SESSION_COOKIE = "mine606_admin"
SESSION_AGE = 60 * 60 * 8  # 8 hours

def set_session(resp: Response, username: str):
    settings = get_settings()
    token = _serializer().dumps({"u": username, "t": datetime.utcnow().isoformat()})
    resp.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_AGE,
        httponly=True,
        secure=(settings.environment.lower() == "production"),  # only secure in prod
        samesite="lax",
        path="/",
    )

def clear_session(resp: Response):
    resp.delete_cookie(SESSION_COOKIE, path="/")

def get_current_admin(request: Request) -> Optional[str]:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        data = _serializer().loads(token, max_age=SESSION_AGE)
        return data.get("u")
    except (BadSignature, SignatureExpired):
        return None

def admin_required(request: Request):
    user = get_current_admin(request)
    if not user:
        # redirect to login
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )
    return user
