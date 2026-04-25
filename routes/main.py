from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    from models.item import Category
    from models.auction import Auction
    from models.user import User

    # Fetch top-level categories
    categories = Category.query.filter_by(level=0).order_by(Category.name).all()
    category_cards = []
    for category in categories:
        child_names = [
            child.name for child in category.children.order_by(Category.name).limit(2).all()
        ]
        category_cards.append(
            {
                'category': category,
                'preview': ' · '.join(child_names) if child_names else 'Curated picks',
            }
        )

    # Fetch 8 active auctions ending soonest
    active_auction_query = Auction.query.filter_by(status='active').filter(
        Auction.end_time > datetime.utcnow()
    )
    featured_auctions = active_auction_query.order_by(
        Auction.end_time.asc()
    ).limit(8).all()

    return render_template(
        'index.html',
        categories=categories,
        category_cards=category_cards,
        featured_auctions=featured_auctions,
        active_auction_count=active_auction_query.count(),
        member_count=User.query.filter_by(role='user').count(),
    )


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
