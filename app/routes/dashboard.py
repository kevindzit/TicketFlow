from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models.ticket import Ticket, Client
from app.models.technician import Technician
from app.models.notification import Notification
from app.services.assignment_engine import get_tech_availability

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return admin_dashboard()
    return tech_dashboard()

def tech_dashboard():
    tech = Technician.query.filter_by(user_id=current_user.id).first()

    tickets = []
    notifications = []
    if tech:
        tickets = Ticket.query.filter_by(assigned_tech_id=tech.id).order_by(Ticket.created_at.desc()).all()
        notifications = Notification.query.filter_by(
            technician_id=tech.id, read=False
        ).order_by(Notification.created_at.desc()).all()

    return render_template('dashboard.html', tickets=tickets, notifications=notifications)

def admin_dashboard():
    query = Ticket.query

    # apply filters
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    urgency_filter = request.args.get('urgency')
    tech_filter = request.args.get('technician')
    client_filter = request.args.get('client')

    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if urgency_filter:
        query = query.filter_by(urgency=urgency_filter)
    if tech_filter:
        query = query.filter_by(assigned_tech_id=tech_filter)
    if client_filter:
        query = query.filter_by(client_id=client_filter)

    tickets = query.order_by(Ticket.created_at.desc()).all()

    total = Ticket.query.count()
    open_count = Ticket.query.filter(Ticket.status != 'Resolved').count()
    resolved = Ticket.query.filter_by(status='Resolved').count()

    technicians = Technician.query.all()
    clients = Client.query.all()

    # build availability map for each tech
    tech_availability = {}
    for tech in technicians:
        tech_availability[tech.id] = get_tech_availability(tech.id)

    return render_template('admin_dashboard.html',
        tickets=tickets,
        total=total,
        open_count=open_count,
        resolved=resolved,
        technicians=technicians,
        clients=clients,
        tech_availability=tech_availability,
        filters={
            'status': status_filter,
            'category': category_filter,
            'urgency': urgency_filter,
            'technician': tech_filter,
            'client': client_filter
        }
    )
