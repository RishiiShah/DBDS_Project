from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from models import db
from models.auction import Auction, AutoBid, Bid
from models.item import Category, Item, ItemAttribute
from utils.bidding import close_expired_auctions, process_new_bid

auction_bp = Blueprint('auction', __name__)


def _parse_decimal(raw_value: str, field_name: str):
    try:
        value = Decimal(raw_value)
        if value <= 0:
            raise ValueError
        return value
    except (InvalidOperation, ValueError):
        raise ValueError(f'{field_name} must be a positive number.')


def _leaf_categories():
    return Category.query.filter(~Category.children.any()).order_by(Category.name.asc()).all()


@auction_bp.route('/auctions')
def list_auctions():
    close_expired_auctions()
    category_id = request.args.get('category', type=int)

    query = (
        Auction.query.options(joinedload(Auction.item))
        .filter_by(status='active')
        .filter(Auction.end_time > datetime.utcnow())
        .order_by(Auction.end_time.asc())
    )

    if category_id:
        query = query.join(Auction.item).filter(Item.category_id == category_id)

    auctions = query.all()
    categories = _leaf_categories()
    return render_template(
        'auction/list.html',
        auctions=auctions,
        categories=categories,
        selected_category=category_id,
    )


@auction_bp.route('/auction/create', methods=['GET', 'POST'])
@login_required
def create_auction():
    categories = _leaf_categories()

    if request.method == 'GET':
        return render_template('auction/create.html', categories=categories, selected_category=None)

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category_id = request.form.get('category_id', type=int)
    condition = request.form.get('condition', 'good')
    end_time_raw = request.form.get('end_time', '').strip()

    if not category_id:
        flash('Please select a category.', 'error')
        return render_template('auction/create.html', categories=categories, selected_category=None)

    category = Category.query.get_or_404(category_id)

    errors = []
    if not name:
        errors.append('Item name is required.')

    try:
        starting_price = _parse_decimal(request.form.get('starting_price', ''), 'Starting price')
        reserve_price = _parse_decimal(request.form.get('reserve_price', ''), 'Reserve price')
        bid_increment = _parse_decimal(request.form.get('bid_increment', ''), 'Bid increment')
    except ValueError as exc:
        errors.append(str(exc))
        starting_price = reserve_price = bid_increment = None

    if reserve_price is not None and starting_price is not None and reserve_price < starting_price:
        errors.append('Reserve price must be greater than or equal to starting price.')

    try:
        end_time = datetime.strptime(end_time_raw, '%Y-%m-%dT%H:%M')
        if end_time <= datetime.utcnow():
            errors.append('End time must be in the future.')
    except ValueError:
        errors.append('End time is invalid.')
        end_time = None

    required_fields = category.required_fields or []
    item_attributes = []
    for field_name in required_fields:
        field_value = request.form.get(f'attr_{field_name}', '').strip()
        if not field_value:
            errors.append(f'"{field_name}" is required for {category.name}.')
        else:
            item_attributes.append((field_name, field_value))

    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template(
            'auction/create.html',
            categories=categories,
            selected_category=category_id,
            selected_required_fields=required_fields,
        )

    item = Item(
        name=name,
        description=description or None,
        category_id=category.id,
        seller_id=current_user.id,
        condition=condition,
    )
    db.session.add(item)
    db.session.flush()

    for attr_name, attr_value in item_attributes:
        db.session.add(ItemAttribute(item_id=item.id, attr_name=attr_name, attr_value=attr_value))

    auction = Auction(
        item_id=item.id,
        seller_id=current_user.id,
        starting_price=starting_price,
        reserve_price=reserve_price,
        bid_increment=bid_increment,
        current_price=starting_price,
        end_time=end_time,
        status='active',
    )
    db.session.add(auction)
    db.session.commit()

    flash('Auction created successfully.', 'success')
    return redirect(url_for('auction.auction_detail', id=auction.id))


@auction_bp.route('/auction/<int:id>')
def auction_detail(id: int):
    close_expired_auctions()
    auction = Auction.query.options(joinedload(Auction.item)).get_or_404(id)
    bids = (
        Bid.query.filter_by(auction_id=auction.id)
        .order_by(Bid.created_at.desc(), Bid.amount.desc())
        .all()
    )
    return render_template('auction/detail.html', auction=auction, bids=bids)


@auction_bp.route('/auction/<int:id>/bid', methods=['POST'])
@login_required
def place_bid(id: int):
    close_expired_auctions()
    auction = Auction.query.get_or_404(id)

    if not auction.is_active:
        flash('This auction is no longer active.', 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    if auction.seller_id == current_user.id:
        flash('Sellers cannot bid on their own auctions.', 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    raw_amount = request.form.get('amount', '').strip()
    try:
        amount = _parse_decimal(raw_amount, 'Bid amount')
    except ValueError as exc:
        flash(str(exc), 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    minimum = Decimal(str(auction.current_price)) + Decimal(str(auction.bid_increment))
    if amount < minimum:
        flash(f'Bid must be at least ${minimum:.2f}.', 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    process_new_bid(auction, amount, current_user.id)
    flash('Bid placed.', 'success')
    return redirect(url_for('auction.auction_detail', id=id))


@auction_bp.route('/auction/<int:id>/autobid', methods=['POST'])
@login_required
def set_autobid(id: int):
    close_expired_auctions()
    auction = Auction.query.get_or_404(id)

    if not auction.is_active:
        flash('This auction is no longer active.', 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    if auction.seller_id == current_user.id:
        flash('Sellers cannot auto-bid on their own auctions.', 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    raw_limit = request.form.get('upper_limit', '').strip()
    try:
        upper_limit = _parse_decimal(raw_limit, 'Auto-bid upper limit')
    except ValueError as exc:
        flash(str(exc), 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    minimum = Decimal(str(auction.current_price)) + Decimal(str(auction.bid_increment))
    if upper_limit < minimum:
        flash(f'Auto-bid upper limit must be at least ${minimum:.2f}.', 'error')
        return redirect(url_for('auction.auction_detail', id=id))

    auto_bid = AutoBid.query.filter_by(auction_id=id, bidder_id=current_user.id).first()
    if auto_bid:
        auto_bid.upper_limit = upper_limit
        auto_bid.bid_increment = auction.bid_increment
        auto_bid.is_active = True
    else:
        auto_bid = AutoBid(
            auction_id=id,
            bidder_id=current_user.id,
            upper_limit=upper_limit,
            bid_increment=auction.bid_increment,
            is_active=True,
        )
        db.session.add(auto_bid)

    db.session.commit()
    flash('Auto-bid updated.', 'success')
    return redirect(url_for('auction.auction_detail', id=id))


@auction_bp.route('/auction/<int:id>/history')
def bid_history(id: int):
    auction = Auction.query.get_or_404(id)
    bids = (
        Bid.query.filter_by(auction_id=auction.id)
        .order_by(Bid.created_at.desc(), Bid.amount.desc())
        .limit(30)
        .all()
    )
    payload = [
        {
            'id': bid.id,
            'amount': f'{Decimal(str(bid.amount)):.2f}',
            'bidder': bid.bidder.username,
            'is_auto': bid.is_auto,
            'created_at': bid.created_at.isoformat() + 'Z',
        }
        for bid in bids
    ]
    return jsonify(payload)
