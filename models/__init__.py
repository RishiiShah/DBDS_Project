from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Import all models so they register with SQLAlchemy metadata
from models.user import User                              # noqa: F401, E402
from models.item import Category, Item, ItemAttribute     # noqa: F401, E402
from models.auction import Auction, Bid, AutoBid, Transaction  # noqa: F401, E402
from models.alert import Alert, ItemWatch                 # noqa: F401, E402
from models.support import Question, Answer               # noqa: F401, E402
