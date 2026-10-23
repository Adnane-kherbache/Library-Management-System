import os
from datetime import timedelta

# Get the base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings"""
    
    # Secret key for session management and CSRF protection
    # In production, use environment variable: os.environ.get('SECRET_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    
    # Disable SQLAlchemy modification tracking (saves resources)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application settings
    APP_NAME = 'Library Management System'
    
    # Borrowing settings
    DEFAULT_BORROW_DAYS = 14  # Default borrowing period in days
    MAX_BOOKS_PER_MEMBER = 5  # Maximum books a member can borrow at once
    OVERDUE_FINE_PER_DAY = 1.0  # Fine amount per day for overdue books (in currency)
    
    # Pagination settings
    BOOKS_PER_PAGE = 10
    MEMBERS_PER_PAGE = 10
    BORROWS_PER_PAGE = 15
    
    # Upload settings (for book covers)
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Date format
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Flash message categories
    FLASH_SUCCESS = 'success'
    FLASH_ERROR = 'danger'
    FLASH_WARNING = 'warning'
    FLASH_INFO = 'info'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # In production, ensure SECRET_KEY is set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Use PostgreSQL or MySQL in production
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration object based on environment
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Config: Configuration class object
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, DevelopmentConfig)