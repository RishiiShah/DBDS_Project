"""
User blueprint — profile, my auctions, alerts, and wishlist management.
"""

from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy.orm import joinedload

from models import db
from models.auction import Auction, Bid
from models.alert import Alert, ItemWatch
from models.item import Category

user_bp = Blueprint('user', __name__)


# ═══════════════════════════════════════════════════════════════════════════
#  PROFILE
# ═══════════════════════════════════════════════════════════════════════════

@user_bp.route('/profile')
@login_required
def profile():
    """View current user's profile."""
    return render_template('user/profile.html')


@user_bp.route('/profile/edit', methods=['POST'])
@login_required
def profile_edit():
    """Update first name, last name, email."""
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()

    errors = []
    if not first_name:
        errors.append('First name is required.')
    if not last_name:
        errors.append('Last name is required.')
    if not email:
        errors.append('Email is required.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('user.profile'))

    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email
    db.session.commit()

    flash('Profile updated.', 'success')
    return redirect(url_for('user.profile'))


@user_bp.route('/profile/delete', methods=['POST'])
@login_required
def profile_delete():
    """Soft-delete (is_active=False), then log out."""
    current_user.is_active = False
    db.session.commit()
    logout_user()
    flash('Your account has been deactivated.', 'info')
    return redirect(url_for('main.index'))


# ═══════════════════════════════════════════════════════════════════════════
#  MY AUCTIONS
# ═══════════════════════════════════════════════════════════════════════════

@user_bp.route('/my-auctions')
@login_required
def my_auctions():
    """Auctions I'm selling / bidding on, with tabs."""
    # Selling
    selling = (
        Auction.query
        .options(joinedload(Auction.item))
        .filter_by(seller_id=current_user.id)
        .order_by(Auction.created_at.desc())
        .all()
    )

    # Bidding (active auctions where user has placed bids)
    bidding_ids = (
        db.session.query(Bid.auction_id)
        .filter_by(bidder_id=current_user.id)
        .distinct()
        .subquery()
    )
    bidding = (
        Auction.query
        .options(joinedload(Auction.item))
        .filter(
            Auction.id.in_(db.session.query(bidding_ids)),
            Auction.status == 'active',
        )
        .order_by(Auction.end_time.asc())
        .all()
    )

    # Won (closed auctions where user is current winner)
    won = (
        Auction.query
        .options(joinedload(Auction.item))
        .filter(
            Auction.status == 'closed',
            Auction.current_winner_id == current_user.id,
        )
        .order_by(Auction.end_time.desc())
        .all()
    )

    # Lost (closed auctions where user bid but didn't win)
    lost_ids = (
        db.session.query(Bid.auction_id)
        .filter_by(bidder_id=current_user.id)
        .distinct()
        .subquery()
    )
    lost = (
        Auction.query
        .options(joinedload(Auction.item))
        .filter(
            Auction.id.in_(db.session.query(lost_ids)),
            Auction.status == 'closed',
            Auction.current_winner_id != current_user.id,
        )
        .order_by(Auction.end_time.desc())
        .all()
    )

    return render_template(
        'user/my_auctions.html',
        selling=selling,
        bidding=bidding,
        won=won,
        lost=lost,
    )


@user_bp.route('/user/<int:id>/auctions')
def public_auctions(id):
    """Public view of auctions a specific user participated in."""
    from models.user import User
    user = User.query.get_or_404(id)

    auctions = (
        Auction.query
        .options(joinedload(Auction.item))
        .filter_by(seller_id=id)
        .order_by(Auction.created_at.desc())
        .all()
    )
    return render_template(
        'user/my_auctions.html',
        selling=auctions,
        bidding=[],
        won=[],
        lost=[],
        public_user=user,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  ALERTS
# ═══════════════════════════════════════════════════════════════════════════

@user_bp.route('/alerts')
@login_required
def alerts():
    """All alerts (newest first, paginated)."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = (
        Alert.query
        .filter_by(user_id=current_user.id)
        .order_by(Alert.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('user/alerts.html', pagination=pagination)


@user_bp.route('/alerts/<int:id>/read', methods=['POST'])
@login_required
def mark_alert_read(id):
    """Mark a single alert as read."""
    alert = Alert.query.get_or_404(id)
    if alert.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('user.alerts'))

    alert.is_read = True
    db.session.commit()
    flash('Alert marked as read.', 'success')
    return redirect(url_for('user.alerts'))


@user_bp.route('/alerts/unread-count')
@login_required
def unread_count():
    """JSON: { "count": N }"""
    count = Alert.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


# ═══════════════════════════════════════════════════════════════════════════
#  WISHLIST (ItemWatch)
# ═══════════════════════════════════════════════════════════════════════════

@user_bp.route('/wishlist')
@login_required
def wishlist():
    """My active watches."""
    watches = (
        ItemWatch.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(ItemWatch.created_at.desc())
        .all()
    )
    categories = Category.query.order_by(Category.name).all()
    return render_template('user/wishlist.html', watches=watches, categories=categories)


@user_bp.route('/wishlist/create', methods=['POST'])
@login_required
def wishlist_create():
    """Create a new item watch."""
    keyword = request.form.get('keyword', '').strip()
    category_id = request.form.get('category_id', type=int) or None
    min_price = request.form.get('min_price', type=float) or None
    max_price = request.form.get('max_price', type=float) or None

    if not keyword:
        flash('Keyword is required.', 'error')
        return redirect(url_for('user.wishlist'))

    watch = ItemWatch(
        user_id=current_user.id,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=True,
    )
    db.session.add(watch)
    db.session.commit()

    flash(f'Watch for "{keyword}" created.', 'success')
    return redirect(url_for('user.wishlist'))


@user_bp.route('/wishlist/<int:id>/delete', methods=['POST'])
@login_required
def wishlist_delete(id):
    """Remove a watch."""
    watch = ItemWatch.query.get_or_404(id)
    if watch.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('user.wishlist'))

    watch.is_active = False
    db.session.commit()
    flash('Watch removed.', 'success')
    return redirect(url_for('user.wishlist'))
