# app/services/forms.py
from typing import Dict, Optional
import httpx
from ..settings import get_settings

settings = get_settings()

async def forward_to_formspree(kind: str, payload: Dict) -> Dict:
    """
    kind: 'musician' | 'rental' | 'contact'
    payload: flattened dict
    """
    endpoints = {
        "musician": settings.formspree.musician_endpoint,
        "rental": settings.formspree.rental_endpoint,
        "contact": settings.formspree.contact_endpoint,
    }
    url: Optional[str] = endpoints.get(kind)
    if not url:
        return {"ok": False, "reason": "Formspree endpoint not configured"}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, data=payload, headers={"Accept": "application/json"})
            if r.status_code in (200, 201, 202):
                return {"ok": True}
            return {"ok": False, "status": r.status_code, "body": r.text}
        except Exception as e:
            return {"ok": False, "reason": str(e)}
