"""The photographed menus, with a one-time import into the editable food catalog."""

import json
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Column, MetaData, String, Table, select, text
from sqlalchemy.orm import Session

from ..models.menu import MenuCategory, MenuItem

EDITION = json.loads((Path(__file__).resolve().parents[2] / "data/menu.json").read_text(encoding="utf-8"))
REVISION = "20261109-photographed-menu"
IMPORTS = Table("menu_imports", MetaData(), Column("revision", String(100), primary_key=True))


def import_menu_edition(db: Session) -> bool:
    """Update existing dishes by name, preserving photos, tags, and availability."""
    connection = db.connection()
    if connection.dialect.name == "postgresql":
        connection.execute(text("SELECT pg_advisory_xact_lock(606, 20261109)"))
    IMPORTS.create(connection, checkfirst=True)
    if db.scalar(select(IMPORTS.c.revision).where(IMPORTS.c.revision == REVISION)):
        return False

    categories = list(db.scalars(select(MenuCategory)))
    by_slug = {category.slug: category for category in categories}
    by_name = {category.name.casefold(): category for category in categories}
    items_by_name = {}
    for item in db.scalars(select(MenuItem).order_by(MenuItem.id)):
        items_by_name.setdefault(item.name.strip().casefold(), item)

    soda = next(section for section in EDITION["drinks"] if section["slug"] == "soft-drinks")
    sections = [
        *EDITION["food"],
        {
            "slug": "drinks",
            "title": "Drinks",
            "items": [{
                "name": soda["title"],
                "price": soda["price"],
                "description": ", ".join(soda["items"]) + ".",
            }],
        },
    ]
    for position, section in enumerate(sections):
        category = by_slug.get(section["slug"]) or by_name.get(section["title"].casefold())
        if category is None:
            category = MenuCategory(name=section["title"], slug=section["slug"], sort_order=position)
            db.add(category)
        for entry in section["items"]:
            candidates = [entry["name"], *entry.get("aliases", [])]
            item = next(
                (items_by_name[name.casefold()] for name in candidates if name.casefold() in items_by_name),
                None,
            )
            if item is None:
                item = MenuItem(available=True)
                db.add(item)
            item.name = entry["name"]
            item.price = Decimal(entry["price"])
            item.description = entry.get("description", "")
            item.category_rel = category
            item.category = section["slug"]

    db.execute(IMPORTS.insert().values(revision=REVISION))
    return True
