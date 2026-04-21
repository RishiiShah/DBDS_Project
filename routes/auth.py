from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new end-user account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validation
        errors = []
        if not all([username, email, password, first_name, last_name]):
            errors.append('All fields are required.')
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('auth/register.html',
                                   username=username, email=email,
                                   first_name=first_name, last_name=last_name)

        # Create user
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            password_hash=pw_hash,
            first_name=first_name,
            last_name=last_name,
            role='user',
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Welcome to BuyMe.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and not user.is_active:
            flash('This account has been deactivated. Contact support.', 'error')
            return render_template('auth/login.html', username=username)

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash('Invalid username or password.', 'error')
        return render_template('auth/login.html', username=username)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
