from functools import wraps

from flask import redirect, url_for, flash, abort
from flask_login import current_user


def role_required(*roles):
    """
    Decorator that restricts a route to users with one of the specified roles.
    Usage:
        @role_required('admin')
        @role_required('admin', 'rep')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
