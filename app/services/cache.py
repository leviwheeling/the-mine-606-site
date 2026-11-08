"""Short-lived public settings snapshots; admin saves invalidate immediately."""
from datetime import datetime
from functools import lru_cache
from html import escape
from time import time
from zoneinfo import ZoneInfo

from ..db.session import SessionLocal
from ..models.site import Hours, SiteSetting, HolidayOverride


def convert_to_12hour(value):
    if not value:
        return '—'
    try:
        hour, minute = map(int, value.split(':'))
        return f"{hour % 12 or 12}:{minute:02d}{'am' if hour < 12 else 'pm'}"
    except (ValueError, AttributeError):
        return value


def get_cached_hours():
    return _hours(int(time() // 30))


@lru_cache(maxsize=2)
def _hours(bucket):
    with SessionLocal() as db:
        rows = {r.dow: r for r in db.query(Hours).all()}
        parts = []
        today = datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d')
        override = db.query(HolidayOverride).filter(HolidayOverride.date == today).first()
        def formatted(row):
            return 'Closed' if row.closed else escape(f'{convert_to_12hour(row.open)}–{convert_to_12hour(row.close)}')
        if override:
            parts.append(f'<div><strong>Today: {formatted(override)}</strong></div>')
        for dow, label in [('mon','Mon'),('tue','Tue'),('wed','Wed'),('thu','Thu'),('fri','Fri'),('sat','Sat'),('sun','Sun')]:
            if dow in rows:
                parts.append(f'<div>{label}: {formatted(rows[dow])}</div>')
        return ''.join(parts) or None


def get_cached_site_settings():
    return _site(int(time() // 30))


@lru_cache(maxsize=2)
def _site(bucket):
    with SessionLocal() as db:
        row = db.query(SiteSetting).first()
        return {col.name: getattr(row, col.name) for col in SiteSetting.__table__.columns} if row else None


def clear_caches():
    _hours.cache_clear()
    _site.cache_clear()
