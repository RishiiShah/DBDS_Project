from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import db
from models.user import User
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@role_required('admin')
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_reps  = User.query.filter_by(role='rep').count()
    reps = User.query.filter_by(role='rep').order_by(User.created_at.desc()).all()
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_reps=total_reps,
                           reps=reps)


@admin_bp.route('/reports')
@role_required('admin')
def reports():
    from decimal import Decimal
    from sqlalchemy import func
    from models.auction import Transaction, Auction
    from models.item import Item, Category

    # ── Totals ───────────────────────────────────────────────────
    totals = db.session.query(
        func.count(Transaction.id),
        func.coalesce(func.sum(Transaction.final_price), 0),
        func.coalesce(func.sum(Transaction.commission), 0),
    ).first()
    total_sales, total_revenue, total_commission = totals

    # ── Per item (top 10 by final price) ─────────────────────────
    per_item = (
        db.session.query(Item.name, Transaction.final_price, Transaction.commission)
        .join(Auction, Auction.id == Transaction.auction_id)
        .join(Item, Item.id == Auction.item_id)
        .order_by(Transaction.final_price.desc())
        .limit(10)
        .all()
    )

    # ── Per category ─────────────────────────────────────────────
    per_category = (
        db.session.query(
            Category.name,
            func.count(Transaction.id).label('sales'),
            func.sum(Transaction.final_price).label('revenue'),
        )
        .join(Auction, Auction.id == Transaction.auction_id)
        .join(Item, Item.id == Auction.item_id)
        .join(Category, Category.id == Item.category_id)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.final_price).desc())
        .all()
    )

    # ── Per seller (top earners) ──────────────────────────────────
    from models.user import User
    per_seller = (
        db.session.query(
            User.username,
            func.count(Transaction.id).label('sales'),
            func.sum(Transaction.final_price).label('revenue'),
        )
        .join(User, User.id == Transaction.seller_id)
        .group_by(User.id, User.username)
        .order_by(func.sum(Transaction.final_price).desc())
        .limit(10)
        .all()
    )

    # ── Best buyers (most spent) ──────────────────────────────────
    per_buyer = (
        db.session.query(
            User.username,
            func.count(Transaction.id).label('purchases'),
            func.sum(Transaction.final_price).label('spent'),
        )
        .join(User, User.id == Transaction.buyer_id)
        .group_by(User.id, User.username)
        .order_by(func.sum(Transaction.final_price).desc())
        .limit(10)
        .all()
    )

    return render_template(
        'admin/reports.html',
        total_sales=total_sales,
        total_revenue=total_revenue,
        total_commission=total_commission,
        per_item=per_item,
        per_category=per_category,
        per_seller=per_seller,
        per_buyer=per_buyer,
    )


@admin_bp.route('/create-rep', methods=['GET', 'POST'])
@role_required('admin')
def create_rep():
    if request.method == 'GET':
        return render_template('admin/create_rep.html')

    username   = request.form.get('username', '').strip()
    email      = request.form.get('email', '').strip()
    password   = request.form.get('password', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name  = request.form.get('last_name', '').strip()

    errors = []
    if not username:   errors.append('Username is required.')
    if not email:      errors.append('Email is required.')
    if not password:   errors.append('Password is required.')
    if not first_name: errors.append('First name is required.')
    if not last_name:  errors.append('Last name is required.')

    if not errors:
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already in use.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return render_template('admin/create_rep.html',
                               username=username, email=email,
                               first_name=first_name, last_name=last_name)

    from app import bcrypt
    rep = User(
        username=username,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        first_name=first_name,
        last_name=last_name,
        role='rep',
    )
    db.session.add(rep)
    db.session.commit()

    flash(f'Customer rep "{username}" created successfully.', 'success')
    return redirect(url_for('admin.dashboard'))
