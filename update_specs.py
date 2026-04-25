"""
One-shot script: updates required_fields on every leaf category to match
the 3-spec definitions in seed_catalog.py.  Run once after editing the catalog.

Usage:
    python update_specs.py
"""
from app import create_app
from models import db
from models.item import Category
from seed import ensure_category_tree

app = create_app()

with app.app_context():
    ensure_category_tree()
    db.session.commit()
    print("Category specs updated.")
