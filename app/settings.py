# app/settings.py
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    app_name: str = "The Mine 606"
    environment: str = "development"
    debug: bool = True

    # Security
    secret_key: str = "dev-not-secret-change-me"   # <-- add this

    # DB (required)
    database_url: str  # maps to DATABASE_URL

    # CORS
    cors_origins: List[str] = ["*"]  # accepts JSON list string in .env

    # Admin auth (env-based simple login)
    admin_username: str = "admin"          # ADMIN_USERNAME
    admin_password_hash: Optional[str] = None  # ADMIN_PASSWORD_HASH (preferred in prod)
    temp_admin_password: Optional[str] = None  # TEMP_ADMIN_PASSWORD (dev convenience)

    # External keys (optional)
    google_maps_api_key: Optional[str] = None     # GOOGLE_MAPS_API_KEY
    openweather_api_key: Optional[str] = None     # OPENWEATHER_API_KEY
    google_places_api_key: Optional[str] = None   # GOOGLE_PLACES_API_KEY
    yelp_api_key: Optional[str] = None            # YELP_API_KEY
    facebook_graph_token: Optional[str] = None    # FACEBOOK_GRAPH_TOKEN
    
    # Cloudinary (for image uploads)
    cloudinary_cloud_name: Optional[str] = None   # CLOUDINARY_CLOUD_NAME
    cloudinary_api_key: Optional[str] = None      # CLOUDINARY_API_KEY
    cloudinary_api_secret: Optional[str] = None   # CLOUDINARY_API_SECRET

    # Formspree endpoints (optional)
    formspree_musician_endpoint: Optional[str] = None  # FORMSPREE_MUSICIAN_ENDPOINT
    formspree_rental_endpoint: Optional[str] = None    # FORMSPREE_RENTAL_ENDPOINT
    formspree_contact_endpoint: Optional[str] = None   # FORMSPREE_CONTACT_ENDPOINT

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",           # use exact env names given above
        case_sensitive=False,    # DATABASE_URL == database_url, etc.
        extra="ignore",          # ignore unknown env keys rather than erroring
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
