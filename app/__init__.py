from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # register blueprints
    from app.routes.auth import auth_bp
    from app.routes.tickets import tickets_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.technicians import technicians_bp
    from app.routes.known_issues import known_issues_bp
    from app.routes.notifications import notifications_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(technicians_bp)
    app.register_blueprint(known_issues_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(reports_bp)

    # inject unread notifications into all templates
    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        from app.models.notification import Notification
        from app.models.technician import Technician

        if not current_user.is_authenticated:
            return {'unread_count': 0, 'recent_notifications': []}

        tech = Technician.query.filter_by(user_id=current_user.id).first()
        if not tech:
            return {'unread_count': 0, 'recent_notifications': []}

        notifs = Notification.query.filter_by(
            technician_id=tech.id, read=False
        ).order_by(Notification.created_at.desc()).limit(10).all()

        return {'unread_count': len(notifs), 'recent_notifications': notifs}

    # create tables if they dont exist
    with app.app_context():
        from app.models import user, ticket, technician, known_issue, calendar_entry, notification, assignment_log
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
