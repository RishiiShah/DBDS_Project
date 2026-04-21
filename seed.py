"""
Seed script — populates the database with:
  1. Admin account (pre-created per spec)
  2. Full Electronics category hierarchy with required fields
  3. A couple of sample users for testing

Run:  source venv/bin/activate && python seed.py
"""
from app import create_app
from models import db
from models.user import User
from models.item import Category
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)


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
        for udata in [
            ('johndoe', 'john@example.com', 'password', 'John', 'Doe'),
            ('janesmith', 'jane@example.com', 'password', 'Jane', 'Smith'),
        ]:
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

        # ── 3. Category hierarchy ───────────────────────────────
        if not Category.query.first():
            # Root
            electronics = Category(name='Electronics', level=0, required_fields=None)
            db.session.add(electronics)
            db.session.flush()  # Get ID

            # Level 1
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

            # Level 2 (leaf categories with required fields)
            leaf_categories = [
                # Computers
                ('Laptops', categories_l1['Computers'].id,
                 ['brand', 'ram', 'storage', 'screen_size', 'cpu', 'gpu', 'os']),
                ('Desktops', categories_l1['Computers'].id,
                 ['brand', 'ram', 'storage', 'cpu', 'gpu', 'form_factor']),
                ('Components', categories_l1['Computers'].id,
                 ['component_type', 'brand', 'compatibility']),
                # Phones
                ('Smartphones', categories_l1['Phones'].id,
                 ['brand', 'os', 'screen_size', 'storage', 'ram', 'battery']),
                ('Feature Phones', categories_l1['Phones'].id,
                 ['brand', 'battery', 'screen_size']),
                # Audio
                ('Headphones', categories_l1['Audio'].id,
                 ['brand', 'type', 'wireless', 'noise_cancelling']),
                ('Speakers', categories_l1['Audio'].id,
                 ['brand', 'type', 'wattage', 'wireless']),
                ('Turntables', categories_l1['Audio'].id,
                 ['brand', 'drive_type', 'cartridge_type']),
                # Gaming
                ('Consoles', categories_l1['Gaming'].id,
                 ['brand', 'model', 'storage', 'generation']),
                ('Accessories', categories_l1['Gaming'].id,
                 ['brand', 'compatible_console', 'type']),
            ]
            for name, parent_id, fields in leaf_categories:
                cat = Category(
                    name=name,
                    parent_id=parent_id,
                    level=2,
                    required_fields=fields,
                )
                db.session.add(cat)

            print('[+] Created Electronics category hierarchy (4 sub-categories, 10 leaf categories)')

        db.session.commit()
        print('\n✅ Seed complete!')


if __name__ == '__main__':
    seed()
