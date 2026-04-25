import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key')
    _basedir = os.path.abspath(os.path.dirname(__file__))

    # MySQL connection via mysql-connector-python
    MYSQL_USER = os.getenv('MYSQL_USER', 'buyme')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'buyme_pass')
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'buyme')

    # Use MySQL when USE_MYSQL=true in .env, otherwise fall back to SQLite
    USE_MYSQL = os.getenv('USE_MYSQL', 'false').lower() == 'true'

    if USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 3600,
            'pool_pre_ping': True,
        }
    else:
        # SQLite for local dev without Docker
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'buyme.db')
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEM_UPLOAD_SUBDIR = os.path.join('uploads', 'items')
    ITEM_UPLOAD_DIR = os.path.join(_basedir, 'static', ITEM_UPLOAD_SUBDIR)
