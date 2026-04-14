from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.ticket import Ticket, Client, TicketNote
from app.services.ai_classifier import classify_ticket, check_known_issues
from app.services.assignment_engine import assign_ticket, get_tech_availability

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets')
@login_required
def list_tickets():
    # filter by status if provided
    status_filter = request.args.get('status')
    if status_filter:
        tickets = Ticket.query.filter_by(status=status_filter).order_by(Ticket.created_at.desc()).all()
    else:
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets.html', tickets=tickets, current_filter=status_filter)

@tickets_bp.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium')

        if not subject or not description:
            flash('Subject and description are required', 'error')
            clients = Client.query.all()
            return render_template('new_ticket.html', clients=clients)

        # run AI classification
        ai_result = classify_ticket(subject, description)

        ticket = Ticket(
            client_id=client_id,
            subject=subject,
            description=description,
            priority=ai_result.get('priority', priority),
            category=ai_result.get('category', 'Other'),
            urgency=ai_result.get('urgency', 'Medium'),
            ai_summary=ai_result.get('summary', ''),
            ai_classified=ai_result.get('ai_classified', True)
        )
        db.session.add(ticket)
        db.session.commit()

        # check for known issues
        matched_issue = check_known_issues(ticket.category, description)
        if matched_issue:
            flash(f'Known issue detected: {matched_issue.title}. Suggested fix: {matched_issue.suggested_fix}', 'success')

        # auto assign to best available technician
        assigned_tech = assign_ticket(ticket)
        if assigned_tech:
            flash(f'Ticket #{ticket.id} created and assigned to {assigned_tech.name}', 'success')
        else:
            flash(f'Ticket #{ticket.id} created. No matching technician available, status set to Pending', 'success')

        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

    clients = Client.query.all()
    return render_template('new_ticket.html', clients=clients)

@tickets_bp.route('/tickets/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    from app.models.technician import Technician
    from app.models.known_issue import KnownIssue
    technicians = Technician.query.all()

    # build open ticket counts and availability, sort by least loaded first
    tech_open_counts = {}
    tech_availability = {}
    for tech in technicians:
        tech_open_counts[tech.id] = Ticket.query.filter(
            Ticket.assigned_tech_id == tech.id,
            Ticket.status != 'Resolved'
        ).count()
        tech_availability[tech.id] = get_tech_availability(tech.id)
    technicians = sorted(technicians, key=lambda t: tech_open_counts[t.id])

    known_issue = None
    if ticket.category:
        known_issue = KnownIssue.query.filter_by(category=ticket.category, status='active').first()
    return render_template('ticket_detail.html', ticket=ticket, technicians=technicians,
                           tech_open_counts=tech_open_counts, tech_availability=tech_availability,
                           known_issue=known_issue)

@tickets_bp.route('/tickets/<int:ticket_id>/note', methods=['POST'])
@login_required
def add_note(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    content = request.form.get('content', '').strip()

    if content:
        note = TicketNote(
            ticket_id=ticket.id,
            author_id=current_user.id,
            content=content
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added', 'success')

    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

@tickets_bp.route('/tickets/<int:ticket_id>/status', methods=['POST'])
@login_required
def update_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form.get('status')
    if new_status:
        ticket.status = new_status
        db.session.commit()
        flash(f'Status updated to {new_status}', 'success')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

# api endpoint for ticket intake
@tickets_bp.route('/api/tickets', methods=['POST'])
def api_create_ticket():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    if not data.get('subject') or not data.get('description'):
        return jsonify({'error': 'Subject and description are required'}), 400

    # validate client exists
    client_id = data.get('client_id')
    if client_id:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': f'Client with id {client_id} not found'}), 400
    else:
        return jsonify({'error': 'client_id is required'}), 400

    # run AI classification on api tickets too
    ai_result = classify_ticket(data['subject'], data['description'])

    ticket = Ticket(
        client_id=client_id,
        subject=data['subject'],
        description=data['description'],
        priority=ai_result.get('priority', 'Medium'),
        category=ai_result.get('category', 'Other'),
        urgency=ai_result.get('urgency', 'Medium'),
        ai_summary=ai_result.get('summary', ''),
        ai_classified=ai_result.get('ai_classified', True)
    )
    db.session.add(ticket)
    db.session.commit()

    assigned_tech = assign_ticket(ticket)

    return jsonify({
        'success': True,
        'message': f'Ticket #{ticket.id} created successfully',
        'ticket_id': ticket.id,
        'assigned_to': assigned_tech.name if assigned_tech else None,
        'status': ticket.status,
        'ai_classification': {
            'category': ticket.category,
            'priority': ticket.priority,
            'urgency': ticket.urgency,
            'summary': ticket.ai_summary
        }
    }), 201
