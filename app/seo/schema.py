# app/seo/schema.py
from typing import Dict, Any, List

def local_business(site: Any) -> Dict[str, Any]:
    name = getattr(site, "site_name", "The Mine 606")
    phone = getattr(site, "phone", "") or None
    address = " ".join(filter(None, [getattr(site,"address",""), getattr(site,"city",""), getattr(site,"state",""), getattr(site,"zip","")])) or None
    out = {
        "@context": "https://schema.org",
        "@type": "BarOrPub",
        "name": name,
        "slogan": "What's Mine is Yours",
        "image": "/assets/images/og-card.jpg",
        "url": "/",
    }
    if phone: out["telephone"] = phone
    if address: out["address"] = address
    lat = getattr(site, "lat", None); lng = getattr(site, "lng", None)
    if lat and lng:
        out["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
    return out

def events(events: List[Any]) -> List[Dict[str, Any]]:
    arr = []
    for e in events:
        arr.append({
            "@context": "https://schema.org",
            "@type": "Event",
            "name": getattr(e,"title",""),
            "startDate": getattr(e,"start",None).isoformat() if getattr(e,"start",None) else None,
            "endDate": getattr(e,"end",None).isoformat() if getattr(e,"end",None) else None,
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "image": getattr(e,"image_url","") or "/assets/images/placeholders/event.jpg",
            "description": getattr(e,"description","") or "",
            "location": {
                "@type": "Place",
                "name": getattr(e,"venue_area","Deck") or "Deck",
                "address": "Across from Appalachian Wireless Arena, Pikeville, KY"
            }
        })
    return arr
