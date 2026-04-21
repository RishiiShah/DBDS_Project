from datetime import datetime

from sqlalchemy import (
    String, Text, Integer, ForeignKey, DateTime, Boolean, Numeric, JSON,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from models import db


class Alert(db.Model):
    """
    In-app notification for a user.
    Types:
      - outbid: someone bid higher on an auction you're in
      - auction_won: you won an auction
      - auction_lost: auction closed and you didn't win (or reserve not met)
      - item_available: an item matching your watch was listed
      - auto_bid_exceeded: someone bid past your auto-bid upper limit
      - custom: a message from a customer rep or system
    """
    __tablename__ = 'alerts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(
        SAEnum('outbid', 'auction_won', 'auction_lost', 'item_available',
               'auto_bid_exceeded', 'custom', name='alert_type'),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auction_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey('auctions.id'), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = db.relationship('User', back_populates='alerts')
    auction = db.relationship('Auction')

    def __repr__(self):
        return f'<Alert [{self.alert_type}] for User #{self.user_id}>'


class ItemWatch(db.Model):
    """
    Lets a user set an alert for items they're interested in.
    When a new auction is created matching the criteria, an alert is generated.
    """
    __tablename__ = 'item_watches'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    keyword: Mapped[str] = mapped_column(String(200), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey('categories.id'), nullable=True
    )
    min_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = db.relationship('User', back_populates='item_watches')
    category = db.relationship('Category')

    def __repr__(self):
        return f'<ItemWatch "{self.keyword}" by User #{self.user_id}>'
