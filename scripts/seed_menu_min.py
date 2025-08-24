# scripts/seed_menu_min.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env if present
load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL not set in environment or .env file")

engine = create_engine(db_url, future=True)

SQL = """
-- Ensure base categories exist
INSERT INTO menu_categories (name, slug, sort_order)
SELECT * FROM (VALUES
  ('Starters','starters',1),
  ('Entrees','entrees',2),
  ('Drinks','drinks',3),
  ('Cocktails','cocktails',4)
) AS v(name,slug,sort_order)
WHERE NOT EXISTS (SELECT 1 FROM menu_categories);

-- Fried Pickles
INSERT INTO menu_items (name, category, price, image_url, description, available, featured_rank, category_id)
SELECT 'Fried Pickles', 'Starters', 8.50, '/assets/images/placeholders/dish-1.jpg',
       'Crispy spears with house ranch.', TRUE, 1, c.id
FROM menu_categories c
WHERE c.slug='starters'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Fried Pickles');

-- Braveheart Burger
INSERT INTO menu_items (name, category, price, image_url, description, available, featured_rank, category_id)
SELECT 'Braveheart Burger', 'Entrees', 14.00, '/assets/images/placeholders/dish-2.jpg',
       'Half-pound smash, cheddar, secret sauce.', TRUE, 2, c.id
FROM menu_categories c
WHERE c.slug='entrees'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Braveheart Burger');

-- 12" Pizza
INSERT INTO menu_items (name, category, price, image_url, description, available, featured_rank, category_id)
SELECT '12" Pizza', 'Entrees', 12.00, '/assets/images/placeholders/dish-3.jpg',
       'Hand-tossed, classic red.', TRUE, 3, c.id
FROM menu_categories c
WHERE c.slug='entrees'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='12" Pizza');

-- Margarita
INSERT INTO menu_items (name, category, price, image_url, description, available, featured_rank, category_id)
SELECT 'Margarita', 'Cocktails', 9.00, '/assets/images/placeholders/event.jpg',
       'Tequila, lime, salt.', TRUE, 0, c.id
FROM menu_categories c
WHERE c.slug='cocktails'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Margarita');
"""

def main():
    print(f"[SEED] Using {db_url}")
    with engine.begin() as conn:
        for chunk in [s for s in SQL.split(";") if s.strip()]:
            conn.execute(text(chunk))
    print("✅ Seeded minimal menu.")

if __name__ == "__main__":
    main()
