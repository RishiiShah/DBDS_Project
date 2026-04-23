"""
Similar-items scoring algorithm.
Finds active auctions from the past month that are most similar to a given auction.
"""

from datetime import datetime, timedelta

from models import db
from models.auction import Auction
from models.item import Item, ItemAttribute, Category


def _get_child_category_ids(category_id):
    """Return a set of all descendant category IDs (including the given one)."""
    ids = {category_id}
    children = Category.query.filter_by(parent_id=category_id).all()
    for child in children:
        ids |= _get_child_category_ids(child.id)
    return ids


def find_similar(auction, limit=10):
    """
    Score other active auctions from the past month.

    Scoring:
      +40  Same leaf category
      +20  Same parent category (different leaf)
      +20  Price within ±30 % of auction.current_price
      +10  Each matching ItemAttribute (brand, condition …)

    Returns top `limit` auctions sorted by score DESC.
    """
    if not auction or not auction.item:
        return []

    source_item = auction.item
    source_category = source_item.category
    source_price = float(auction.current_price)

    # Collect source attributes as a dict {name: value}
    source_attrs = {
        attr.attr_name.lower(): attr.attr_value.lower()
        for attr in source_item.attributes
    }

    # ── Candidate query: active auctions from the past 30 days ──────────
    cutoff = datetime.utcnow() - timedelta(days=30)
    candidates = (
        Auction.query
        .join(Auction.item)
        .filter(
            Auction.id != auction.id,
            Auction.status == 'active',
            Auction.end_time > datetime.utcnow(),
            Auction.created_at >= cutoff,
        )
        .all()
    )

    scored = []
    for candidate in candidates:
        score = 0
        c_item = candidate.item

        # ── Category scoring ────────────────────────────────────────────
        if c_item.category_id == source_item.category_id:
            score += 40                                        # same leaf
        elif source_category and source_category.parent_id:
            # Same parent category but different leaf
            if c_item.category and c_item.category.parent_id == source_category.parent_id:
                score += 20

        # ── Price scoring ───────────────────────────────────────────────
        c_price = float(candidate.current_price)
        if source_price > 0:
            lower = source_price * 0.7
            upper = source_price * 1.3
            if lower <= c_price <= upper:
                score += 20

        # ── Attribute scoring ───────────────────────────────────────────
        for attr in c_item.attributes:
            key = attr.attr_name.lower()
            val = attr.attr_value.lower()
            if source_attrs.get(key) == val:
                score += 10

        if score > 0:
            scored.append((score, candidate))

    # Sort descending by score, then by auction ID for determinism
    scored.sort(key=lambda x: (-x[0], x[1].id))
    return [auction_obj for _score, auction_obj in scored[:limit]]
