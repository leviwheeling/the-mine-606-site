from sqlalchemy import text
from app.db.session import engine

SQL = """
ALTER TABLE rentals
  ADD COLUMN IF NOT EXISTS venue_area VARCHAR(80) DEFAULT 'Deck';
"""

def main():
    print("[DB PATCH] Adding venue_area column to rentals table...")
    with engine.begin() as conn:
        conn.execute(text(SQL))
    print("[DB PATCH] Done.")

if __name__ == "__main__":
    main()
