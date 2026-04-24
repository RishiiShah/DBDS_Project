"""
Seed script — populates the database with:
  1. Admin account (pre-created per spec)
  2. Sample users for testing
  3. Electronics category hierarchy with required fields
  4. Sporting Goods category hierarchy with required fields
  5. Sample auctions with items, attributes, and bids

Run:  python seed.py
      (safe to re-run — all blocks are individually guarded)
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


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_or_create_user(username, email, password, first_name, last_name, role='user'):
    if User.query.filter_by(username=username).first():
        return
    db.session.add(User(
        username=username,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        first_name=first_name,
        last_name=last_name,
        role=role,
    ))
    print(f'[+] Created user: {username}')


def make_auction(seller, cat_name, item_name, description, condition,
                 attrs, starting, reserve, increment, days_left):
    category = Category.query.filter_by(name=cat_name).first()
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
    db.session.add(Bid(
        auction_id=auction.id,
        bidder_id=bidder.id,
        amount=amount,
        is_auto=False,
    ))
    auction.current_price = amount
    auction.current_winner_id = bidder.id


# ── Seed ─────────────────────────────────────────────────────────────────────

def seed():
    with app.app_context():

        # ── 1. Admin ────────────────────────────────────────────────────────
        get_or_create_user('admin', 'admin@buyme.com', 'admin123',
                           'System', 'Administrator', role='admin')

        # ── 2. Sample end-users ─────────────────────────────────────────────
        for udata in [
            ('johndoe',   'john@example.com',  'password', 'John',  'Doe'),
            ('janesmith', 'jane@example.com',  'password', 'Jane',  'Smith'),
            ('alice',     'alice@example.com', 'password', 'Alice', 'Walker'),
            ('bob',       'bob@example.com',   'password', 'Bob',   'Jones'),
        ]:
            get_or_create_user(*udata)

        db.session.flush()

        # ── 3. Electronics category hierarchy ───────────────────────────────
        if not Category.query.filter_by(name='Electronics', level=0).first():
            electronics = Category(name='Electronics', level=0, required_fields=None)
            db.session.add(electronics)
            db.session.flush()

            l1 = {
                'Computers': Category(name='Computers', parent_id=electronics.id, level=1, required_fields=None),
                'Phones':    Category(name='Phones',    parent_id=electronics.id, level=1, required_fields=None),
                'Audio':     Category(name='Audio',     parent_id=electronics.id, level=1, required_fields=None),
                'Gaming':    Category(name='Gaming',    parent_id=electronics.id, level=1, required_fields=None),
            }
            for cat in l1.values():
                db.session.add(cat)
            db.session.flush()

            for name, parent_id, fields in [
                ('Laptops',        l1['Computers'].id, ['brand', 'ram', 'storage', 'screen_size', 'cpu', 'gpu', 'os']),
                ('Desktops',       l1['Computers'].id, ['brand', 'ram', 'storage', 'cpu', 'gpu', 'form_factor']),
                ('Components',     l1['Computers'].id, ['component_type', 'brand', 'compatibility']),
                ('Smartphones',    l1['Phones'].id,    ['brand', 'os', 'screen_size', 'storage', 'ram', 'battery']),
                ('Feature Phones', l1['Phones'].id,    ['brand', 'battery', 'screen_size']),
                ('Headphones',     l1['Audio'].id,     ['brand', 'type', 'wireless', 'noise_cancelling']),
                ('Speakers',       l1['Audio'].id,     ['brand', 'type', 'wattage', 'wireless']),
                ('Turntables',     l1['Audio'].id,     ['brand', 'drive_type', 'cartridge_type']),
                ('Consoles',       l1['Gaming'].id,    ['brand', 'model', 'storage', 'generation']),
                ('Gaming Accessories', l1['Gaming'].id, ['brand', 'compatible_console', 'type']),
            ]:
                db.session.add(Category(name=name, parent_id=parent_id, level=2, required_fields=fields))

            db.session.commit()
            print('[+] Created Electronics category hierarchy')

        # ── 4. Sporting Goods category hierarchy ─────────────────────────────
        if not Category.query.filter_by(name='Sporting Goods', level=0).first():
            sporting = Category(name='Sporting Goods', level=0, required_fields=None)
            db.session.add(sporting)
            db.session.flush()

            l1 = {
                'Cycling':           Category(name='Cycling',           parent_id=sporting.id, level=1, required_fields=None),
                'Fitness':           Category(name='Fitness',           parent_id=sporting.id, level=1, required_fields=None),
                'Outdoor & Adventure': Category(name='Outdoor & Adventure', parent_id=sporting.id, level=1, required_fields=None),
                'Team Sports':       Category(name='Team Sports',       parent_id=sporting.id, level=1, required_fields=None),
            }
            for cat in l1.values():
                db.session.add(cat)
            db.session.flush()

            for name, parent_id, fields in [
                ('Bikes',              l1['Cycling'].id,             ['brand', 'type', 'frame_size', 'frame_material', 'gears', 'wheel_size']),
                ('Cycling Accessories',l1['Cycling'].id,             ['brand', 'type', 'compatible_with']),
                ('Cardio Equipment',   l1['Fitness'].id,             ['brand', 'type', 'max_user_weight', 'foldable']),
                ('Strength Equipment', l1['Fitness'].id,             ['brand', 'type', 'weight', 'material']),
                ('Camping Gear',       l1['Outdoor & Adventure'].id, ['brand', 'type', 'capacity', 'material', 'season_rating']),
                ('Hiking Gear',        l1['Outdoor & Adventure'].id, ['brand', 'type', 'size', 'waterproof']),
                ('Football',           l1['Team Sports'].id,         ['brand', 'size', 'material', 'type']),
                ('Basketball',         l1['Team Sports'].id,         ['brand', 'size', 'material', 'indoor_outdoor']),
                ('Baseball',           l1['Team Sports'].id,         ['brand', 'type', 'material', 'size']),
            ]:
                db.session.add(Category(name=name, parent_id=parent_id, level=2, required_fields=fields))

            db.session.commit()
            print('[+] Created Sporting Goods category hierarchy')

        # ── 5. Sample auctions ───────────────────────────────────────────────
        john  = User.query.filter_by(username='johndoe').first()
        jane  = User.query.filter_by(username='janesmith').first()
        alice = User.query.filter_by(username='alice').first()
        bob   = User.query.filter_by(username='bob').first()

        # ── Electronics auctions (skip if already seeded) ────────────────────
        if not Auction.query.join(Item).join(Category).filter(Category.name == 'Laptops').first():

            a1 = make_auction(
                john, 'Laptops', 'Apple MacBook Pro 14" M3',
                'Barely used MacBook Pro with M3 chip, perfect for developers and creatives.',
                'like_new',
                {'brand': 'Apple', 'ram': '16GB', 'storage': '512GB SSD',
                 'screen_size': '14"', 'cpu': 'Apple M3', 'gpu': 'Apple M3 GPU', 'os': 'macOS'},
                starting=1200.00, reserve=1400.00, increment=25.00, days_left=7,
            )
            add_bid(a1, jane, 1225.00)
            add_bid(a1, alice, 1250.00)

            a2 = make_auction(
                jane, 'Laptops', 'Dell XPS 15 OLED',
                'Dell XPS 15 with OLED display and RTX 4060. Excellent condition.',
                'good',
                {'brand': 'Dell', 'ram': '32GB', 'storage': '1TB SSD',
                 'screen_size': '15.6"', 'cpu': 'Intel i9-13900H', 'gpu': 'RTX 4060', 'os': 'Windows 11'},
                starting=900.00, reserve=1100.00, increment=20.00, days_left=5,
            )
            add_bid(a2, bob, 920.00)

            a3 = make_auction(
                alice, 'Desktops', 'Custom Gaming PC — RTX 4080',
                'High-end gaming desktop built in 2023. Runs everything on ultra.',
                'good',
                {'brand': 'Custom Build', 'ram': '32GB DDR5', 'storage': '2TB NVMe',
                 'cpu': 'AMD Ryzen 9 7950X', 'gpu': 'RTX 4080', 'form_factor': 'Mid Tower'},
                starting=1500.00, reserve=1800.00, increment=50.00, days_left=10,
            )
            add_bid(a3, john, 1550.00)
            add_bid(a3, bob, 1600.00)
            add_bid(a3, jane, 1650.00)

            make_auction(
                bob, 'Components', 'NVIDIA RTX 4070 Ti GPU',
                'RTX 4070 Ti, lightly used for 6 months. No mining.',
                'good',
                {'component_type': 'GPU', 'brand': 'NVIDIA', 'compatibility': 'PCIe 4.0 x16'},
                starting=550.00, reserve=650.00, increment=10.00, days_left=4,
            )

            make_auction(
                john, 'Components', 'Samsung 990 Pro 2TB NVMe SSD',
                'Factory sealed, bought extra. PCIe 4.0 NVMe.',
                'new',
                {'component_type': 'Storage', 'brand': 'Samsung', 'compatibility': 'M.2 PCIe 4.0'},
                starting=130.00, reserve=150.00, increment=5.00, days_left=3,
            )

            a6 = make_auction(
                jane, 'Smartphones', 'iPhone 15 Pro — 256GB Natural Titanium',
                'Unlocked, no scratches. Includes original box and accessories.',
                'like_new',
                {'brand': 'Apple', 'os': 'iOS 17', 'screen_size': '6.1"',
                 'storage': '256GB', 'ram': '8GB', 'battery': '3274mAh'},
                starting=750.00, reserve=900.00, increment=15.00, days_left=6,
            )
            add_bid(a6, alice, 765.00)
            add_bid(a6, bob, 780.00)

            make_auction(
                alice, 'Smartphones', 'Samsung Galaxy S24 Ultra',
                'S24 Ultra with S Pen. 12GB RAM, titanium build. Carrier unlocked.',
                'good',
                {'brand': 'Samsung', 'os': 'Android 14', 'screen_size': '6.8"',
                 'storage': '512GB', 'ram': '12GB', 'battery': '5000mAh'},
                starting=700.00, reserve=850.00, increment=15.00, days_left=8,
            )

            a8 = make_auction(
                bob, 'Headphones', 'Sony WH-1000XM5 Wireless Headphones',
                'Best-in-class noise cancelling. Barely used, all accessories included.',
                'like_new',
                {'brand': 'Sony', 'type': 'Over-ear', 'wireless': 'Yes', 'noise_cancelling': 'Yes'},
                starting=200.00, reserve=260.00, increment=5.00, days_left=5,
            )
            add_bid(a8, john, 205.00)
            add_bid(a8, jane, 210.00)

            make_auction(
                john, 'Headphones', 'Apple AirPods Pro (2nd Gen)',
                'AirPods Pro 2nd gen with USB-C case. Used 3 months.',
                'good',
                {'brand': 'Apple', 'type': 'In-ear', 'wireless': 'Yes', 'noise_cancelling': 'Yes'},
                starting=150.00, reserve=180.00, increment=5.00, days_left=9,
            )

            make_auction(
                jane, 'Speakers', 'Sonos Era 300 Spatial Audio Speaker',
                'Dolby Atmos and Apple Spatial Audio support. Like new.',
                'like_new',
                {'brand': 'Sonos', 'type': 'Smart Speaker', 'wattage': '240W', 'wireless': 'Yes'},
                starting=280.00, reserve=350.00, increment=10.00, days_left=12,
            )

            make_auction(
                alice, 'Turntables', 'Audio-Technica AT-LP120XUSB',
                'Direct-drive turntable with USB output. Great condition, includes dust cover.',
                'good',
                {'brand': 'Audio-Technica', 'drive_type': 'Direct Drive', 'cartridge_type': 'AT-VM95E'},
                starting=180.00, reserve=220.00, increment=10.00, days_left=7,
            )

            a12 = make_auction(
                bob, 'Consoles', 'PlayStation 5 Slim Disc Edition',
                'PS5 Slim with 2 controllers. Includes 3 games.',
                'good',
                {'brand': 'Sony', 'model': 'PS5 Slim', 'storage': '1TB', 'generation': '9th Gen'},
                starting=380.00, reserve=450.00, increment=10.00, days_left=6,
            )
            add_bid(a12, john, 390.00)
            add_bid(a12, alice, 400.00)
            add_bid(a12, jane, 410.00)

            make_auction(
                john, 'Consoles', 'Nintendo Switch OLED',
                'Switch OLED with white Joy-Cons and dock. Barely used.',
                'like_new',
                {'brand': 'Nintendo', 'model': 'Switch OLED', 'storage': '64GB', 'generation': '2nd Gen'},
                starting=220.00, reserve=270.00, increment=10.00, days_left=4,
            )

            make_auction(
                jane, 'Gaming Accessories', 'PlayStation 5 DualSense Edge Controller',
                'PS5 DualSense Edge — premium controller with swappable parts.',
                'good',
                {'brand': 'Sony', 'compatible_console': 'PlayStation 5', 'type': 'Controller'},
                starting=150.00, reserve=180.00, increment=5.00, days_left=5,
            )

            db.session.commit()
            print('[+] Created 14 Electronics auctions')

        # ── Sporting Goods auctions (skip if already seeded) ─────────────────
        if not Auction.query.join(Item).join(Category).filter(Category.name == 'Bikes').first():

            a_sg1 = make_auction(
                alice, 'Bikes', 'Trek Marlin 7 Mountain Bike',
                'Hardtail mountain bike with hydraulic disc brakes and 1x drivetrain. Barely ridden.',
                'like_new',
                {'brand': 'Trek', 'type': 'Mountain', 'frame_size': 'Medium (17.5")',
                 'frame_material': 'Aluminum', 'gears': '12-speed', 'wheel_size': '29"'},
                starting=650.00, reserve=800.00, increment=25.00, days_left=8,
            )
            add_bid(a_sg1, john, 675.00)
            add_bid(a_sg1, bob, 700.00)

            make_auction(
                bob, 'Bikes', 'Specialized Sirrus 3.0 Hybrid Bike',
                'Lightweight hybrid for commuting and fitness. Carbon fork, 24-speed.',
                'good',
                {'brand': 'Specialized', 'type': 'Hybrid', 'frame_size': 'Large (56cm)',
                 'frame_material': 'Aluminum', 'gears': '24-speed', 'wheel_size': '700c'},
                starting=400.00, reserve=500.00, increment=15.00, days_left=6,
            )

            make_auction(
                john, 'Cycling Accessories', 'Garmin Edge 540 Cycling Computer',
                'GPS cycling computer with mapping, ClimbPro, and Garmin Coach training plans.',
                'like_new',
                {'brand': 'Garmin', 'type': 'GPS Computer', 'compatible_with': 'Universal mount'},
                starting=280.00, reserve=330.00, increment=10.00, days_left=5,
            )

            a_sg4 = make_auction(
                jane, 'Cardio Equipment', 'Peloton Bike+',
                'Peloton Bike+ with rotating screen and auto-resistance. 1 year subscription included.',
                'good',
                {'brand': 'Peloton', 'type': 'Stationary Bike',
                 'max_user_weight': '297 lbs', 'foldable': 'No'},
                starting=1200.00, reserve=1500.00, increment=50.00, days_left=10,
            )
            add_bid(a_sg4, alice, 1250.00)
            add_bid(a_sg4, bob, 1300.00)

            make_auction(
                alice, 'Cardio Equipment', 'NordicTrack T 6.5 Si Treadmill',
                'Folding treadmill with 10% incline, iFit compatible, and 10" touchscreen.',
                'good',
                {'brand': 'NordicTrack', 'type': 'Treadmill',
                 'max_user_weight': '300 lbs', 'foldable': 'Yes'},
                starting=500.00, reserve=650.00, increment=20.00, days_left=7,
            )

            a_sg6 = make_auction(
                bob, 'Strength Equipment', 'Bowflex SelectTech 552 Adjustable Dumbbells',
                'Adjustable dumbbells from 5 to 52.5 lbs each. Replaces 15 sets of weights.',
                'like_new',
                {'brand': 'Bowflex', 'type': 'Dumbbells',
                 'weight': '5–52.5 lbs each', 'material': 'Steel/Plastic'},
                starting=250.00, reserve=320.00, increment=10.00, days_left=5,
            )
            add_bid(a_sg6, john, 260.00)
            add_bid(a_sg6, jane, 270.00)

            make_auction(
                john, 'Strength Equipment', 'CAP Barbell 300 lb Olympic Weight Set',
                '300 lb Olympic barbell set with 7-foot bar, collars, and plates. Never used.',
                'new',
                {'brand': 'CAP Barbell', 'type': 'Barbell Set',
                 'weight': '300 lbs total', 'material': 'Cast Iron'},
                starting=200.00, reserve=260.00, increment=10.00, days_left=9,
            )

            a_sg8 = make_auction(
                jane, 'Camping Gear', 'REI Co-op Half Dome 2 Plus Tent',
                'Two-person backpacking tent with full coverage rainfly and gear loft. Used twice.',
                'like_new',
                {'brand': 'REI Co-op', 'type': 'Backpacking Tent',
                 'capacity': '2 person', 'material': 'Ripstop Nylon', 'season_rating': '3-season'},
                starting=180.00, reserve=230.00, increment=10.00, days_left=6,
            )
            add_bid(a_sg8, alice, 190.00)

            make_auction(
                alice, 'Camping Gear', 'Coleman Sundome 4-Person Tent',
                'Easy setup dome tent with WeatherTec system. Great for car camping.',
                'good',
                {'brand': 'Coleman', 'type': 'Dome Tent',
                 'capacity': '4 person', 'material': 'Polyester', 'season_rating': '3-season'},
                starting=80.00, reserve=110.00, increment=5.00, days_left=4,
            )

            make_auction(
                bob, 'Hiking Gear', 'Salomon X Ultra 4 GTX Hiking Shoes',
                'Gore-Tex waterproof trail shoes, size US 10. Only used on 2 hikes.',
                'like_new',
                {'brand': 'Salomon', 'type': 'Trail Shoes',
                 'size': 'US 10', 'waterproof': 'Yes (Gore-Tex)'},
                starting=100.00, reserve=130.00, increment=5.00, days_left=7,
            )

            make_auction(
                john, 'Football', 'Wilson NFL Duke Official Game Ball',
                'Official NFL game ball, hand-selected premium leather. New in box.',
                'new',
                {'brand': 'Wilson', 'size': 'Official', 'material': 'Premium Leather', 'type': 'Game Ball'},
                starting=90.00, reserve=120.00, increment=5.00, days_left=5,
            )

            a_sg12 = make_auction(
                jane, 'Basketball', 'Spalding NBA Official Game Ball',
                'Official NBA game ball, genuine leather. Used for one season in a rec league.',
                'good',
                {'brand': 'Spalding', 'size': 'Size 7 (29.5")',
                 'material': 'Genuine Leather', 'indoor_outdoor': 'Indoor'},
                starting=120.00, reserve=160.00, increment=5.00, days_left=6,
            )
            add_bid(a_sg12, bob, 125.00)
            add_bid(a_sg12, alice, 130.00)

            make_auction(
                alice, 'Baseball', 'Rawlings Heart of the Hide Baseball Glove',
                '11.5" infielder glove, pro-grade leather. Broken in and game ready.',
                'good',
                {'brand': 'Rawlings', 'type': 'Infielder Glove',
                 'material': 'Pro-grade Leather', 'size': '11.5"'},
                starting=150.00, reserve=200.00, increment=10.00, days_left=8,
            )

            db.session.commit()
            print('[+] Created 13 Sporting Goods auctions')

        print('\n✅ Seed complete!')
        print('\nTest accounts:')
        print('  admin     / admin123')
        print('  johndoe   / password')
        print('  janesmith / password')
        print('  alice     / password')
        print('  bob       / password')


if __name__ == '__main__':
    seed()
