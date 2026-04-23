"""
WishList trigger — called when a new auction is created.
Checks all active ItemWatch entries and creates Alert('item_available')
for matching users.
"""

from models import db
from models.alert import Alert, ItemWatch


def check_wishlist(new_auction):
    """
    Called when a new auction is created (by routes/auction.py).

    Check all active ItemWatch entries.  If match:
      - keyword found in item.name or item.description
      - category matches (if specified in watch)
      - price in range (if specified)
    Then create Alert('item_available') for that user.
    """
    if not new_auction or not new_auction.item:
        return

    item = new_auction.item
    item_name = (item.name or '').lower()
    item_desc = (item.description or '').lower()
    starting_price = float(new_auction.starting_price)

    watches = ItemWatch.query.filter_by(is_active=True).all()

    for watch in watches:
        # Skip if the watcher is the seller
        if watch.user_id == new_auction.seller_id:
            continue

        # ── Keyword matching ────────────────────────────────────────
        keyword = (watch.keyword or '').lower()
        if keyword and keyword not in item_name and keyword not in item_desc:
            continue  # no keyword match

        # ── Category matching (if specified) ────────────────────────
        if watch.category_id and watch.category_id != item.category_id:
            continue

        # ── Price range matching (if specified) ─────────────────────
        if watch.min_price is not None and starting_price < float(watch.min_price):
            continue
        if watch.max_price is not None and starting_price > float(watch.max_price):
            continue

        # ── All criteria matched — create alert ─────────────────────
        alert = Alert(
            user_id=watch.user_id,
            alert_type='item_available',
            message=f'An item matching your watch "{watch.keyword}" is now available: {item.name}',
            auction_id=new_auction.id,
        )
        db.session.add(alert)

    db.session.commit()
