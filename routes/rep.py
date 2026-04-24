from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt

from models import db
from models.auction import Auction, Bid
from models.user import User
from utils.bidding import recalc_after_bid_removal
from utils.decorators import role_required

rep_bp = Blueprint('rep', __name__, url_prefix='/rep')
bcrypt = Bcrypt()


# ── Dashboard ────────────────────────────────────────────────────────────────

@rep_bp.route('/')
@role_required('rep', 'admin')
def dashboard():
    from models.support import Question
    open_questions = Question.query.filter_by(status='open').count()
    total_users = User.query.filter_by(role='user', is_active=True).count()
    active_auctions = Auction.query.filter_by(status='active').count()
    return render_template('rep/dashboard.html',
                           open_questions=open_questions,
                           total_users=total_users,
                           active_auctions=active_auctions)


# ── User management ──────────────────────────────────────────────────────────

@rep_bp.route('/users')
@role_required('rep', 'admin')
def users():
    q = request.args.get('q', '').strip()
    query = User.query.filter_by(role='user')
    if q:
        pattern = f'%{q}%'
        query = query.filter(
            db.or_(
                User.username.ilike(pattern),
                User.email.ilike(pattern),
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
            )
        )
    users = query.order_by(User.created_at.desc()).all()
    return render_template('rep/manage_user.html', users=users, q=q)


@rep_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@role_required('rep', 'admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'user':
        flash('Only end-user accounts can be edited here.', 'error')
        return redirect(url_for('rep.users'))

    first_name = request.form.get('first_name', '').strip()
    last_name  = request.form.get('last_name', '').strip()
    email      = request.form.get('email', '').strip()

    errors = []
    if not first_name: errors.append('First name is required.')
    if not last_name:  errors.append('Last name is required.')
    if not email:      errors.append('Email is required.')

    if not errors:
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user_id:
            errors.append('Email already in use by another account.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('rep.users'))

    user.first_name = first_name
    user.last_name  = last_name
    user.email      = email
    db.session.commit()
    flash(f'Account for "{user.username}" updated.', 'success')
    return redirect(url_for('rep.users'))


@rep_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@role_required('rep', 'admin')
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'user':
        flash('Only end-user passwords can be reset here.', 'error')
        return redirect(url_for('rep.users'))

    new_password = request.form.get('new_password', '').strip()
    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'error')
        return redirect(url_for('rep.users'))

    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    flash(f'Password reset for "{user.username}".', 'success')
    return redirect(url_for('rep.users'))


@rep_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@role_required('rep', 'admin')
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'user':
        flash('Only end-user accounts can be deactivated here.', 'error')
        return redirect(url_for('rep.users'))

    user.is_active = not user.is_active
    status = 'reactivated' if user.is_active else 'deactivated'
    db.session.commit()
    flash(f'Account "{user.username}" {status}.', 'success')
    return redirect(url_for('rep.users'))


# ── Auction / bid management ─────────────────────────────────────────────────

@rep_bp.route('/auctions')
@role_required('rep', 'admin')
def auctions():
    from sqlalchemy.orm import joinedload
    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'active')

    query = (
        Auction.query
        .join(Auction.item)
        .options(joinedload(Auction.item))
    )
    if status_filter in ('active', 'closed', 'cancelled'):
        query = query.filter(Auction.status == status_filter)
    if q:
        from models.item import Item
        query = query.filter(Item.name.ilike(f'%{q}%'))

    auctions = query.order_by(Auction.created_at.desc()).all()
    return render_template('rep/manage_auctions.html',
                           auctions=auctions, q=q, status_filter=status_filter)


@rep_bp.route('/auctions/<int:auction_id>/remove', methods=['POST'])
@role_required('rep', 'admin')
def remove_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    reason = request.form.get('reason', '').strip()

    auction.status = 'cancelled'
    db.session.commit()

    from models.alert import Alert
    if auction.current_winner_id:
        db.session.add(Alert(
            user_id=auction.current_winner_id,
            alert_type='auction_cancelled',
            message=f'Auction #{auction_id} ("{auction.item.name}") was removed by a rep.{" Reason: " + reason if reason else ""}',
            auction_id=auction_id,
        ))
    db.session.add(Alert(
        user_id=auction.seller_id,
        alert_type='auction_cancelled',
        message=f'Your auction #{auction_id} ("{auction.item.name}") was removed by a customer rep.{" Reason: " + reason if reason else ""}',
        auction_id=auction_id,
    ))
    db.session.commit()

    flash(f'Auction #{auction_id} has been removed.', 'success')
    return redirect(url_for('rep.auctions'))


@rep_bp.route('/auctions/<int:auction_id>/bids')
@role_required('rep', 'admin')
def auction_bids(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    bids = (
        Bid.query.filter_by(auction_id=auction_id)
        .order_by(Bid.amount.desc(), Bid.created_at.desc())
        .all()
    )
    return render_template('rep/manage_auctions.html',
                           auctions=Auction.query.filter_by(status='active').all(),
                           selected_auction=auction,
                           bids=bids,
                           q='', status_filter='active')


@rep_bp.route('/bids/<int:bid_id>/remove', methods=['POST'])
@role_required('rep', 'admin')
def remove_bid(bid_id):
    bid = Bid.query.get_or_404(bid_id)
    auction = Auction.query.get_or_404(bid.auction_id)

    if auction.status != 'active':
        flash('Bids can only be removed from active auctions.', 'error')
        return redirect(url_for('rep.auctions'))

    auction_id = bid.auction_id
    bidder_id  = bid.bidder_id

    db.session.delete(bid)
    db.session.flush()
    recalc_after_bid_removal(auction)

    from models.alert import Alert
    db.session.add(Alert(
        user_id=bidder_id,
        alert_type='bid_removed',
        message=f'Your bid on auction #{auction_id} ("{auction.item.name}") was removed by a customer rep.',
        auction_id=auction_id,
    ))
    db.session.commit()

    flash(f'Bid removed from auction #{auction_id}.', 'success')
    return redirect(url_for('rep.auction_bids', auction_id=auction_id))
