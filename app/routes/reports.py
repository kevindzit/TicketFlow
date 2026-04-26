# admin reporting page with summary stats and category/technician breakdowns
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.ticket import Ticket
from app.models.technician import Technician
from app.models.assignment_log import AssignmentLog

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # summary stats
    open_tickets = Ticket.query.filter(Ticket.status != 'Resolved').count()
    resolved_today = Ticket.query.filter(
        Ticket.status == 'Resolved',
        Ticket.updated_at >= today_start
    ).count()
    unassigned = Ticket.query.filter(
        Ticket.assigned_tech_id == None,
        Ticket.status != 'Resolved'
    ).count()

    # average time to assign in hours
    assigned_tickets = Ticket.query.filter(Ticket.assigned_tech_id != None).all()
    total_hours = 0
    count = 0
    for ticket in assigned_tickets:
        log = AssignmentLog.query.filter_by(ticket_id=ticket.id).order_by(AssignmentLog.timestamp.asc()).first()
        if log:
            delta = log.timestamp - ticket.created_at
            total_hours += delta.total_seconds() / 3600
            count += 1
    avg_time_to_assign = round(total_hours / count, 1) if count > 0 else 0

    # category breakdown
    categories = ['Network', 'Hardware', 'Software', 'Security', 'Email', 'Other']
    category_stats = []
    for cat in categories:
        cat_count = Ticket.query.filter(
            Ticket.category == cat,
            Ticket.status != 'Resolved'
        ).count()
        category_stats.append({'name': cat, 'count': cat_count})

    # technician breakdown
    techs = Technician.query.all()
    tech_stats = []
    for tech in techs:
        assigned_count = Ticket.query.filter(
            Ticket.assigned_tech_id == tech.id,
            Ticket.status != 'Resolved'
        ).count()
        resolved_count = Ticket.query.filter(
            Ticket.assigned_tech_id == tech.id,
            Ticket.status == 'Resolved',
            Ticket.updated_at >= week_ago
        ).count()
        tech_stats.append({
            'name': tech.name,
            'assigned': assigned_count,
            'resolved': resolved_count
        })

    return render_template('reports.html',
        open_tickets=open_tickets,
        resolved_today=resolved_today,
        avg_time_to_assign=avg_time_to_assign,
        unassigned=unassigned,
        category_stats=category_stats,
        tech_stats=tech_stats
    )
