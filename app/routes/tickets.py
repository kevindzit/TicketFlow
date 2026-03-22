from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.ticket import Ticket, Client, TicketNote

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets')
@login_required
def list_tickets():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets.html', tickets=tickets)

@tickets_bp.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        subject = request.form.get('subject')
        description = request.form.get('description')
        priority = request.form.get('priority', 'Medium')

        ticket = Ticket(
            client_id=client_id,
            subject=subject,
            description=description,
            priority=priority
        )
        db.session.add(ticket)
        db.session.commit()

        flash('Ticket created successfully', 'success')
        return redirect(url_for('tickets.list_tickets'))

    clients = Client.query.all()
    return render_template('new_ticket.html', clients=clients)

@tickets_bp.route('/tickets/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket_detail.html', ticket=ticket)

# api endpoint for ticket intake
@tickets_bp.route('/api/tickets', methods=['POST'])
def api_create_ticket():
    data = request.get_json()

    if not data or not data.get('subject') or not data.get('description'):
        return jsonify({'error': 'Subject and description are required'}), 400

    ticket = Ticket(
        client_id=data.get('client_id', 1),
        subject=data['subject'],
        description=data['description'],
        priority=data.get('priority', 'Medium')
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify({'message': 'Ticket created', 'ticket_id': ticket.id}), 201
