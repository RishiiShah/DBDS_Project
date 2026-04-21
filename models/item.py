from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from models import db


class Category(db.Model):
    """
    Hierarchical category tree for items.
    Uses self-referential FK (parent_id) to support arbitrary depth.
    The `required_fields` JSON column stores field names that must be filled
    when listing an item in this category — this makes adding new categories
    data-driven (no code recompilation needed → bonus points).
    """
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey('categories.id'), nullable=True
    )
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Self-referential relationship
    parent = db.relationship('Category', remote_side='Category.id',
                             backref=db.backref('children', lazy='dynamic'))
    items = db.relationship('Item', back_populates='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name} (level {self.level})>'


class Item(db.Model):
    """
    An item listed for auction on BuyMe.
    Generic fields live here; category-specific fields are in ItemAttribute.
    """
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('categories.id'), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    condition: Mapped[str] = mapped_column(
        SAEnum('new', 'like_new', 'good', 'fair', 'poor', name='item_condition'),
        default='good',
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    category = db.relationship('Category', back_populates='items')
    seller = db.relationship('User', back_populates='items')
    attributes = db.relationship('ItemAttribute', back_populates='item',
                                 cascade='all, delete-orphan', lazy='joined')
    auction = db.relationship('Auction', back_populates='item', uselist=False)

    def get_attribute(self, name):
        """Helper to get a specific attribute value by name."""
        for attr in self.attributes:
            if attr.attr_name == name:
                return attr.attr_value
        return None

    def __repr__(self):
        return f'<Item {self.name}>'


class ItemAttribute(db.Model):
    """
    EAV (Entity-Attribute-Value) pattern for category-specific item fields.
    e.g., { attr_name: "ram", attr_value: "16GB" }
    """
    __tablename__ = 'item_attributes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('items.id'), nullable=False
    )
    attr_name: Mapped[str] = mapped_column(String(100), nullable=False)
    attr_value: Mapped[str] = mapped_column(String(255), nullable=False)

    item = db.relationship('Item', back_populates='attributes')

    def __repr__(self):
        return f'<ItemAttribute {self.attr_name}={self.attr_value}>'
