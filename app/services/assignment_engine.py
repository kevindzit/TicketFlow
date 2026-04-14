from datetime import datetime, timedelta
from app import db
from app.models.technician import Technician
from app.models.ticket import Ticket
from app.models.calendar_entry import CalendarEntry
from app.models.notification import Notification
from app.models.assignment_log import AssignmentLog

def get_tech_availability(tech_id):
    now = datetime.utcnow()
    soon = now + timedelta(hours=2)

    # check if busy right now
    busy_now = CalendarEntry.query.filter(
        CalendarEntry.technician_id == tech_id,
        CalendarEntry.start_time <= now,
        CalendarEntry.end_time >= now,
        CalendarEntry.status.in_(['busy', 'out_of_office'])
    ).first()

    if busy_now:
        return 'busy'

    # check if busy within next 2 hours
    busy_soon = CalendarEntry.query.filter(
        CalendarEntry.technician_id == tech_id,
        CalendarEntry.start_time > now,
        CalendarEntry.start_time <= soon,
        CalendarEntry.status.in_(['busy', 'out_of_office'])
    ).first()

    if busy_soon:
        return 'busy_soon'

    return 'available'

def assign_ticket(ticket):
    techs = Technician.query.all()

    # filter to techs whose skills match the ticket category
    matched = []
    for tech in techs:
        skills = tech.get_skills()
        if ticket.category in skills:
            matched.append(tech)

    if not matched:
        ticket.status = 'Pending'
        db.session.commit()
        return None

    # check availability for matched techs
    available = []
    busy_soon = []
    for tech in matched:
        status = get_tech_availability(tech.id)
        if status == 'available':
            available.append(tech)
        elif status == 'busy_soon':
            busy_soon.append(tech)

    # prefer available, then busy_soon, then fall back to all matched
    pool = available or busy_soon or matched

    # pick the tech with fewest open tickets
    best = min(pool, key=lambda t: Ticket.query.filter(
        Ticket.assigned_tech_id == t.id,
        Ticket.status != 'Resolved'
    ).count())

    ticket.assigned_tech_id = best.id
    ticket.status = 'Assigned'

    notif = Notification(
        technician_id=best.id,
        ticket_id=ticket.id,
        message=f'You have been assigned ticket #{ticket.id}: {ticket.subject}'
    )
    db.session.add(notif)

    log = AssignmentLog(
        ticket_id=ticket.id,
        assigned_by='system',
        new_tech_id=best.id
    )
    db.session.add(log)
    db.session.commit()

    return best
