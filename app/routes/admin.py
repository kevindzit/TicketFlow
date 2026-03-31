from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.ticket import Ticket
from app.models.technician import Technician
from app.models.assignment_log import AssignmentLog

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/assign/<int:ticket_id>', methods=['POST'])
@login_required
def assign_ticket(ticket_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    ticket = Ticket.query.get_or_404(ticket_id)
    new_tech_id = request.form.get('technician_id')

    # log the assignment change
    log = AssignmentLog(
        ticket_id=ticket.id,
        assigned_by=current_user.name,
        old_tech_id=ticket.assigned_tech_id,
        new_tech_id=new_tech_id
    )

    ticket.assigned_tech_id = new_tech_id
    ticket.status = 'Assigned'

    db.session.add(log)
    db.session.commit()

    flash('Ticket reassigned', 'success')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
