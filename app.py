from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from config import Config
from models import db
from models.user import User

login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Extensions ──────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Blueprints ──────────────────────────────────────────────
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.main import main_bp
    app.register_blueprint(main_bp)

    from routes.auction import auction_bp
    app.register_blueprint(auction_bp)

    from routes.search import search_bp
    app.register_blueprint(search_bp)

    from routes.user import user_bp
    app.register_blueprint(user_bp)

    from routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    # ── Create tables ───────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Error handlers ──────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_error(403, 'Forbidden',
                            "You don't have permission to access this page."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_error(404, 'Not Found',
                            "The page you're looking for doesn't exist."), 404

    @app.errorhandler(500)
    def internal(e):
        return render_error(500, 'Server Error',
                            'Something went wrong on our end.'), 500

    return app


def render_error(code, title, message):
    from flask import render_template
    return render_template('error.html', code=code, title=title, message=message)


# ── Entry point ─────────────────────────────────────────────────
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
