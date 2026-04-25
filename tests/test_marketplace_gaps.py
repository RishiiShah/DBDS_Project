import os
import tempfile
import unittest
from datetime import datetime, timedelta

from app import create_app
from config import Config
from models import db
from models.alert import Alert, ItemWatch
from models.auction import Auction, Bid
from models.item import Category, Item, ItemAttribute
from models.user import User
from utils.bidding import process_new_bid
from utils.watches import check_wishlist


class MarketplaceGapTests(unittest.TestCase):
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
            self._seed_marketplace()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def _seed_marketplace(self):
        seller = User(
            username='seller1',
            email='seller@example.com',
            password_hash='hash',
            first_name='Sell',
            last_name='Er',
            role='user',
        )
        buyer_a = User(
            username='buyer_a',
            email='buyer_a@example.com',
            password_hash='hash',
            first_name='Buyer',
            last_name='A',
            role='user',
        )
        buyer_b = User(
            username='buyer_b',
            email='buyer_b@example.com',
            password_hash='hash',
            first_name='Buyer',
            last_name='B',
            role='user',
        )
        buyer_c = User(
            username='buyer_c',
            email='buyer_c@example.com',
            password_hash='hash',
            first_name='Buyer',
            last_name='C',
            role='user',
        )
        watcher = User(
            username='watcher1',
            email='watcher@example.com',
            password_hash='hash',
            first_name='Watch',
            last_name='Er',
            role='user',
        )
        db.session.add_all([seller, buyer_a, buyer_b, buyer_c, watcher])
        db.session.flush()

        self.seller_id = seller.id
        self.buyer_a_id = buyer_a.id
        self.buyer_b_id = buyer_b.id
        self.buyer_c_id = buyer_c.id
        self.watcher_id = watcher.id

        root = Category(name='Electronics', level=0)
        db.session.add(root)
        db.session.flush()

        branch = Category(name='Computers', parent_id=root.id, level=1)
        db.session.add(branch)
        db.session.flush()

        leaf = Category(
            name='Laptops',
            parent_id=branch.id,
            level=2,
            required_fields=['brand', 'color'],
        )
        db.session.add(leaf)
        db.session.flush()
        self.branch_id = branch.id
        self.leaf_id = leaf.id

        apple_item = Item(
            name='Apple MacBook Test',
            description='Blue Apple laptop.',
            category_id=leaf.id,
            seller_id=seller.id,
            condition='good',
        )
        dell_item = Item(
            name='Dell XPS Test',
            description='Black Dell laptop.',
            category_id=leaf.id,
            seller_id=seller.id,
            condition='good',
        )
        db.session.add_all([apple_item, dell_item])
        db.session.flush()

        db.session.add_all(
            [
                ItemAttribute(item_id=apple_item.id, attr_name='brand', attr_value='Apple'),
                ItemAttribute(item_id=apple_item.id, attr_name='color', attr_value='Blue'),
                ItemAttribute(item_id=dell_item.id, attr_name='brand', attr_value='Dell'),
                ItemAttribute(item_id=dell_item.id, attr_name='color', attr_value='Black'),
            ]
        )

        apple_auction = Auction(
            item_id=apple_item.id,
            seller_id=seller.id,
            starting_price=800,
            reserve_price=900,
            bid_increment=25,
            current_price=850,
            end_time=datetime.utcnow() + timedelta(days=10),
            status='active',
        )
        dell_auction = Auction(
            item_id=dell_item.id,
            seller_id=seller.id,
            starting_price=700,
            reserve_price=800,
            bid_increment=25,
            current_price=700,
            end_time=datetime.utcnow() + timedelta(days=12),
            status='active',
        )
        db.session.add_all([apple_auction, dell_auction])
        db.session.flush()

        db.session.add_all(
            [
                Bid(auction_id=apple_auction.id, bidder_id=buyer_a.id, amount=850, is_auto=False),
                Bid(auction_id=apple_auction.id, bidder_id=buyer_b.id, amount=875, is_auto=False),
            ]
        )
        apple_auction.current_price = 875
        apple_auction.current_winner_id = buyer_b.id
        db.session.commit()

        self.apple_auction_id = apple_auction.id

    def test_browse_filters_by_item_attributes(self):
        response = self.client.get(f'/browse/{self.branch_id}?attr_brand=Apple')

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('Apple MacBook Test', body)
        self.assertNotIn('Dell XPS Test', body)

    def test_public_user_auctions_show_bid_participation(self):
        response = self.client.get(f'/user/{self.buyer_a_id}/auctions')

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('Bid Participation', body)
        self.assertIn('Apple MacBook Test', body)

    def test_watch_attribute_filters_drive_item_available_alerts(self):
        with self.app.app_context():
            watch = ItemWatch(
                user_id=self.watcher_id,
                keyword='MacBook',
                category_id=self.leaf_id,
                attributes={'brand': 'Apple', 'color': 'Blue'},
                is_active=True,
            )
            db.session.add(watch)

            item = Item(
                name='MacBook Air Match',
                description='A blue Apple laptop just listed.',
                category_id=self.leaf_id,
                seller_id=self.seller_id,
                condition='good',
            )
            db.session.add(item)
            db.session.flush()
            db.session.add_all(
                [
                    ItemAttribute(item_id=item.id, attr_name='brand', attr_value='Apple'),
                    ItemAttribute(item_id=item.id, attr_name='color', attr_value='Blue'),
                ]
            )
            auction = Auction(
                item_id=item.id,
                seller_id=self.seller_id,
                starting_price=650,
                reserve_price=700,
                bid_increment=25,
                current_price=650,
                end_time=datetime.utcnow() + timedelta(days=8),
                status='active',
            )
            db.session.add(auction)
            db.session.commit()

            check_wishlist(auction)

            alerts = Alert.query.filter_by(user_id=self.watcher_id, alert_type='item_available').all()
            self.assertEqual(len(alerts), 1)
            self.assertIn('MacBook Air Match', alerts[0].message)

    def test_manual_bid_alerts_other_participants(self):
        with self.app.app_context():
            auction = Auction.query.get(self.apple_auction_id)
            process_new_bid(auction, 925, self.buyer_c_id)

            buyer_a_alerts = Alert.query.filter_by(user_id=self.buyer_a_id).all()
            buyer_b_alerts = Alert.query.filter_by(user_id=self.buyer_b_id).all()

            self.assertTrue(
                any(
                    alert.alert_type == 'custom' and 'higher manual bid' in alert.message.lower()
                    for alert in buyer_a_alerts
                )
            )
            self.assertTrue(
                any(alert.alert_type == 'outbid' for alert in buyer_b_alerts)
            )


if __name__ == '__main__':
    unittest.main()
