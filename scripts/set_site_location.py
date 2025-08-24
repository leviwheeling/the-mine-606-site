# scripts/set_site_location.py
import os
import argparse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.site import SiteSetting

def upsert_site(address: str, lat: float, lng: float):
    db: Session = SessionLocal()
    try:
        s = db.query(SiteSetting).first()
        if not s:
            s = SiteSetting()
            db.add(s)
        s.address = address
        s.lat = lat
        s.lng = lng
        db.commit()
        print(f"✅ Saved site location:\n  address={s.address}\n  lat={s.lat}\n  lng={s.lng}")
    finally:
        db.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Set site address and coordinates")
    p.add_argument("--address", required=True, help='e.g. "121 Main St, Pikeville, KY"')
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lng", type=float, required=True)
    args = p.parse_args()
    upsert_site(args.address, args.lat, args.lng)
