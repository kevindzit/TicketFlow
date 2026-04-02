from datetime import datetime
from app import db
from app.models.technician import Technician
from app.models.ticket import Ticket
from app.models.calendar_entry import CalendarEntry
from app.models.notification import Notification
from app.models.assignment_log import AssignmentLog

def assign_ticket(ticket):
    now = datetime.utcnow()

    # get all technicians
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

    # filter out techs who are busy or out of office right now
    available = []
    for tech in matched:
        busy = CalendarEntry.query.filter(
            CalendarEntry.technician_id == tech.id,
            CalendarEntry.start_time <= now,
            CalendarEntry.end_time >= now,
            CalendarEntry.status.in_(['busy', 'out_of_office'])
        ).first()
        if not busy:
            available.append(tech)

    if not available:
        # all matched techs are busy, still assign to least loaded matched tech
        available = matched

    # pick the tech with fewest open tickets
    best = min(available, key=lambda t: Ticket.query.filter(
        Ticket.assigned_tech_id == t.id,
        Ticket.status != 'Resolved'
    ).count())

    ticket.assigned_tech_id = best.id
    ticket.status = 'Assigned'

    # create notification
    notif = Notification(
        technician_id=best.id,
        ticket_id=ticket.id,
        message=f'You have been assigned ticket #{ticket.id}: {ticket.subject}'
    )
    db.session.add(notif)

    # log the assignment
    log = AssignmentLog(
        ticket_id=ticket.id,
        assigned_by='system',
        new_tech_id=best.id
    )
    db.session.add(log)
    db.session.commit()

    return best
