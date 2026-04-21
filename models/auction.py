from datetime import datetime

from sqlalchemy import (
    String, Integer, ForeignKey, DateTime, Boolean, Numeric,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from models import db


class Auction(db.Model):
    """
    Represents an auction for a single item.
    The seller sets a starting_price, bid_increment, reserve_price (secret),
    and end_time.  current_price / current_winner_id are denormalized for
    fast reads.
    """
    __tablename__ = 'auctions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('items.id'), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    starting_price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    reserve_price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    bid_increment: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    current_price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    current_winner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum('active', 'closed', 'cancelled', name='auction_status'),
        default='active',
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    item = db.relationship('Item', back_populates='auction')
    seller = db.relationship('User', back_populates='auctions',
                             foreign_keys=[seller_id])
    current_winner = db.relationship('User', foreign_keys=[current_winner_id])
    bids = db.relationship('Bid', back_populates='auction', lazy='dynamic',
                           order_by='Bid.amount.desc()')
    auto_bids = db.relationship('AutoBid', back_populates='auction', lazy='dynamic')
    transaction = db.relationship('Transaction', back_populates='auction',
                                  uselist=False)

    @property
    def is_active(self):
        return self.status == 'active' and self.end_time > datetime.utcnow()

    @property
    def bid_count(self):
        return self.bids.count()

    @property
    def minimum_bid(self):
        """The minimum amount a new bid must be."""
        return float(self.current_price) + float(self.bid_increment)

    def __repr__(self):
        return f'<Auction #{self.id} for Item #{self.item_id}>'


class Bid(db.Model):
    """
    A single bid placed on an auction — either manual or auto-generated.
    """
    __tablename__ = 'bids'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    auction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auctions.id'), nullable=False
    )
    bidder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_auto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    auction = db.relationship('Auction', back_populates='bids')
    bidder = db.relationship('User', back_populates='bids')

    def __repr__(self):
        return f'<Bid ${self.amount} by User #{self.bidder_id}>'


class AutoBid(db.Model):
    """
    Automatic bidding configuration.  The system will bid on behalf of the
    user up to `upper_limit`, incrementing by `bid_increment` each time
    someone outbids them.
    """
    __tablename__ = 'auto_bids'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    auction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auctions.id'), nullable=False
    )
    bidder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    upper_limit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    bid_increment: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    auction = db.relationship('Auction', back_populates='auto_bids')
    bidder = db.relationship('User', back_populates='auto_bids')

    def __repr__(self):
        return f'<AutoBid limit=${self.upper_limit} by User #{self.bidder_id}>'


class Transaction(db.Model):
    """
    Created when an auction closes successfully (reserve met).
    Stores the final price and BuyMe's commission for reporting.
    """
    __tablename__ = 'transactions'

    COMMISSION_RATE = 0.05  # 5%

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    auction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auctions.id'), nullable=False, unique=True
    )
    buyer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    commission: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    auction = db.relationship('Auction', back_populates='transaction')
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])

    def __repr__(self):
        return f'<Transaction ${self.final_price} for Auction #{self.auction_id}>'
