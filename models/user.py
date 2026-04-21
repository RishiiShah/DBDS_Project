from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from models import db


class User(UserMixin, db.Model):
    """
    Represents all user types in the BuyMe system.
    Roles: 'user' (buyer/seller), 'rep' (customer representative), 'admin'.
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum('user', 'rep', 'admin', name='user_role'),
        default='user',
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    items = db.relationship('Item', back_populates='seller', lazy='dynamic')
    auctions = db.relationship('Auction', back_populates='seller', lazy='dynamic',
                               foreign_keys='Auction.seller_id')
    bids = db.relationship('Bid', back_populates='bidder', lazy='dynamic')
    auto_bids = db.relationship('AutoBid', back_populates='bidder', lazy='dynamic')
    alerts = db.relationship('Alert', back_populates='user', lazy='dynamic')
    item_watches = db.relationship('ItemWatch', back_populates='user', lazy='dynamic')
    questions = db.relationship('Question', back_populates='user', lazy='dynamic')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_rep(self):
        return self.role == 'rep'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
