# scripts/patch_db.py
from sqlalchemy import text
from app.db.session import engine

SQL = """
-- === MENU ===
ALTER TABLE menu_items
  ADD COLUMN IF NOT EXISTS description TEXT,
  ADD COLUMN IF NOT EXISTS available BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS featured_rank INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS category_id INTEGER;

ALTER TABLE menu_items
  ALTER COLUMN available SET NOT NULL,
  ALTER COLUMN featured_rank SET NOT NULL;

CREATE TABLE IF NOT EXISTS menu_categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE,
  sort_order INTEGER NOT NULL DEFAULT 0
);

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

-- === EVENTS ===
ALTER TABLE events
  ADD COLUMN IF NOT EXISTS venue_area VARCHAR(100),
  ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS ticket_url VARCHAR(200);

ALTER TABLE events
  ALTER COLUMN is_published SET NOT NULL;

-- === REVIEWS (optional but used by admin UI) ===
ALTER TABLE reviews
  ADD COLUMN IF NOT EXISTS rating INTEGER,
  ADD COLUMN IF NOT EXISTS reviewer_name VARCHAR(100),
  ADD COLUMN IF NOT EXISTS reviewer_avatar VARCHAR(300),
  ADD COLUMN IF NOT EXISTS url VARCHAR(300),
  ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;

-- === MUSICIAN APPLICATIONS (optional fields) ===
ALTER TABLE musician_applications
  ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
  ADD COLUMN IF NOT EXISTS genre VARCHAR(100),
  ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'new';

-- === RENTALS (optional fields) ===
ALTER TABLE rentals
  ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
  ADD COLUMN IF NOT EXISTS party_size VARCHAR(20),
  ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'new';
"""

def main():
    print("[DB PATCH] Applying schema changes...")
    with engine.begin() as conn:
        for chunk in [s for s in SQL.split(";") if s.strip()]:
            conn.execute(text(chunk))
    print("[DB PATCH] Done.")

if __name__ == "__main__":
    main()
