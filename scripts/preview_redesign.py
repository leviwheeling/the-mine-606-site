"""Run an isolated design preview with sample data, never the production database.

Usage: python3 -m scripts.preview_redesign
"""
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Use a disposable SQLite database even if the shell has DATABASE_URL configured.
preview_dir = Path(tempfile.mkdtemp(prefix='mine606-preview-'))
os.environ['DATABASE_URL'] = f'sqlite:///{preview_dir / "preview.sqlite"}'
os.environ['ENVIRONMENT'] = 'testing'
os.environ['DEBUG'] = 'false'
os.environ['SECRET_KEY'] = 'local-isolated-design-preview'
os.environ['ADMIN_USERNAME'] = 'preview'
os.environ['ADMIN_PASSWORD_HASH'] = ''
os.environ['TEMP_ADMIN_PASSWORD'] = 'preview-local-only'

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, 'sqlite')
def jsonb_for_preview(type_, compiler, **kw):
    return 'JSON'

from app.main import app
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.menu import MenuCategory, MenuItem, MenuTag, MenuItemTag
from app.models.events import Event
from app.models.site import SiteSetting, Hours
from app.models.rentals import Rental
from app.models.musician import MusicianApp


def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add(SiteSetting(site_name='The Mine 606', address='121 Main St', city='Pikeville', state='KY', zip='41501', hero_title='', hero_sub=''))
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            db.add(Hours(dow=day, open='11:00', close='23:00', closed=day=='mon'))
        categories = [MenuCategory(name=n, slug=s, sort_order=i) for i,(n,s) in enumerate([('Burgers','burgers'),('Pizza','pizza'),('Sandwiches','sandwiches'),('Shareables','shareables')])]
        db.add_all(categories)
        tags=[MenuTag(name='Vegetarian',slug='vegetarian'),MenuTag(name='Spicy',slug='spicy',type='spice')]
        db.add_all(tags);db.flush()
        for i,(name,price,cat,image,description) in enumerate([('Sample Burger',12,0,'03','Sample menu item for design preview.'),('Sample Pizza',15,1,'04','Sample menu item for design preview.'),('Sample Club',11,2,'01','Sample menu item for design preview.'),('Sample Shareable',7,3,'02','Sample menu item for design preview.')]):
            item=MenuItem(name=name,price=price,category_id=categories[cat].id,image_url=f'/static/media/venue/{image}.webp',description=description,featured_rank=i+1 if i<3 else 0,available=True)
            db.add(item);db.flush()
            if i==3:
                for tag in tags:db.add(MenuItemTag(item_id=item.id,tag_id=tag.id))
        now=datetime.now(ZoneInfo('America/New_York')).replace(tzinfo=None)
        db.add(Event(title='Sample Weekend Event',start=now+timedelta(days=5),description='Illustrative event for local design review only.',image_url='/static/media/venue/14.webp',venue_area='Indoors',is_published=True))
        db.add(Rental(name='Sample Party Request',email='sample@example.com',date=now+timedelta(days=10),party_size='25',message='Local preview inquiry. This is sample data.',venue_area='Deck',status='new'))
        db.add(MusicianApp(name='Sample Artist',email='artist@example.com',genre='Acoustic',message='Local preview application.',status='new'))
        db.commit()


if __name__ == '__main__':
    import uvicorn
    seed()
    print('Isolated preview: http://127.0.0.1:6062')
    print('Local staff preview: preview / preview-local-only')
    uvicorn.run(app, host='127.0.0.1', port=6062)
