import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)

    # Context processor to inject global variables
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.now(),
            'app_name': app.config.get('APP_NAME', 'Library Management System')
        }
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Register blueprints/routes
    with app.app_context():
        from app import routes
        app.register_blueprint(routes.main_bp)
        db.create_all()
    
    # Register template filters
    register_template_filters(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_template_filters(app):
    """Register custom Jinja2 template filters"""
    
    @app.template_filter('format_date')
    def format_date(value, format='%b %d, %Y'):
        """Format a date object to readable string"""
        if value is None:
            return '—'
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('format_datetime')
    def format_datetime(value, format='%b %d, %Y %H:%M'):
        """Format a datetime object to string"""
        if value is None:
            return '—'
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('days_overdue')
    def days_overdue(due_date):
        """Calculate days overdue from due date"""
        if due_date is None:
            return 0
        today = datetime.now()
        if due_date > today:
            return 0
        delta = (today.date() - due_date.date()).days
        return max(0, delta)
    
    @app.template_filter('calculate_fine')
    def calculate_fine(due_date):
        """Calculate fine based on overdue days"""
        if due_date is None:
            return 0.0
        overdue_days = days_overdue(due_date)
        fine_per_day = app.config.get('OVERDUE_FINE_PER_DAY', 1.0)
        return round(float(overdue_days * fine_per_day), 2)


def register_error_handlers(app):
    """Register error handlers for HTTP errors"""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403