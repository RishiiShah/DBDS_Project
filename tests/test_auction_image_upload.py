import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

from app import create_app
from config import Config
from models import db
from models.auction import Auction
from models.item import Category, Item
from models.user import User


class AuctionImageUploadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._original_uri = Config.SQLALCHEMY_DATABASE_URI
        cls._original_engine_options = Config.SQLALCHEMY_ENGINE_OPTIONS
        cls._original_upload_dir = Config.ITEM_UPLOAD_DIR

        fd, cls._db_path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        cls._upload_dir = tempfile.mkdtemp(prefix='buyme-item-images-')

        Config.SQLALCHEMY_DATABASE_URI = f'sqlite:///{cls._db_path}'
        Config.SQLALCHEMY_ENGINE_OPTIONS = {}
        Config.ITEM_UPLOAD_DIR = cls._upload_dir

        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['ITEM_UPLOAD_DIR'] = cls._upload_dir
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

        Config.SQLALCHEMY_DATABASE_URI = cls._original_uri
        Config.SQLALCHEMY_ENGINE_OPTIONS = cls._original_engine_options
        Config.ITEM_UPLOAD_DIR = cls._original_upload_dir

        if os.path.exists(cls._db_path):
            os.unlink(cls._db_path)
        if os.path.exists(cls._upload_dir):
            shutil.rmtree(cls._upload_dir)

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self._seed_user_and_category()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

    def _seed_user_and_category(self):
        user = User(
            username='seller1',
            email='seller@example.com',
            password_hash='hash',
            first_name='Sell',
            last_name='Er',
            role='user',
        )
        db.session.add(user)
        db.session.flush()
        self.user_id = user.id

        root = Category(name='Electronics', level=0, required_fields=['brand'])
        db.session.add(root)
        db.session.flush()

        leaf = Category(
            name='Computers',
            parent_id=root.id,
            level=1,
            required_fields=['brand', 'storage'],
        )
        db.session.add(leaf)
        db.session.commit()
        self.leaf_category_id = leaf.id

    def _login(self):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(self.user_id)
            session['_fresh'] = True

    def _auction_form_data(self):
        end_time = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        return {
            'name': 'Uploaded Test Item',
            'description': 'Listing created during upload test.',
            'category_id': str(self.leaf_category_id),
            'condition': 'good',
            'starting_price': '100.00',
            'reserve_price': '120.00',
            'bid_increment': '5.00',
            'end_time': end_time,
            'attr_brand': 'TestBrand',
            'attr_storage': '256GB',
        }

    def test_create_auction_keeps_image_optional(self):
        self._login()

        response = self.client.post('/auction/create', data=self._auction_form_data())

        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            item = Item.query.one()
            auction = Auction.query.one()
            self.assertEqual(auction.item_id, item.id)
            self.assertIsNone(item.image_filename)

    def test_create_auction_saves_optional_image(self):
        self._login()
        form_data = self._auction_form_data()
        form_data['image'] = (io.BytesIO(b'fake-image-bytes'), 'camera.jpg')

        response = self.client.post(
            '/auction/create',
            data=form_data,
            content_type='multipart/form-data',
        )

        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            item = Item.query.one()
            self.assertIsNotNone(item.image_filename)
            self.assertTrue(
                os.path.exists(os.path.join(self._upload_dir, item.image_filename))
            )


if __name__ == '__main__':
    unittest.main()
