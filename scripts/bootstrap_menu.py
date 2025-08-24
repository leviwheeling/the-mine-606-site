# scripts/bootstrap_menu.py
import os, sys
from sqlalchemy import create_engine, text

# Allow "python scripts/bootstrap_menu.py" to import app if needed later
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# --- DATABASE URL ---
# Prefer the app settings if available; otherwise use env var.
db_url = os.getenv("DATABASE_URL")
if not db_url:
    try:
        from app.settings import get_settings
        db_url = get_settings().database_url
    except Exception:
        pass
if not db_url:
    raise SystemExit("DATABASE_URL not set. Put it in .env or export it in your shell.")

engine = create_engine(db_url, future=True)

PATCH_SQL = """
-- === MENU schema upgrades ===
CREATE TABLE IF NOT EXISTS menu_categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE,
  sort_order INTEGER NOT NULL DEFAULT 0
);

ALTER TABLE menu_items
  ADD COLUMN IF NOT EXISTS description TEXT,
  ADD COLUMN IF NOT EXISTS available BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS featured_rank INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS category_id INTEGER;

ALTER TABLE menu_items
  ALTER COLUMN available SET NOT NULL,
  ALTER COLUMN featured_rank SET NOT NULL;

-- Backfill categories from legacy string column if present
INSERT INTO menu_categories (name, slug, sort_order)
SELECT DISTINCT category,
       LOWER(REGEXP_REPLACE(category, '[^a-z0-9]+', '-', 'g')),
       0
FROM menu_items
WHERE category IS NOT NULL AND category <> ''
ON CONFLICT (slug) DO NOTHING;

UPDATE menu_items m
SET category_id = c.id
FROM menu_categories c
WHERE m.category_id IS NULL
  AND LOWER(REGEXP_REPLACE(m.category, '[^a-z0-9]+', '-', 'g')) = c.slug;

-- === Optional extra fields used elsewhere (safe to run repeatedly) ===
ALTER TABLE events
  ADD COLUMN IF NOT EXISTS venue_area VARCHAR(100),
  ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS ticket_url VARCHAR(200);
ALTER TABLE events
  ALTER COLUMN is_published SET NOT NULL;

ALTER TABLE reviews
  ADD COLUMN IF NOT EXISTS rating INTEGER,
  ADD COLUMN IF NOT EXISTS reviewer_name VARCHAR(100),
  ADD COLUMN IF NOT EXISTS reviewer_avatar VARCHAR(300),
  ADD COLUMN IF NOT EXISTS url VARCHAR(300),
  ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;

ALTER TABLE musician_applications
  ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
  ADD COLUMN IF NOT EXISTS genre VARCHAR(100),
  ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'new';

ALTER TABLE rentals
  ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
  ADD COLUMN IF NOT EXISTS party_size VARCHAR(20),
  ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'new';
"""

SEED_SQL = """
-- Seed categories if empty
INSERT INTO menu_categories (name, slug, sort_order)
SELECT * FROM (VALUES
  ('Starters','starters',1),
  ('Entrees','entrees',2),
  ('Drinks','drinks',3),
  ('Cocktails','cocktails',4)
) AS v(name,slug,sort_order)
WHERE NOT EXISTS (SELECT 1 FROM menu_categories);

-- Minimal items (idempotent-ish via name check)
INSERT INTO menu_items (name, price, image_url, description, available, featured_rank, category_id)
SELECT 'Fried Pickles', 8.50, '/assets/images/placeholders/dish-1.jpg', 'Crispy spears with house ranch.', TRUE, 1, c.id
FROM menu_categories c WHERE c.slug='starters'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Fried Pickles');

INSERT INTO menu_items (name, price, image_url, description, available, featured_rank, category_id)
SELECT 'Braveheart Burger', 14.00, '/assets/images/placeholders/dish-2.jpg', 'Half-pound smash, cheddar, secret sauce.', TRUE, 2, c.id
FROM menu_categories c WHERE c.slug='entrees'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Braveheart Burger');

INSERT INTO menu_items (name, price, image_url, description, available, featured_rank, category_id)
SELECT '12" Pizza', 12.00, '/assets/images/placeholders/dish-3.jpg', 'Hand-tossed, classic red.', TRUE, 3, c.id
FROM menu_categories c WHERE c.slug='entrees'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='12" Pizza');

INSERT INTO menu_items (name, price, image_url, description, available, featured_rank, category_id)
SELECT 'Margarita', 9.00, '/assets/images/placeholders/event.jpg', 'Tequila, lime, salt.', TRUE, 0, c.id
FROM menu_categories c WHERE c.slug='cocktails'
  AND NOT EXISTS (SELECT 1 FROM menu_items WHERE name='Margarita');
"""

def run_sql(sql: str):
    chunks = [s for s in sql.split(";") if s.strip()]
    with engine.begin() as conn:
        for q in chunks:
            conn.execute(text(q))

if __name__ == "__main__":
    print(f"[BOOTSTRAP] Using {db_url}")
    print("[1/2] Patching schema…")
    run_sql(PATCH_SQL)
    print("[2/2] Seeding sample menu data…")
    run_sql(SEED_SQL)
    print("✅ Done. Visit /menu")
