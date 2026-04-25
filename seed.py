"""
Seed script for the expanded BuyMe catalog.

Creates:
  - default admin account
  - sample end-user accounts
  - a broader multi-family category hierarchy
  - roughly 150 deterministic auctions across the catalog
  - bid history and completed transactions for some closed auctions

Run:
  python seed.py
"""

from datetime import datetime, timedelta

from flask_bcrypt import Bcrypt

from app import create_app
from models import db
from models.auction import Auction, Bid, Transaction
from models.item import Category, Item, ItemAttribute
from models.user import User
from seed_catalog import CATEGORY_TREE, SEED_USERS, get_seed_auction_specs

app = create_app()
bcrypt = Bcrypt(app)
NOW = datetime.utcnow()


def get_or_create_user(user_spec):
    existing_user = User.query.filter_by(username=user_spec["username"]).first()
    if existing_user:
        return existing_user, False

    user = User(
        username=user_spec["username"],
        email=user_spec["email"],
        password_hash=bcrypt.generate_password_hash(user_spec["password"]).decode("utf-8"),
        first_name=user_spec["first_name"],
        last_name=user_spec["last_name"],
        role=user_spec.get("role", "user"),
    )
    db.session.add(user)
    return user, True


def get_or_create_category(name, parent_id, level, required_fields=None):
    category = Category.query.filter_by(name=name, parent_id=parent_id).first()
    created = False

    if not category:
        category = Category(
            name=name,
            parent_id=parent_id,
            level=level,
            required_fields=required_fields,
        )
        db.session.add(category)
        db.session.flush()
        created = True
    else:
        category.level = level
        if required_fields is not None:
            category.required_fields = required_fields

    return category, created


def ensure_category_tree():
    leaf_categories = {}
    created_count = 0

    for root_spec in CATEGORY_TREE:
        root_category, created = get_or_create_category(
            root_spec["name"],
            None,
            0,
            None,
        )
        created_count += int(created)

        for branch_spec in root_spec["children"]:
            branch_category, created = get_or_create_category(
                branch_spec["name"],
                root_category.id,
                1,
                None,
            )
            created_count += int(created)

            for leaf_spec in branch_spec["leaves"]:
                leaf_category, created = get_or_create_category(
                    leaf_spec["name"],
                    branch_category.id,
                    2,
                    leaf_spec["required_fields"],
                )
                leaf_categories[leaf_spec["name"]] = leaf_category
                created_count += int(created)

    return leaf_categories, created_count


def _canonical_category_paths():
    paths = set()
    for root_spec in CATEGORY_TREE:
        root_path = (root_spec["name"],)
        paths.add(root_path)
        for branch_spec in root_spec["children"]:
            branch_path = root_path + (branch_spec["name"],)
            paths.add(branch_path)
            for leaf_spec in branch_spec["leaves"]:
                paths.add(branch_path + (leaf_spec["name"],))
    return paths


def _category_path(category):
    names = []
    current = category
    while current is not None:
        names.append(current.name)
        current = current.parent
    return tuple(reversed(names))


def prune_obsolete_categories():
    canonical_paths = _canonical_category_paths()
    pruned_count = 0

    changed = True
    while changed:
        changed = False
        categories = Category.query.order_by(Category.level.desc(), Category.id.desc()).all()
        for category in categories:
            if _category_path(category) in canonical_paths:
                continue
            if category.items.count() or category.children.count():
                continue

            db.session.delete(category)
            db.session.flush()
            pruned_count += 1
            changed = True

    return pruned_count


def add_bid(auction, bidder_id, amount):
    db.session.add(
        Bid(
            auction_id=auction.id,
            bidder_id=bidder_id,
            amount=amount,
            is_auto=False,
        )
    )
    auction.current_price = amount
    auction.current_winner_id = bidder_id


def ensure_transaction(auction):
    if (
        auction.status != "closed"
        or not auction.current_winner_id
        or float(auction.current_price) < float(auction.reserve_price)
        or auction.transaction
    ):
        return False

    final_price = float(auction.current_price)
    transaction = Transaction(
        auction_id=auction.id,
        buyer_id=auction.current_winner_id,
        seller_id=auction.seller_id,
        final_price=final_price,
        commission=round(final_price * Transaction.COMMISSION_RATE, 2),
    )
    db.session.add(transaction)
    return True


def create_seed_auction(spec, user_map, leaf_categories):
    seller = user_map[spec["seller"]]
    existing_item = Item.query.filter_by(name=spec["name"], seller_id=seller.id).first()
    if existing_item:
        updated = False
        existing_auction = existing_item.auction
        target_end_time = NOW + timedelta(days=spec["days_left"])

        if existing_auction:
            if existing_auction.end_time != target_end_time:
                existing_auction.end_time = target_end_time
                updated = True
            if existing_auction.status != spec["status"]:
                existing_auction.status = spec["status"]
                updated = True

            transaction_created = ensure_transaction(existing_auction)
            return False, transaction_created, updated

        return False, False, updated

    item = Item(
        name=spec["name"],
        description=spec["description"],
        category_id=leaf_categories[spec["category"]].id,
        seller_id=seller.id,
        condition=spec["condition"],
    )
    db.session.add(item)
    db.session.flush()

    for attr_name, attr_value in spec["attrs"].items():
        db.session.add(
            ItemAttribute(
                item_id=item.id,
                attr_name=attr_name,
                attr_value=attr_value,
            )
        )

    auction = Auction(
        item_id=item.id,
        seller_id=seller.id,
        starting_price=spec["starting_price"],
        reserve_price=spec["reserve_price"],
        bid_increment=spec["bid_increment"],
        current_price=spec["starting_price"],
        end_time=NOW + timedelta(days=spec["days_left"]),
        status=spec["status"],
    )
    db.session.add(auction)
    db.session.flush()

    for bid_spec in spec["bids"]:
        bidder = user_map[bid_spec["bidder"]]
        add_bid(auction, bidder.id, bid_spec["amount"])

    transaction_created = ensure_transaction(auction)
    return True, transaction_created, False


def seed():
    with app.app_context():
        admin, admin_created = get_or_create_user(
            {
                "username": "admin",
                "email": "admin@buyme.com",
                "password": "admin123",
                "first_name": "System",
                "last_name": "Administrator",
                "role": "admin",
            }
        )
        db.session.flush()

        created_users = int(admin_created)
        for user_spec in SEED_USERS:
            _, created = get_or_create_user(user_spec)
            created_users += int(created)

        db.session.flush()
        user_map = {
            user.username: user
            for user in User.query.filter(User.username.in_([u["username"] for u in SEED_USERS] + [admin.username])).all()
        }

        leaf_categories, created_categories = ensure_category_tree()
        pruned_categories = prune_obsolete_categories()
        db.session.flush()

        created_auctions = 0
        created_transactions = 0
        updated_auctions = 0
        for auction_spec in get_seed_auction_specs():
            auction_created, transaction_created, auction_updated = create_seed_auction(
                auction_spec,
                user_map,
                leaf_categories,
            )
            created_auctions += int(auction_created)
            created_transactions += int(transaction_created)
            updated_auctions += int(auction_updated)

        db.session.commit()

        total_categories = Category.query.count()
        total_auctions = Auction.query.count()
        total_transactions = Transaction.query.count()

        print("\n[+] Seed complete")
        print(f"[+] Users created this run: {created_users}")
        print(f"[+] Categories created this run: {created_categories}")
        print(f"[+] Categories pruned this run: {pruned_categories}")
        print(f"[+] Auctions created this run: {created_auctions}")
        print(f"[+] Auctions updated this run: {updated_auctions}")
        print(f"[+] Transactions created this run: {created_transactions}")
        print(f"[+] Total categories in database: {total_categories}")
        print(f"[+] Total auctions in database: {total_auctions}")
        print(f"[+] Total completed transactions: {total_transactions}")
        print("\nTest accounts:")
        print("  admin     / admin123")
        for user_spec in SEED_USERS:
            print(f"  {user_spec['username']:<9} / {user_spec['password']}")


if __name__ == "__main__":
    seed()
