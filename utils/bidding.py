from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from models import db
from models.alert import Alert
from models.auction import Auction, AutoBid, Bid, Transaction


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


def _create_alert(user_id: int, alert_type: str, message: str, auction_id: int | None = None) -> None:
    db.session.add(
        Alert(
            user_id=user_id,
            alert_type=alert_type,
            message=message,
            auction_id=auction_id,
        )
    )


def process_new_bid(auction, bid_amount, bidder_id: int):
    """Save a manual bid and resolve auto-bid competition."""
    increment = _to_decimal(auction.bid_increment)
    bid_amount = _to_decimal(bid_amount)

    manual_bid = Bid(
        auction_id=auction.id,
        bidder_id=bidder_id,
        amount=bid_amount,
        is_auto=False,
    )
    db.session.add(manual_bid)
    db.session.flush()

    min_counter = bid_amount + increment
    active_auto_bids = (
        AutoBid.query.filter_by(auction_id=auction.id, is_active=True)
        .filter(AutoBid.bidder_id != bidder_id)
        .order_by(AutoBid.upper_limit.desc(), AutoBid.created_at.asc())
        .all()
    )

    contenders = []
    for auto_bid in active_auto_bids:
        if _to_decimal(auto_bid.upper_limit) >= min_counter:
            contenders.append(auto_bid)
        else:
            auto_bid.is_active = False
            _create_alert(
                user_id=auto_bid.bidder_id,
                alert_type='auto_bid_exceeded',
                message=f'Auto-bid limit reached on auction #{auction.id}.',
                auction_id=auction.id,
            )

    if not contenders:
        if auction.current_winner_id and auction.current_winner_id != bidder_id:
            _create_alert(
                user_id=auction.current_winner_id,
                alert_type='outbid',
                message=f'You were outbid on auction #{auction.id}.',
                auction_id=auction.id,
            )
        auction.current_price = bid_amount
        auction.current_winner_id = bidder_id
        db.session.commit()
        return manual_bid

    winner_auto_bid = contenders[0]
    winner_amount = min_counter

    if len(contenders) >= 2:
        second_limit = _to_decimal(contenders[1].upper_limit)
        top_limit = _to_decimal(winner_auto_bid.upper_limit)
        winner_amount = min(top_limit, second_limit + increment)

    auto_bid = Bid(
        auction_id=auction.id,
        bidder_id=winner_auto_bid.bidder_id,
        amount=winner_amount,
        is_auto=True,
    )
    db.session.add(auto_bid)

    _create_alert(
        user_id=bidder_id,
        alert_type='outbid',
        message=f'You were outbid on auction #{auction.id}.',
        auction_id=auction.id,
    )

    auction.current_price = winner_amount
    auction.current_winner_id = winner_auto_bid.bidder_id
    db.session.commit()
    return auto_bid


def trigger_autobid_on_register(auction, new_autobid) -> None:
    """
    Resolve auto-bid competition immediately when a new auto-bid is registered.
    Without this, two users setting auto-bids with no manual bid in between
    would leave the price stale and winner unset.
    """
    increment = _to_decimal(auction.bid_increment)
    current = _to_decimal(auction.current_price)
    new_limit = _to_decimal(new_autobid.upper_limit)
    new_bidder_id = new_autobid.bidder_id

    if auction.current_winner_id == new_bidder_id:
        # Already leading — auto-bid just raised our ceiling, nothing to resolve now.
        db.session.commit()
        return

    # Best competing auto-bid (someone other than the new bidder)
    competing = (
        AutoBid.query.filter_by(auction_id=auction.id, is_active=True)
        .filter(AutoBid.bidder_id != new_bidder_id)
        .order_by(AutoBid.upper_limit.desc(), AutoBid.created_at.asc())
        .first()
    )

    if not auction.current_winner_id:
        # No winner yet — new bidder takes the lead at starting/current price.
        db.session.add(Bid(auction_id=auction.id, bidder_id=new_bidder_id,
                           amount=current, is_auto=True))
        auction.current_winner_id = new_bidder_id
        db.session.commit()
        return

    if not competing:
        # Current winner has no auto-bid — new bidder challenges at current + increment.
        challenge = current + increment
        old_winner = auction.current_winner_id
        db.session.add(Bid(auction_id=auction.id, bidder_id=new_bidder_id,
                           amount=challenge, is_auto=True))
        auction.current_price = challenge
        auction.current_winner_id = new_bidder_id
        _create_alert(old_winner, 'outbid',
                      f'You were outbid on auction #{auction.id}.', auction.id)
        db.session.commit()
        return

    # Two auto-bids compete — proxy (eBay-style) resolution.
    competing_limit = _to_decimal(competing.upper_limit)

    if new_limit > competing_limit:
        # New bidder wins.
        winner_amount = min(new_limit, competing_limit + increment)
        db.session.add(Bid(auction_id=auction.id, bidder_id=new_bidder_id,
                           amount=winner_amount, is_auto=True))
        auction.current_price = winner_amount
        auction.current_winner_id = new_bidder_id
        competing.is_active = False
        _create_alert(competing.bidder_id, 'auto_bid_exceeded',
                      f'Auto-bid limit reached on auction #{auction.id}.', auction.id)
    else:
        # Existing auto-bidder retains the lead (tie goes to the earlier bidder).
        winner_amount = min(competing_limit, new_limit + increment)
        db.session.add(Bid(auction_id=auction.id, bidder_id=competing.bidder_id,
                           amount=winner_amount, is_auto=True))
        auction.current_price = winner_amount
        # current_winner_id stays unchanged — existing bidder keeps the lead
        new_autobid.is_active = False
        _create_alert(new_bidder_id, 'auto_bid_exceeded',
                      f'Auto-bid limit reached on auction #{auction.id}.', auction.id)

    db.session.commit()


def close_expired_auctions() -> int:
    """Close active auctions that reached end time and create outcomes."""
    now = datetime.utcnow()
    closed_count = 0
    auctions = (
        Auction.query
        .filter_by(status='active')
        .filter(Auction.end_time <= now)
        .all()
    )

    for auction in auctions:
        auction.status = 'closed'
        closed_count += 1
        current_price = _to_decimal(auction.current_price)
        reserve_price = _to_decimal(auction.reserve_price)

        if auction.current_winner_id and current_price >= reserve_price:
            existing_txn = Transaction.query.filter_by(auction_id=auction.id).first()
            if not existing_txn:
                commission = current_price * Decimal(str(Transaction.COMMISSION_RATE))
                db.session.add(
                    Transaction(
                        auction_id=auction.id,
                        buyer_id=auction.current_winner_id,
                        seller_id=auction.seller_id,
                        final_price=current_price,
                        commission=commission,
                    )
                )
            _create_alert(
                user_id=auction.current_winner_id,
                alert_type='auction_won',
                message=f'You won auction #{auction.id} at ${current_price:.2f}.',
                auction_id=auction.id,
            )
        else:
            _create_alert(
                user_id=auction.seller_id,
                alert_type='auction_lost',
                message=f'Auction #{auction.id} closed without meeting reserve.',
                auction_id=auction.id,
            )
            if auction.current_winner_id:
                _create_alert(
                    user_id=auction.current_winner_id,
                    alert_type='auction_lost',
                    message=f'Auction #{auction.id} closed: reserve was not met.',
                    auction_id=auction.id,
                )

    db.session.commit()
    return closed_count


def recalc_after_bid_removal(auction) -> None:
    """Recalculate denormalized current price/winner after bid deletion."""
    highest_bid = (
        Bid.query.filter_by(auction_id=auction.id)
        .order_by(Bid.amount.desc(), Bid.created_at.asc())
        .first()
    )

    if highest_bid:
        auction.current_price = highest_bid.amount
        auction.current_winner_id = highest_bid.bidder_id
    else:
        auction.current_price = auction.starting_price
        auction.current_winner_id = None

    db.session.commit()
