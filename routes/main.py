from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    from models import db
    from models.auction import Auction, Bid
    from models.alert import Alert

    active_listings = Auction.query.filter_by(
        seller_id=current_user.id, status='active'
    ).count()

    active_bids = (
        db.session.query(Bid.auction_id)
        .filter_by(bidder_id=current_user.id)
        .join(Auction, Auction.id == Bid.auction_id)
        .filter(Auction.status == 'active')
        .distinct()
        .count()
    )

    unread_alerts = Alert.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    won_auctions = Auction.query.filter_by(
        status='closed', current_winner_id=current_user.id
    ).count()

    return render_template(
        'dashboard.html',
        active_listings=active_listings,
        active_bids=active_bids,
        unread_alerts=unread_alerts,
        won_auctions=won_auctions,
    )
