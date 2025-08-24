# scripts/seed_dev.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models import menu, events, site, reviews, user  # register models
from app.models.menu import MenuCategory, MenuTag, MenuItem, MenuItemTag
from app.models.events import Event
from app.models.site import SiteSetting, Hours
from passlib.context import CryptContext
import os

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def ensure_tables():
    Base.metadata.create_all(bind=engine)

def seed_site(db: Session):
    s = db.query(SiteSetting).first()
    if not s:
        s = SiteSetting(
            site_name="The Mine 606",
            hero_title="What’s Mine is Yours",
            hero_sub="Across from Appalachian Wireless Arena.",
            phone="(555) 555-0606",
            email="mine606@example.com",
            address="123 Main St",
            city="Pikeville",
            state="KY",
            zip="41501",
            lat=37.479, lng=-82.518,  # rough Pikeville coords
            facebook="", instagram="", tiktok="", youtube=""
        )
        db.add(s)
    # hours (Mon–Sun)
    if db.query(Hours).count() == 0:
        hours = [
            ("mon", "", "", True),
            ("tue", "11:00", "22:00", False),
            ("wed", "11:00", "22:00", False),
            ("thu", "11:00", "22:00", False),
            ("fri", "11:00", "24:00", False),
            ("sat", "11:00", "24:00", False),
            ("sun", "11:00", "21:00", False),
        ]
        for dow, o, c, closed in hours:
            db.add(Hours(dow=dow, open=o, close=c, closed=closed))

def seed_menu(db: Session):
    if db.query(MenuCategory).count() == 0:
        starters = MenuCategory(name="Starters", slug="starters", sort_order=1)
        entrees  = MenuCategory(name="Entrees", slug="entrees", sort_order=2)
        drinks   = MenuCategory(name="Drinks", slug="drinks", sort_order=3)
        cocktails= MenuCategory(name="Cocktails", slug="cocktails", sort_order=4)
        db.add_all([starters, entrees, drinks, cocktails])
        db.flush()

        tags = [
            MenuTag(name="vegetarian", slug="vegetarian", type="dietary"),
            MenuTag(name="vegan", slug="vegan", type="dietary"),
            MenuTag(name="gluten-free", slug="gluten-free", type="dietary"),
            MenuTag(name="dairy-free", slug="dairy-free", type="dietary"),
            MenuTag(name="spicy", slug="spicy", type="spice"),
        ]
        db.add_all(tags); db.flush()

        items = [
            MenuItem(name="Fried Pickles", price=8.50, category_id=starters.id,
                     description="Crispy spears with house ranch.",
                     image_url="/assets/images/placeholders/dish-1.jpg", available=True, featured_rank=1),
            MenuItem(name="Braveheart Burger", price=14.00, category_id=entrees.id,
                     description="Half-pound smash, cheddar, secret sauce.",
                     image_url="/assets/images/placeholders/dish-2.jpg", available=True, featured_rank=2),
            MenuItem(name="12\" Pizza", price=12.00, category_id=entrees.id,
                     description="Hand-tossed, classic red.",
                     image_url="/assets/images/placeholders/dish-3.jpg", available=True, featured_rank=3),
            MenuItem(name="Margarita", price=9.00, category_id=cocktails.id,
                     description="Tequila, lime, salt.",
                     image_url="/assets/images/placeholders/event.jpg", available=True),
        ]
        db.add_all(items); db.flush()

        # tag Fried Pickles veg + dairy-free
        fp = items[0]
        veg = db.query(MenuTag).filter_by(slug="vegetarian").first()
        df  = db.query(MenuTag).filter_by(slug="dairy-free").first()
        db.add_all([MenuItemTag(item_id=fp.id, tag_id=veg.id), MenuItemTag(item_id=fp.id, tag_id=df.id)])

def seed_events(db: Session):
    if db.query(Event).count() == 0:
        now = datetime.utcnow()
        evs = [
            Event(title="Live Band Night", start=now + timedelta(days=2, hours=3),
                  description="Local favorites on the deck.", image_url="/assets/images/placeholders/event.jpg", venue_area="Deck"),
            Event(title="Trivia Thursday", start=now + timedelta(days=5, hours=2),
                  description="Win tabs & swag!", image_url="/assets/images/placeholders/event.jpg", venue_area="Indoors"),
            Event(title="Acoustic Sunday", start=now + timedelta(days=7, hours=1),
                  description="Chill vibes, good food.", image_url="/assets/images/placeholders/event.jpg", venue_area="Deck"),
        ]
        db.add_all(evs)

def main():
    ensure_tables()
    db = SessionLocal()
    try:
        seed_site(db)
        seed_menu(db)
        seed_events(db)
        # optional: create admin user row if you plan to store later (we use env-based login now)
        db.commit()
        print("Seed complete.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
