"""
Search & Browse blueprint — category navigation, multi-criteria search,
and similar-items endpoint.
"""

from datetime import datetime

from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload

from models import db
from models.auction import Auction
from models.item import Category, Item, ItemAttribute
from utils.similarity import find_similar

search_bp = Blueprint('search', __name__)


# ── Helpers ──────────────────────────────────────────────────────────────

def _get_all_child_ids(category_id):
    """Return a set containing category_id and all its descendant IDs."""
    ids = {category_id}
    children = Category.query.filter_by(parent_id=category_id).all()
    for child in children:
        ids |= _get_all_child_ids(child.id)
    return ids


def _root_categories():
    """Top-level categories (no parent)."""
    return Category.query.filter_by(parent_id=None).order_by(Category.name).all()


# ── Browse ───────────────────────────────────────────────────────────────

@search_bp.route('/browse')
def browse():
    """Category hierarchy page."""
    categories = _root_categories()
    return render_template('search/browse.html', categories=categories)


@search_bp.route('/browse/<int:category_id>')
def browse_category(category_id):
    """Auctions in a specific category (including child categories)."""
    category = Category.query.get_or_404(category_id)
    cat_ids = _get_all_child_ids(category_id)

    auctions = (
        Auction.query
        .join(Auction.item)
        .options(joinedload(Auction.item))
        .filter(
            Item.category_id.in_(cat_ids),
            Auction.status == 'active',
            Auction.end_time > datetime.utcnow(),
        )
        .order_by(Auction.end_time.asc())
        .all()
    )
    return render_template(
        'search/browse.html',
        categories=_root_categories(),
        selected_category=category,
        auctions=auctions,
    )


# ── Search ───────────────────────────────────────────────────────────────

@search_bp.route('/search')
def search():
    """
    Multi-criteria search with query params:
      ?q=keyword&category_id=5&min_price=100&max_price=500
      &condition=new&sort=price_asc
    """
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    condition = request.args.get('condition', '').strip()
    sort = request.args.get('sort', 'ending_soon').strip()

    query = (
        Auction.query
        .join(Auction.item)
        .options(joinedload(Auction.item))
        .filter(
            Auction.status == 'active',
            Auction.end_time > datetime.utcnow(),
        )
    )

    # ── Keyword ─────────────────────────────────────────────────────
    if q:
        pattern = f'%{q}%'
        query = query.filter(
            db.or_(
                Item.name.ilike(pattern),
                Item.description.ilike(pattern),
            )
        )

    # ── Category (include children) ─────────────────────────────────
    if category_id:
        cat_ids = _get_all_child_ids(category_id)
        query = query.filter(Item.category_id.in_(cat_ids))

    # ── Price range ─────────────────────────────────────────────────
    if min_price is not None:
        query = query.filter(Auction.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Auction.current_price <= max_price)

    # ── Condition ───────────────────────────────────────────────────
    if condition:
        query = query.filter(Item.condition == condition)

    # ── Sort ────────────────────────────────────────────────────────
    sort_map = {
        'price_asc':    Auction.current_price.asc(),
        'price_desc':   Auction.current_price.desc(),
        'ending_soon':  Auction.end_time.asc(),
        'newest':       Auction.created_at.desc(),
    }
    query = query.order_by(sort_map.get(sort, Auction.end_time.asc()))

    auctions = query.all()
    categories = _root_categories()

    return render_template(
        'search/results.html',
        auctions=auctions,
        categories=categories,
        q=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        condition=condition,
        sort=sort,
    )


# ── Similar items ────────────────────────────────────────────────────────

@search_bp.route('/auction/<int:id>/similar')
def similar_items(id):
    """Show similar items to a given auction."""
    auction = Auction.query.options(joinedload(Auction.item)).get_or_404(id)
    similar = find_similar(auction, limit=10)
    return render_template(
        'search/results.html',
        auctions=similar,
        categories=_root_categories(),
        q='',
        category_id=None,
        min_price=None,
        max_price=None,
        condition='',
        sort='',
        similar_to=auction,
    )
