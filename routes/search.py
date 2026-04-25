"""
Search & Browse blueprint — category navigation, multi-criteria search,
and similar-items endpoint.
"""

from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for
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


def _browse_params():
    params = {
        'q': request.args.get('q', '').strip(),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float),
        'condition': request.args.get('condition', '').strip(),
        'sort': request.args.get('sort', 'ending_soon').strip(),
    }
    params['attribute_filters'] = {
        key.removeprefix('attr_'): value.strip()
        for key, value in request.args.items()
        if key.startswith('attr_') and value.strip()
    }
    return params


def _selected_category(path_category_id=None):
    category_id = path_category_id or request.args.get('category_id', type=int)
    if not category_id:
        return None
    return Category.query.get_or_404(category_id)


def _category_attribute_fields(category):
    if not category:
        return []

    fields = set(category.required_fields or [])
    for child in category.children.order_by(Category.name).all():
        fields.update(_category_attribute_fields(child))
    return sorted(fields)


def _leaf_descendants(category):
    if not category.children.count():
        return [category]

    leaves = []
    for child in category.children.order_by(Category.name).all():
        leaves.extend(_leaf_descendants(child))
    return leaves


def _root_category_id(category):
    if not category:
        return None
    current = category
    while current.parent_id is not None:
        current = current.parent
    return current.id


def _browse_category_children():
    children = {}
    for root_category in _root_categories():
        unique_children = {}
        for leaf_category in _leaf_descendants(root_category):
            unique_children.setdefault(leaf_category.name, leaf_category)
        children[root_category.id] = [
            unique_children[name]
            for name in sorted(unique_children.keys())
        ]
    return children


def _browse_query(selected_category, q, min_price, max_price, condition, sort, attribute_filters):
    query = (
        Auction.query
        .join(Auction.item)
        .options(joinedload(Auction.item))
        .filter(
            Auction.status == 'active',
            Auction.end_time > datetime.utcnow(),
        )
    )

    if selected_category:
        cat_ids = _get_all_child_ids(selected_category.id)
        query = query.filter(Item.category_id.in_(cat_ids))

    if q:
        pattern = f'%{q}%'
        query = query.filter(
            db.or_(
                Item.name.ilike(pattern),
                Item.description.ilike(pattern),
            )
        )

    if min_price is not None:
        query = query.filter(Auction.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Auction.current_price <= max_price)

    if condition:
        query = query.filter(Item.condition == condition)

    for attr_name, attr_value in attribute_filters.items():
        query = query.filter(
            Item.attributes.any(
                db.and_(
                    ItemAttribute.attr_name == attr_name,
                    ItemAttribute.attr_value.ilike(f'%{attr_value}%'),
                )
            )
        )

    sort_map = {
        'price_asc': Auction.current_price.asc(),
        'price_desc': Auction.current_price.desc(),
        'ending_soon': Auction.end_time.asc(),
        'newest': Auction.created_at.desc(),
    }
    return query.order_by(sort_map.get(sort, Auction.end_time.asc()))


def _render_browse(path_category_id=None):
    params = _browse_params()
    selected_category = _selected_category(path_category_id)
    auctions = _browse_query(selected_category=selected_category, **params).all()
    attribute_fields = _category_attribute_fields(selected_category)
    selected_root_id = _root_category_id(selected_category)
    active_filter_count = sum([
        bool(params['q']),
        params['min_price'] is not None,
        params['max_price'] is not None,
        bool(params['condition']),
        params['sort'] != 'ending_soon',
        len(params['attribute_filters']),
    ])
    has_active_filters = active_filter_count > 0
    return render_template(
        'search/browse.html',
        categories=_root_categories(),
        category_children=_browse_category_children(),
        selected_category=selected_category,
        selected_root_id=selected_root_id,
        auctions=auctions,
        has_active_filters=has_active_filters,
        active_filter_count=active_filter_count,
        available_attribute_fields=attribute_fields,
        **params,
    )


# ── Browse ───────────────────────────────────────────────────────────────

@search_bp.route('/browse')
def browse():
    """Unified browse page with category browsing and advanced filters."""
    return _render_browse()


@search_bp.route('/browse/<int:category_id>')
def browse_category(category_id):
    """Auctions in a specific category (including child categories)."""
    return _render_browse(category_id)


# ── Search ───────────────────────────────────────────────────────────────

@search_bp.route('/search')
def search():
    """Legacy item-search URL now redirects into the unified browse page."""
    return redirect(url_for('search.browse', **request.args.to_dict(flat=True)))


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
