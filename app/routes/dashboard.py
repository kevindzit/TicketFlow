from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.ticket import Ticket
from app.models.technician import Technician
from app.models.notification import Notification

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # get ticket counts by status
    total = Ticket.query.count()
    new_count = Ticket.query.filter_by(status='New').count()
    assigned = Ticket.query.filter_by(status='Assigned').count()
    resolved = Ticket.query.filter_by(status='Resolved').count()

    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()

    # get unread notifications for current user
    notifications = []
    if current_user.role == 'technician':
        tech = Technician.query.filter_by(user_id=current_user.id).first()
        if tech:
            notifications = Notification.query.filter_by(
                technician_id=tech.id, read=False
            ).order_by(Notification.created_at.desc()).all()

    return render_template('dashboard.html',
        total=total,
        new_count=new_count,
        assigned=assigned,
        resolved=resolved,
        recent_tickets=recent_tickets,
        notifications=notifications
    )
