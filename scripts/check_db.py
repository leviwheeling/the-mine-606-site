# scripts/check_db.py
import os
import sys
from sqlalchemy import create_engine, text

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.settings import get_settings

settings = get_settings()

def check_db():
    print(f"📦 Connecting to: {settings.database_url}")
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        print("\n--- MENU CATEGORIES ---")
        cats = conn.execute(text("SELECT id, name, slug FROM menu_categories ORDER BY id")).fetchall()
        if cats:
            for row in cats:
                print(row)
        else:
            print("⚠️ No categories found.")

        print("\n--- MENU TAGS ---")
        tags = conn.execute(text("SELECT id, name, slug FROM menu_tags ORDER BY id")).fetchall()
        if tags:
            for row in tags:
                print(row)
        else:
            print("⚠️ No tags found.")

        print("\n--- MENU ITEMS ---")
        items = conn.execute(text("SELECT id, name, price, category_id, description FROM menu_items ORDER BY id")).fetchall()
        if items:
            for row in items:
                print(row)
        else:
            print("⚠️ No items found.")

if __name__ == "__main__":
    check_db()
