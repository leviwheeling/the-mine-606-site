# app/services/media.py
import os, uuid
from typing import Tuple
from datetime import datetime
from fastapi import UploadFile

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "media")
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}

def ensure_media_root():
    os.makedirs(MEDIA_ROOT, exist_ok=True)

def save_upload(filename: str, content_type: str, data: bytes) -> Tuple[bool, str]:
    """
    Returns (ok, public_url_or_error).
    """
    ensure_media_root()
    ext = ALLOWED.get(content_type)
    if not ext:
        return False, "Unsupported file type"
    key = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(MEDIA_ROOT, key)
    with open(path, "wb") as f:
        f.write(data)
    # public URL served by /static mount
    return True, f"/static/media/{key}"

async def save_upload(file: UploadFile, subdir: str = "uploads") -> str:
    """
    Saves an uploaded file to /app/static/media/<subdir>/yyyy/mm/filename
    Returns a URL path like /static/media/<subdir>/yyyy/mm/filename
    """
    # ensure dirs
    now = datetime.utcnow()
    rel_dir = os.path.join(subdir, str(now.year), f"{now.month:02d}")
    abs_dir = os.path.join(MEDIA_ROOT, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)

    # make safe-ish filename
    name = os.path.basename(file.filename or "upload.bin").replace(" ", "_")
    dest = os.path.join(abs_dir, name)
    # avoid clobber
    base, ext = os.path.splitext(name)
    i = 1
    while os.path.exists(dest):
        dest = os.path.join(abs_dir, f"{base}_{i}{ext}")
        i += 1

    # write
    with open(dest, "wb") as out:
        out.write(await file.read())

    return f"/static/media/{rel_dir}/{os.path.basename(dest)}"
