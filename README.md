# The Mine 606

FastAPI / Jinja / SQLAlchemy website and staff admin for The Mine 606 in Pikeville, Kentucky. Production uses the existing Render service and PostgreSQL database.

## Day / Night redesign

The shared document theme covers all public pages, login, and admin. `data-mode` on the root sets a complete palette for every surface, input, card, table, navigation, and footer. The homepage also changes its photography and copy. The selection persists in local storage and syncs across tabs. The switch uses a document-wide circular View Transition with a fade fallback and respects reduced motion.

- Shared styling: `app/static/css/experience.css`
- Theme, navigation, filtering, forms, and photo interactions: `app/static/js/experience.js`
- Public shell: `app/templates/layout/base.html`
- Admin shell: `app/templates/admin/base.html`
- Optimized venue photographs: `app/static/media/venue/`

Menu items, prices, event dates, contact details, hours, and requests come from the existing database. No schema migration is required. Admin can manage event drafts/publication, ticket links, venue areas, featured menu positions, multiple tags, and hours. Settings changes invalidate the public cache immediately; other workers refresh within 30 seconds.

Public pages: `/`, `/menu`, `/events`, `/rentals`, `/musician`, `/location`, `/ordering`. Staff login: `/admin/login`.

The original DoorDash and Uber Eats buttons had no destination; the ordering page now points guests to the real menu and configured contact information. Merchandise and the Shopify embed have been removed; old `/shopify` links redirect home.

## Run locally with real development settings

Set `DATABASE_URL`, `SECRET_KEY`, and the admin login environment variables, then:

```sh
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Use a development database. The application's existing development startup behavior creates missing tables.

## Isolated design preview

```sh
python3 -m scripts.preview_redesign
```

Open `http://127.0.0.1:6062`. This command explicitly overrides the database with a disposable SQLite database and loads labeled sample data. It never connects to the production database. Local-only staff login: `preview` / `preview-local-only`. These credentials apply only when running the preview command, never the production app.

## Verification

```sh
python3 -m unittest discover -s tests -v
node --check app/static/js/experience.js
python3 -m compileall -q app scripts tests
```

Integration checks cover public/admin rendering and auth, menu CRUD with multiple tags, hidden items, event draft/publish/edit flows, submissions and statuses, categories/tags, and immediate settings/hour updates. Tests use disposable data. Install `httpx` (already in requirements) to run them.

Browser QA: public and admin pages checked at 320px and 390px, with responsive cards replacing mobile admin tables. Mode persistence, navigation, menu filters, photo dialogs, and a real local form submission were checked.

`mockups/` and `client-preview/` contain the earlier design explorations and are separate from the production application.
