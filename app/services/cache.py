from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from ..db.session import SessionLocal
from ..models.site import Hours, SiteSetting

def convert_to_12hour(time_str: str) -> str:
    """Convert 24-hour format time to 12-hour format with am/pm"""
    if not time_str or time_str == '—':
        return time_str
    
    try:
        # Parse the time string (e.g., "11:00" or "22:00")
        hour, minute = map(int, time_str.split(':'))
        
        # Convert to 12-hour format
        if hour == 0:
            return f"12:{minute:02d}am"
        elif hour < 12:
            return f"{hour}:{minute:02d}am"
        elif hour == 12:
            return f"12:{minute:02d}pm"
        else:
            return f"{hour - 12}:{minute:02d}pm"
    except (ValueError, AttributeError):
        return time_str

@lru_cache(maxsize=1)
def get_cached_hours() -> Optional[str]:
    """Cache hours HTML for 1 hour since it rarely changes"""
    try:
        db = SessionLocal()
        rows = db.query(Hours).all()
        if not rows:
            return None
        order = ['mon','tue','wed','thu','fri','sat','sun']
        by = {r.dow: r for r in rows}
        parts = []
        for dow in order:
            r = by.get(dow)
            if not r: continue
            label = {'mon':'Mon','tue':'Tue','wed':'Wed','thu':'Thu','fri':'Fri','sat':'Sat','sun':'Sun'}[dow]
            if r.closed:
                parts.append(f"<div>{label}: Closed</div>")
            else:
                open_ = convert_to_12hour(r.open) if r.open else '—'
                close_ = convert_to_12hour(r.close) if r.close else '—'
                parts.append(f"<div>{label}: {open_}–{close_}</div>")
        return "".join(parts) if parts else None
    except Exception:
        return None
    finally:
        db.close()

@lru_cache(maxsize=1)
def get_cached_site_settings() -> Optional[Dict[str, Any]]:
    """Cache site settings for 1 hour since they rarely change"""
    try:
        db = SessionLocal()
        site = db.query(SiteSetting).first()
        if site:
            # Convert to dict to avoid SQLAlchemy object serialization issues
            return {
                'id': site.id,
                'name': site.name,
                'tagline': site.tagline,
                'description': site.description,
                'address': site.address,
                'phone': site.phone,
                'email': site.email,
                'facebook': site.facebook,
                'instagram': site.instagram,
                'twitter': site.twitter,
                'created_at': site.created_at.isoformat() if site.created_at else None,
                'updated_at': site.updated_at.isoformat() if site.updated_at else None
            }
        return None
    except Exception:
        return None
    finally:
        db.close()

def clear_caches() -> None:
    """Clear all cached data - call this when data is updated"""
    get_cached_hours.cache_clear()
    get_cached_site_settings.cache_clear()
