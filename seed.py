"""
Seed script — populates the database with:
  1. Admin account (pre-created per spec)
  2. Full Electronics category hierarchy with required fields
  3. Sample users for testing
  4. Sample auctions with items and bids

Run:  python seed.py
"""
from datetime import datetime, timedelta

from app import create_app
from models import db
from models.user import User
from models.item import Category, Item, ItemAttribute
from models.auction import Auction, Bid
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

NOW = datetime.utcnow()


def seed():
    with app.app_context():
        # ── 1. Admin account ────────────────────────────────────
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@buyme.com',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                first_name='System',
                last_name='Administrator',
                role='admin',
            )
            db.session.add(admin)
            print('[+] Created admin account (admin / admin123)')

        # ── 2. Sample end-users ─────────────────────────────────
        sample_users = [
            ('johndoe',   'john@example.com',  'password', 'John',  'Doe'),
            ('janesmith', 'jane@example.com',  'password', 'Jane',  'Smith'),
            ('alice',     'alice@example.com', 'password', 'Alice', 'Walker'),
            ('bob',       'bob@example.com',   'password', 'Bob',   'Jones'),
        ]
        for udata in sample_users:
            if not User.query.filter_by(username=udata[0]).first():
                u = User(
                    username=udata[0],
                    email=udata[1],
                    password_hash=bcrypt.generate_password_hash(udata[2]).decode('utf-8'),
                    first_name=udata[3],
                    last_name=udata[4],
                    role='user',
                )
                db.session.add(u)
                print(f'[+] Created user: {udata[0]}')

        db.session.flush()

        # ── 3. Category hierarchy ───────────────────────────────
        if not Category.query.first():
            electronics = Category(name='Electronics', level=0, required_fields=None)
            db.session.add(electronics)
            db.session.flush()

            categories_l1 = {
                'Computers': Category(name='Computers', parent_id=electronics.id,
                                      level=1, required_fields=None),
                'Phones': Category(name='Phones', parent_id=electronics.id,
                                   level=1, required_fields=None),
                'Audio': Category(name='Audio', parent_id=electronics.id,
                                  level=1, required_fields=None),
                'Gaming': Category(name='Gaming', parent_id=electronics.id,
                                   level=1, required_fields=None),
            }
            for cat in categories_l1.values():
                db.session.add(cat)
            db.session.flush()

            leaf_categories = [
                ('Laptops',       categories_l1['Computers'].id,
                 ['brand', 'ram', 'storage', 'screen_size', 'cpu', 'gpu', 'os']),
                ('Desktops',      categories_l1['Computers'].id,
                 ['brand', 'ram', 'storage', 'cpu', 'gpu', 'form_factor']),
                ('Components',    categories_l1['Computers'].id,
                 ['component_type', 'brand', 'compatibility']),
                ('Smartphones',   categories_l1['Phones'].id,
                 ['brand', 'os', 'screen_size', 'storage', 'ram', 'battery']),
                ('Feature Phones',categories_l1['Phones'].id,
                 ['brand', 'battery', 'screen_size']),
                ('Headphones',    categories_l1['Audio'].id,
                 ['brand', 'type', 'wireless', 'noise_cancelling']),
                ('Speakers',      categories_l1['Audio'].id,
                 ['brand', 'type', 'wattage', 'wireless']),
                ('Turntables',    categories_l1['Audio'].id,
                 ['brand', 'drive_type', 'cartridge_type']),
                ('Consoles',      categories_l1['Gaming'].id,
                 ['brand', 'model', 'storage', 'generation']),
                ('Accessories',   categories_l1['Gaming'].id,
                 ['brand', 'compatible_console', 'type']),
            ]
            for name, parent_id, fields in leaf_categories:
                db.session.add(Category(
                    name=name, parent_id=parent_id, level=2, required_fields=fields,
                ))
            print('[+] Created Electronics category hierarchy')

        db.session.commit()

        # ── 4. Sample auctions ──────────────────────────────────
        # Only seed auctions if none exist yet
        if Auction.query.first():
            print('[~] Auctions already exist, skipping auction seed')
            print('\n✅ Seed complete!')
            return

        john  = User.query.filter_by(username='johndoe').first()
        jane  = User.query.filter_by(username='janesmith').first()
        alice = User.query.filter_by(username='alice').first()
        bob   = User.query.filter_by(username='bob').first()

        def cat(name):
            return Category.query.filter_by(name=name).first()

        def make_auction(seller, cat_name, item_name, description, condition,
                         attrs, starting, reserve, increment, days_left):
            category = cat(cat_name)
            item = Item(
                name=item_name,
                description=description,
                category_id=category.id,
                seller_id=seller.id,
                condition=condition,
            )
            db.session.add(item)
            db.session.flush()
            for k, v in attrs.items():
                db.session.add(ItemAttribute(item_id=item.id, attr_name=k, attr_value=v))
            auction = Auction(
                item_id=item.id,
                seller_id=seller.id,
                starting_price=starting,
                reserve_price=reserve,
                bid_increment=increment,
                current_price=starting,
                end_time=NOW + timedelta(days=days_left),
                status='active',
            )
            db.session.add(auction)
            db.session.flush()
            return auction

        def add_bid(auction, bidder, amount):
            bid = Bid(
                auction_id=auction.id,
                bidder_id=bidder.id,
                amount=amount,
                is_auto=False,
            )
            auction.current_price = amount
            auction.current_winner_id = bidder.id
            db.session.add(bid)

        # ── Laptops ──────────────────────────────────────────────
        a1 = make_auction(
            john, 'Laptops',
            'Apple MacBook Pro 14" M3',
            'Barely used MacBook Pro with M3 chip, perfect for developers and creatives.',
            'like_new',
            {'brand': 'Apple', 'ram': '16GB', 'storage': '512GB SSD',
             'screen_size': '14"', 'cpu': 'Apple M3', 'gpu': 'Apple M3 GPU', 'os': 'macOS'},
            starting=1200.00, reserve=1400.00, increment=25.00, days_left=7,
        )
        add_bid(a1, jane, 1225.00)
        add_bid(a1, alice, 1250.00)

        a2 = make_auction(
            jane, 'Laptops',
            'Dell XPS 15 OLED',
            'Dell XPS 15 with OLED display and RTX 4060. Excellent condition.',
            'good',
            {'brand': 'Dell', 'ram': '32GB', 'storage': '1TB SSD',
             'screen_size': '15.6"', 'cpu': 'Intel i9-13900H', 'gpu': 'RTX 4060', 'os': 'Windows 11'},
            starting=900.00, reserve=1100.00, increment=20.00, days_left=5,
        )
        add_bid(a2, bob, 920.00)

        # ── Desktops ─────────────────────────────────────────────
        a3 = make_auction(
            alice, 'Desktops',
            'Custom Gaming PC — RTX 4080',
            'High-end gaming desktop built in 2023. Runs everything on ultra.',
            'good',
            {'brand': 'Custom Build', 'ram': '32GB DDR5', 'storage': '2TB NVMe',
             'cpu': 'AMD Ryzen 9 7950X', 'gpu': 'RTX 4080', 'form_factor': 'Mid Tower'},
            starting=1500.00, reserve=1800.00, increment=50.00, days_left=10,
        )
        add_bid(a3, john, 1550.00)
        add_bid(a3, bob, 1600.00)
        add_bid(a3, jane, 1650.00)

        # ── Components ───────────────────────────────────────────
        make_auction(
            bob, 'Components',
            'NVIDIA RTX 4070 Ti GPU',
            'RTX 4070 Ti, lightly used for 6 months. No mining.',
            'good',
            {'component_type': 'GPU', 'brand': 'NVIDIA', 'compatibility': 'PCIe 4.0 x16'},
            starting=550.00, reserve=650.00, increment=10.00, days_left=4,
        )

        make_auction(
            john, 'Components',
            'Samsung 990 Pro 2TB NVMe SSD',
            'Factory sealed, bought extra. PCIe 4.0 NVMe.',
            'new',
            {'component_type': 'Storage', 'brand': 'Samsung', 'compatibility': 'M.2 PCIe 4.0'},
            starting=130.00, reserve=150.00, increment=5.00, days_left=3,
        )

        # ── Smartphones ──────────────────────────────────────────
        a6 = make_auction(
            jane, 'Smartphones',
            'iPhone 15 Pro — 256GB Natural Titanium',
            'Unlocked, no scratches. Includes original box and accessories.',
            'like_new',
            {'brand': 'Apple', 'os': 'iOS 17', 'screen_size': '6.1"',
             'storage': '256GB', 'ram': '8GB', 'battery': '3274mAh'},
            starting=750.00, reserve=900.00, increment=15.00, days_left=6,
        )
        add_bid(a6, alice, 765.00)
        add_bid(a6, bob, 780.00)

        make_auction(
            alice, 'Smartphones',
            'Samsung Galaxy S24 Ultra',
            'S24 Ultra with S Pen. 12GB RAM, titanium build. Carrier unlocked.',
            'good',
            {'brand': 'Samsung', 'os': 'Android 14', 'screen_size': '6.8"',
             'storage': '512GB', 'ram': '12GB', 'battery': '5000mAh'},
            starting=700.00, reserve=850.00, increment=15.00, days_left=8,
        )

        # ── Headphones ───────────────────────────────────────────
        a8 = make_auction(
            bob, 'Headphones',
            'Sony WH-1000XM5 Wireless Headphones',
            'Best-in-class noise cancelling. Barely used, all accessories included.',
            'like_new',
            {'brand': 'Sony', 'type': 'Over-ear', 'wireless': 'Yes', 'noise_cancelling': 'Yes'},
            starting=200.00, reserve=260.00, increment=5.00, days_left=5,
        )
        add_bid(a8, john, 205.00)
        add_bid(a8, jane, 210.00)

        make_auction(
            john, 'Headphones',
            'Apple AirPods Pro (2nd Gen)',
            'AirPods Pro 2nd gen with USB-C case. Used 3 months.',
            'good',
            {'brand': 'Apple', 'type': 'In-ear', 'wireless': 'Yes', 'noise_cancelling': 'Yes'},
            starting=150.00, reserve=180.00, increment=5.00, days_left=9,
        )

        # ── Speakers ─────────────────────────────────────────────
        make_auction(
            jane, 'Speakers',
            'Sonos Era 300 Spatial Audio Speaker',
            'Dolby Atmos and Apple Spatial Audio support. Like new.',
            'like_new',
            {'brand': 'Sonos', 'type': 'Smart Speaker', 'wattage': '240W', 'wireless': 'Yes'},
            starting=280.00, reserve=350.00, increment=10.00, days_left=12,
        )

        # ── Turntables ───────────────────────────────────────────
        make_auction(
            alice, 'Turntables',
            'Audio-Technica AT-LP120XUSB',
            'Direct-drive turntable with USB output. Great condition, includes dust cover.',
            'good',
            {'brand': 'Audio-Technica', 'drive_type': 'Direct Drive', 'cartridge_type': 'AT-VM95E'},
            starting=180.00, reserve=220.00, increment=10.00, days_left=7,
        )

        # ── Consoles ─────────────────────────────────────────────
        a12 = make_auction(
            bob, 'Consoles',
            'PlayStation 5 Slim Disc Edition',
            'PS5 Slim with 2 controllers. Includes 3 games.',
            'good',
            {'brand': 'Sony', 'model': 'PS5 Slim', 'storage': '1TB', 'generation': '9th Gen'},
            starting=380.00, reserve=450.00, increment=10.00, days_left=6,
        )
        add_bid(a12, john, 390.00)
        add_bid(a12, alice, 400.00)
        add_bid(a12, jane, 410.00)

        make_auction(
            john, 'Consoles',
            'Nintendo Switch OLED',
            'Switch OLED with white Joy-Cons and dock. Barely used.',
            'like_new',
            {'brand': 'Nintendo', 'model': 'Switch OLED', 'storage': '64GB', 'generation': '2nd Gen'},
            starting=220.00, reserve=270.00, increment=10.00, days_left=4,
        )

        # ── Accessories ──────────────────────────────────────────
        make_auction(
            jane, 'Accessories',
            'PlayStation 5 DualSense Edge Controller',
            'PS5 DualSense Edge — premium controller with swappable parts.',
            'good',
            {'brand': 'Sony', 'compatible_console': 'PlayStation 5', 'type': 'Controller'},
            starting=150.00, reserve=180.00, increment=5.00, days_left=5,
        )

        db.session.commit()
        print('[+] Created 14 sample auctions with items, attributes, and bids')
        print('\n✅ Seed complete!')
        print('\nTest accounts:')
        print('  admin    / admin123')
        print('  johndoe  / password')
        print('  janesmith/ password')
        print('  alice    / password')
        print('  bob      / password')


if __name__ == '__main__':
    seed()
