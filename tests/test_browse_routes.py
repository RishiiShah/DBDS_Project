import os
import tempfile
import unittest
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

from app import create_app
from config import Config
from models import db
from models.auction import Auction
from models.item import Category, Item
from models.user import User


class BrowseRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._original_uri = Config.SQLALCHEMY_DATABASE_URI
        cls._original_engine_options = Config.SQLALCHEMY_ENGINE_OPTIONS
        fd, cls._db_path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)

        Config.SQLALCHEMY_DATABASE_URI = f'sqlite:///{cls._db_path}'
        Config.SQLALCHEMY_ENGINE_OPTIONS = {}

        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

        Config.SQLALCHEMY_DATABASE_URI = cls._original_uri
        Config.SQLALCHEMY_ENGINE_OPTIONS = cls._original_engine_options
        if os.path.exists(cls._db_path):
            os.unlink(cls._db_path)

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self._seed_active_auction()

    def _seed_active_auction(self):
        seller = User(
            username='seller1',
            email='seller@example.com',
            password_hash='hash',
            first_name='Sell',
            last_name='Er',
            role='user',
        )
        db.session.add(seller)
        db.session.flush()

        root = Category(name='Electronics', level=0, required_fields=['brand'])
        db.session.add(root)
        db.session.flush()

        child = Category(
            name='Computers',
            parent_id=root.id,
            level=1,
            required_fields=['brand', 'storage'],
        )
        db.session.add(child)
        db.session.flush()
        self.child_id = child.id

        item = Item(
            name='Test Laptop',
            description='A seeded test listing.',
            category_id=child.id,
            seller_id=seller.id,
            condition='good',
        )
        db.session.add(item)
        db.session.flush()

        db.session.add(
            Auction(
                item_id=item.id,
                seller_id=seller.id,
                starting_price=500,
                reserve_price=600,
                bid_increment=25,
                current_price=550,
                end_time=datetime.utcnow() + timedelta(days=2),
                status='active',
            )
        )
        db.session.commit()

    def test_browse_shows_active_auctions_without_category_selection(self):
        response = self.client.get('/browse')

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('Browse Auctions', body)
        self.assertIn('Filters', body)
        self.assertIn('Test Laptop', body)
        self.assertNotIn('Select a category from the sidebar to browse auctions.', body)

    def test_legacy_search_redirects_to_browse(self):
        response = self.client.get(
            f'/search?q=laptop&condition=good&category_id={self.child_id}',
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response.headers['Location'])
        self.assertEqual(parsed.path, '/browse')
        query = parse_qs(parsed.query)
        self.assertEqual(query['q'], ['laptop'])
        self.assertEqual(query['condition'], ['good'])
        self.assertEqual(query['category_id'], [str(self.child_id)])

    def test_auctions_route_redirects_to_browse(self):
        response = self.client.get(
            f'/auctions?category={self.child_id}',
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response.headers['Location'])
        self.assertEqual(parsed.path, '/browse')
        query = parse_qs(parsed.query)
        self.assertEqual(query['category_id'], [str(self.child_id)])


if __name__ == '__main__':
    unittest.main()
