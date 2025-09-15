# app/services/media.py
"""
Media upload service with cloud storage support.
Now uses Cloudinary for better performance and automatic optimization.
"""

import os, uuid
from typing import Tuple, Optional
from datetime import datetime
from fastapi import UploadFile
from .cloud_storage import upload_image, delete_image, get_storage_info

# Legacy local storage support (kept for backwards compatibility)
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "media")
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}

def ensure_media_root():
    """Ensure local media directory exists (legacy support)."""
    os.makedirs(MEDIA_ROOT, exist_ok=True)

def save_upload(filename: str, content_type: str, data: bytes) -> Tuple[bool, str]:
    """
    Legacy function for backwards compatibility.
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

async def save_upload(file: UploadFile, subdir: str = "uploads") -> Optional[str]:
    """
    Upload file to cloud storage (Cloudinary) with local fallback.
    
    Args:
        file: The uploaded file
        subdir: Subdirectory/folder name (e.g., "menu", "events")
        
    Returns:
        URL of uploaded image or None if failed
    """
    if not file or not file.filename:
        return None
    
    # Use cloud storage service
    image_url = await upload_image(file, folder=subdir)
    
    if image_url:
        return image_url
    
    # If cloud upload fails, fall back to legacy local storage
    return await _save_upload_local_fallback(file, subdir)

async def _save_upload_local_fallback(file: UploadFile, subdir: str = "uploads") -> Optional[str]:
    """
    Legacy local storage fallback.
    Saves an uploaded file to /app/static/media/<subdir>/yyyy/mm/filename
    Returns a URL path like /static/media/<subdir>/yyyy/mm/filename
    """
    try:
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

        # Reset file position in case it was read before
        await file.seek(0)
        
        # write
        with open(dest, "wb") as out:
            out.write(await file.read())

        return f"/static/media/{rel_dir}/{os.path.basename(dest)}"
    except Exception as e:
        print(f"Local upload fallback error: {e}")
        return None

def delete_media(image_url: str) -> bool:
    """
    Delete an uploaded image from cloud or local storage.
    
    Args:
        image_url: The image URL to delete
        
    Returns:
        True if successful, False otherwise
    """
    return delete_image(image_url)

def get_media_info() -> dict:
    """Get information about current media storage configuration."""
    info = get_storage_info()
    info["legacy_local_path"] = MEDIA_ROOT
    return info
