"""Integration checks using a disposable database, never production data."""
import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from scripts.preview_redesign import app, seed, Base, engine, SessionLocal
from app.models.menu import MenuItem, MenuCategory, MenuTag, MenuItemTag
from app.models.events import Event
from app.models.rentals import Rental
from app.models.musician import MusicianApp
from app.services.cache import clear_caches


class RedesignTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(engine)
        seed()
        clear_caches()
        self.client = TestClient(app)

    def login(self):
        response=self.client.post('/admin/login',data={'username':'preview','password':'preview-local-only'},follow_redirects=False)
        self.assertEqual(response.status_code,303)

    def test_public_pages_and_admin_auth(self):
        for path in ['/','/menu','/events','/rentals','/musician','/location','/ordering']:
            with self.subTest(path=path):
                response=self.client.get(path)
                self.assertEqual(response.status_code,200)
                self.assertIn('data-mood-switch',response.text)
                self.assertIn('experience.js',response.text)
                self.assertNotIn('cdn.tailwindcss',response.text)
        self.assertEqual(self.client.get('/missing-page').status_code,404)
        self.assertEqual(self.client.get('/shopify',follow_redirects=False).status_code,301)
        self.assertNotIn('The shop',self.client.get('/').text)
        for path in ['/admin','/admin/menu','/admin/events','/admin/rentals','/admin/musician','/admin/site','/admin/categories','/admin/tags']:
            self.assertEqual(self.client.get(path,follow_redirects=False).status_code,303)
        self.assertEqual(self.client.post('/admin/login',data={'username':'preview','password':'wrong'}).status_code,400)
        self.login()
        for path in ['/admin','/admin/menu','/admin/events','/admin/rentals','/admin/musician','/admin/site','/admin/categories','/admin/tags','/admin/menu/edit/1','/admin/events/edit/1']:
            with self.subTest(admin=path):
                response=self.client.get(path)
                self.assertEqual(response.status_code,200)
                self.assertIn('THE CONTROL ROOM',response.text)
        self.client.get('/admin/logout')
        self.assertEqual(self.client.get('/admin',follow_redirects=False).status_code,303)

    def test_hidden_menu_and_draft_events_stay_private(self):
        with SessionLocal() as db:
            db.add(MenuItem(name='Hidden dish',price=10,available=False,featured_rank=1))
            db.add(Event(title='Secret draft',start=datetime.now()+timedelta(days=2),is_published=False))
            db.commit()
        self.assertNotIn('Hidden dish',self.client.get('/menu').text)
        self.assertNotIn('Hidden dish',self.client.get('/').text)
        self.assertNotIn('Secret draft',self.client.get('/events').text)
        self.assertNotIn('Secret draft',self.client.get('/api/events').text)
        self.assertNotIn('Secret draft',self.client.get('/api/events/data?start=2020-01-01&end=2040-01-01').text)

    def test_menu_create_edit_multitag_and_visibility(self):
        self.login()
        data={'name':'Test Dish','price':'9.50','category_id':'1','available':'on','featured_rank':'1','tag_ids':['1','2'],'description':'A proper description'}
        response=self.client.post('/admin/menu/create',data=data,follow_redirects=False)
        self.assertEqual(response.status_code,303)
        with SessionLocal() as db:
            item=db.query(MenuItem).filter_by(name='Test Dish').one();item_id=item.id
            self.assertEqual(len(item.tags),2)
        response=self.client.post(f'/admin/menu/edit/{item_id}',data={**data,'name':'Edited Dish'},follow_redirects=False)
        self.assertEqual(response.status_code,303)
        with SessionLocal() as db:self.assertEqual(len(db.get(MenuItem,item_id).tags),2)
        self.assertIn('Edited Dish',self.client.get('/menu').text)
        self.client.post(f'/admin/menu/toggle/{item_id}',follow_redirects=False)
        self.assertNotIn('Edited Dish',self.client.get('/menu').text)
        self.client.post(f'/admin/menu/delete/{item_id}',follow_redirects=False)
        with SessionLocal() as db:self.assertIsNone(db.get(MenuItem,item_id))

    def test_event_create_draft_publish_edit(self):
        self.login()
        data={'title':'New Show','start':'2030-01-01T20:00','end':'2030-01-01T23:00','description':'Show details','venue_area':'Indoors','ticket_url':'https://example.com/tickets'}
        self.assertEqual(self.client.post('/admin/events/create',data=data,follow_redirects=False).status_code,302)
        with SessionLocal() as db:
            event=db.query(Event).filter_by(title='New Show').one();event_id=event.id
            self.assertFalse(event.is_published)
        self.assertNotIn('New Show',self.client.get('/events').text)
        self.assertEqual(self.client.post(f'/admin/events/edit/{event_id}',data={**data,'is_published':'on'},follow_redirects=False).status_code,302)
        text=self.client.get('/events').text
        self.assertIn('New Show',text);self.assertIn('https://example.com/tickets',text)
        self.client.post('/admin/events/delete',data={'event_id':event_id},follow_redirects=False)
        self.assertNotIn('New Show',self.client.get('/events').text)

    def test_submissions_and_status_updates(self):
        response=self.client.post('/api/rental',data={'name':'Test Guest','email':'guest@example.com','date':'2030-02-01','party_size':'35','venue_area':'Indoors','message':'Birthday plans'})
        self.assertTrue(response.json()['success']);rental_id=response.json()['id']
        self.assertEqual(self.client.post('/api/rental',data={'name':'Bad Date','email':'guest@example.com','date':'invalid'}).status_code,422)
        response=self.client.post('/api/musician',data={'name':'Test Artist','email':'artist@example.com','genre':'Rock','link':'https://example.com/music'})
        self.assertTrue(response.json()['success']);artist_id=response.json()['id']
        self.login()
        self.client.post('/admin/rentals/status',data={'id':rental_id,'status':'approved'},follow_redirects=False)
        self.client.post('/admin/musician/status',data={'id':artist_id,'status':'booked'},follow_redirects=False)
        with SessionLocal() as db:
            self.assertEqual(db.get(Rental,rental_id).status,'approved')
            self.assertEqual(db.get(Rental,rental_id).venue_area,'Indoors')
            self.assertEqual(db.get(MusicianApp,artist_id).status,'booked')

    def test_settings_and_hours_update_public_immediately(self):
        self.client.get('/') # populate cache
        self.login()
        self.client.post('/admin/site/basic',data={'site_name':'The Mine 606','address':'Test Street','city':'Pikeville','state':'KY','zip':'41501','phone':'6065550100','hero_title':'Custom headline','hero_sub':'Custom intro'},follow_redirects=False)
        text=self.client.get('/').text
        self.assertIn('Test Street',text);self.assertIn('6065550100',text);self.assertIn('Custom headline',text)
        self.client.post('/admin/site/hours',data={'dow':'tue','open':'12:30','close':'21:00'},follow_redirects=False)
        self.assertIn('Tue: 12:30pm–9:00pm',self.client.get('/').text)
        self.client.post('/admin/site/basic',data={'site_name':'The Mine 606','hero_title':'','hero_sub':''},follow_redirects=False)
        self.assertIn('GOOD DAYS.',self.client.get('/').text)

    def test_category_and_tag_management(self):
        self.login()
        self.assertEqual(self.client.post('/admin/categories/create',data={'name':'Desserts','slug':'desserts','sort_order':'5'},follow_redirects=False).status_code,303)
        self.assertEqual(self.client.post('/admin/tags/create',data={'name':'Gluten Free','slug':'gluten-free','type':'dietary'},follow_redirects=False).status_code,303)
        with SessionLocal() as db:
            cat=db.query(MenuCategory).filter_by(slug='desserts').one();tag=db.query(MenuTag).filter_by(slug='gluten-free').one();cid=cat.id;tid=tag.id
        self.assertEqual(self.client.post(f'/admin/categories/edit/{cid}',data={'name':'Sweets','slug':'sweets','sort_order':6},follow_redirects=False).status_code,303)
        self.assertEqual(self.client.post(f'/admin/tags/edit/{tid}',data={'name':'GF','slug':'gf','type':'dietary'},follow_redirects=False).status_code,303)
        self.assertEqual(self.client.post(f'/admin/categories/delete/{cid}',follow_redirects=False).status_code,303)
        self.assertEqual(self.client.post(f'/admin/tags/delete/{tid}',follow_redirects=False).status_code,303)


if __name__=='__main__':unittest.main()
