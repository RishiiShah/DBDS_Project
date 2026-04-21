from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing / home page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Logged-in user dashboard (placeholder for teammates to build out)."""
    return render_template('dashboard.html')
