# app/services/cloud_storage.py
"""
Cloud storage service for handling image uploads.
Supports Cloudinary with fallback to local storage.
"""

import os
import uuid
from typing import Optional
from fastapi import UploadFile
import cloudinary
import cloudinary.uploader
from ..settings import get_settings

settings = get_settings()

# Configure Cloudinary if credentials are available
if all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    CLOUDINARY_ENABLED = True
else:
    CLOUDINARY_ENABLED = False

async def upload_image(
    file: UploadFile, 
    folder: str = "menu",
    max_width: int = 800,
    quality: str = "auto"
) -> Optional[str]:
    """
    Upload an image to Cloudinary or fallback to local storage.
    
    Args:
        file: The uploaded file
        folder: Cloudinary folder (e.g., "menu", "events")
        max_width: Maximum width for optimization
        quality: Image quality ("auto", "best", etc.)
        
    Returns:
        URL of the uploaded image or None if failed
    """
    if not file or not file.filename:
        return None
    
    try:
        # Read file content
        file_content = await file.read()
        
        if CLOUDINARY_ENABLED:
            # Upload to Cloudinary with optimization
            result = cloudinary.uploader.upload(
                file_content,
                folder=f"mine606/{folder}",
                public_id=f"{uuid.uuid4().hex}_{file.filename.split('.')[0]}",
                transformation=[
                    {"width": max_width, "crop": "limit"},
                    {"quality": quality, "fetch_format": "auto"}
                ],
                allowed_formats=["jpg", "jpeg", "png", "webp"],
                max_file_size=5000000  # 5MB limit
            )
            return result.get("secure_url")
        else:
            # Fallback to local storage
            return await _save_local(file, file_content, folder)
            
    except Exception as e:
        print(f"Image upload error: {e}")
        # Try local fallback even if Cloudinary fails
        if CLOUDINARY_ENABLED:
            try:
                return await _save_local(file, file_content, folder)
            except Exception:
                pass
        return None

async def _save_local(file: UploadFile, content: bytes, folder: str) -> str:
    """Fallback local storage implementation."""
    # Create directory structure
    base_dir = os.path.dirname(os.path.dirname(__file__))  # app/
    media_dir = os.path.join(base_dir, "static", "media", folder)
    
    from datetime import datetime
    year_month = datetime.now().strftime("%Y/%m")
    full_dir = os.path.join(media_dir, year_month)
    os.makedirs(full_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(full_dir, unique_name)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return URL path
    return f"/static/media/{folder}/{year_month}/{unique_name}"

def delete_image(image_url: str) -> bool:
    """
    Delete an image from Cloudinary or local storage.
    
    Args:
        image_url: The image URL to delete
        
    Returns:
        True if successful, False otherwise
    """
    if not image_url:
        return False
    
    try:
        if CLOUDINARY_ENABLED and "cloudinary.com" in image_url:
            # Extract public_id from Cloudinary URL
            # URL format: https://res.cloudinary.com/cloud/image/upload/v123/folder/public_id.ext
            parts = image_url.split("/")
            if len(parts) >= 7:
                # Get everything after upload/ and remove file extension
                public_id_with_folder = "/".join(parts[7:])
                public_id = os.path.splitext(public_id_with_folder)[0]
                
                result = cloudinary.uploader.destroy(public_id)
                return result.get("result") == "ok"
        else:
            # Local file deletion
            if image_url.startswith("/static/"):
                base_dir = os.path.dirname(os.path.dirname(__file__))
                file_path = os.path.join(base_dir, image_url[1:])  # Remove leading /
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
    except Exception as e:
        print(f"Image deletion error: {e}")
    
    return False

def get_storage_info() -> dict:
    """Get information about the current storage configuration."""
    return {
        "cloudinary_enabled": CLOUDINARY_ENABLED,
        "cloud_name": settings.cloudinary_cloud_name if CLOUDINARY_ENABLED else None,
        "storage_type": "Cloudinary" if CLOUDINARY_ENABLED else "Local"
    }
