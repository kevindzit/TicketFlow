import json
from datetime import datetime, timedelta
import bcrypt
from app import create_app, db
from app.models.user import User
from app.models.ticket import Client, Ticket, TicketNote
from app.models.technician import Technician
from app.models.known_issue import KnownIssue
from app.models.calendar_entry import CalendarEntry
from app.models.notification import Notification

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed():
    app = create_app()
    with app.app_context():
        # clear existing data
        db.drop_all()
        db.create_all()

        pw = hash_password('password123')

        # admin users
        admin1 = User(name='Kevin Dzit', email='kevin@ticketflow.com', password_hash=pw, role='admin')
        admin2 = User(name='Sarah Miller', email='sarah@ticketflow.com', password_hash=pw, role='admin')

        # technician users
        tech_users = [
            User(name='Mike Johnson', email='mike@ticketflow.com', password_hash=pw, role='technician'),
            User(name='Lisa Chen', email='lisa@ticketflow.com', password_hash=pw, role='technician'),
            User(name='James Wilson', email='james@ticketflow.com', password_hash=pw, role='technician'),
            User(name='Maria Garcia', email='maria@ticketflow.com', password_hash=pw, role='technician'),
            User(name='Tom Brown', email='tom@ticketflow.com', password_hash=pw, role='technician'),
        ]

        db.session.add_all([admin1, admin2] + tech_users)
        db.session.commit()

        # technician profiles
        techs = [
            Technician(user_id=tech_users[0].id, name='Mike Johnson', email='mike@ticketflow.com',
                       skills=json.dumps(['Network', 'Firewall', 'VPN']), ticket_count=3),
            Technician(user_id=tech_users[1].id, name='Lisa Chen', email='lisa@ticketflow.com',
                       skills=json.dumps(['Software', 'Email', 'O365']), ticket_count=2),
            Technician(user_id=tech_users[2].id, name='James Wilson', email='james@ticketflow.com',
                       skills=json.dumps(['Hardware', 'Printers', 'Workstations']), ticket_count=1),
            Technician(user_id=tech_users[3].id, name='Maria Garcia', email='maria@ticketflow.com',
                       skills=json.dumps(['Security', 'Network', 'Servers']), ticket_count=4),
            Technician(user_id=tech_users[4].id, name='Tom Brown', email='tom@ticketflow.com',
                       skills=json.dumps(['Software', 'Hardware', 'Backup']), ticket_count=2),
        ]
        db.session.add_all(techs)
        db.session.commit()

        # clients
        clients = [
            Client(name='Acme Corp'),
            Client(name='Meridian Health Group'),
            Client(name='Lakeside Law Firm'),
            Client(name='Summit Financial'),
            Client(name='Greenfield School District'),
        ]
        db.session.add_all(clients)
        db.session.commit()

        # sample tickets
        now = datetime.utcnow()
        tickets = [
            Ticket(client_id=1, subject='Cannot connect to VPN', description='User reports VPN client times out when connecting from home. Started this morning.',
                   priority='High', category='Network', status='Assigned', assigned_tech_id=1, created_at=now - timedelta(days=2)),
            Ticket(client_id=2, subject='Outlook keeps crashing', description='Outlook 365 crashes every time user opens calendar. Tried restarting.',
                   priority='Medium', category='Email', status='In Progress', assigned_tech_id=2, created_at=now - timedelta(days=1)),
            Ticket(client_id=3, subject='Printer not printing', description='Main office printer shows offline. Power cycled, still offline.',
                   priority='Low', category='Hardware', status='New', created_at=now - timedelta(hours=5)),
            Ticket(client_id=4, subject='Suspicious login attempts', description='Getting alerts for failed login attempts from unknown IP on admin account.',
                   priority='Critical', category='Security', status='Assigned', assigned_tech_id=4, created_at=now - timedelta(hours=3)),
            Ticket(client_id=5, subject='Slow internet across campus', description='All buildings reporting slow internet since yesterday. Speedtests show 5mbps down.',
                   priority='High', category='Network', status='New', created_at=now - timedelta(hours=8)),
            Ticket(client_id=1, subject='New employee laptop setup', description='Need a new laptop configured for new hire starting Monday. Standard software package.',
                   priority='Medium', category='Hardware', status='Assigned', assigned_tech_id=3, created_at=now - timedelta(days=3)),
            Ticket(client_id=2, subject='Backup job failed', description='Nightly backup job failed with error code 0x80070005. Access denied on network share.',
                   priority='High', category='Software', status='In Progress', assigned_tech_id=5, created_at=now - timedelta(days=1)),
            Ticket(client_id=3, subject='Cannot access shared drive', description='Users in accounting department cannot map to S: drive. Other departments are fine.',
                   priority='Medium', category='Network', status='New', created_at=now - timedelta(hours=2)),
            Ticket(client_id=4, subject='MFA not working', description='CEO cannot receive MFA codes on phone. Tried multiple times. Need urgent fix.',
                   priority='Critical', category='Security', status='Escalated', assigned_tech_id=4, created_at=now - timedelta(hours=1)),
            Ticket(client_id=5, subject='Software update needed', description='Adobe Acrobat needs to be updated on all teacher workstations. About 30 machines.',
                   priority='Low', category='Software', status='Resolved', assigned_tech_id=5, created_at=now - timedelta(days=5)),
        ]
        db.session.add_all(tickets)
        db.session.commit()

        # known issues
        issues = [
            KnownIssue(title='Outlook 365 Calendar Crash', description='Known bug in Outlook build 16.0.17328 causes crash when opening calendar with recurring events.',
                       category='Email', status='active', suggested_fix='Update to latest Outlook build or clear calendar cache.'),
            KnownIssue(title='VPN Timeout on Windows 11', description='Cisco AnyConnect VPN times out on Windows 11 23H2 after recent update.',
                       category='Network', status='active', suggested_fix='Downgrade AnyConnect to version 4.10 or apply registry fix KB5034123.'),
            KnownIssue(title='Printer Offline After Firmware Update', description='HP LaserJet printers go offline after firmware update pushed last week.',
                       category='Hardware', status='active', suggested_fix='Roll back firmware to previous version using HP Web Jetadmin.'),
            KnownIssue(title='Backup Error 0x80070005', description='Access denied error on backup jobs after server patching.',
                       category='Software', status='active', suggested_fix='Reset service account permissions on backup share.'),
            KnownIssue(title='O365 Sync Issues Resolved', description='OneDrive sync issues from last month have been resolved by Microsoft.',
                       category='Software', status='resolved', suggested_fix='No action needed. Issue resolved server side.'),
        ]
        db.session.add_all(issues)
        db.session.commit()

        # calendar entries for technicians across the next 7 days
        pto_days = [3, 5, 2, 6, 4]  # different PTO day offset for each tech

        for i, tech in enumerate(techs):
            entries = []
            for day_offset in range(7):
                day = now + timedelta(days=day_offset)
                base = day.replace(hour=0, minute=0, second=0, microsecond=0)

                # morning standup every day
                entries.append(CalendarEntry(technician_id=tech.id, title='Morning standup',
                    start_time=base.replace(hour=9, minute=0), end_time=base.replace(hour=9, minute=30), status='busy'))

                # lunch every day
                entries.append(CalendarEntry(technician_id=tech.id, title='Lunch',
                    start_time=base.replace(hour=12, minute=0), end_time=base.replace(hour=13, minute=0), status='busy'))

                # PTO day for this tech
                if day_offset == pto_days[i]:
                    entries.append(CalendarEntry(technician_id=tech.id, title='Out of office',
                        start_time=base.replace(hour=8, minute=0), end_time=base.replace(hour=17, minute=0), status='out_of_office'))
                    continue

                # afternoon meetings on certain days
                if day_offset % 2 == 0:
                    entries.append(CalendarEntry(technician_id=tech.id, title='Client meeting',
                        start_time=base.replace(hour=14, minute=0), end_time=base.replace(hour=15, minute=0), status='busy'))

                if day_offset % 3 == 0:
                    entries.append(CalendarEntry(technician_id=tech.id, title='Training session',
                        start_time=base.replace(hour=15, minute=30), end_time=base.replace(hour=16, minute=30), status='busy'))

                if day_offset == 1:
                    entries.append(CalendarEntry(technician_id=tech.id, title='Project review',
                        start_time=base.replace(hour=10, minute=0), end_time=base.replace(hour=11, minute=0), status='busy'))

            db.session.add_all(entries)

        db.session.commit()

        # notifications
        notifs = [
            Notification(technician_id=1, ticket_id=1, message='You have been assigned ticket #1: Cannot connect to VPN'),
            Notification(technician_id=2, ticket_id=2, message='You have been assigned ticket #2: Outlook keeps crashing'),
            Notification(technician_id=4, ticket_id=4, message='URGENT: You have been assigned ticket #4: Suspicious login attempts'),
            Notification(technician_id=4, ticket_id=9, message='URGENT: You have been assigned ticket #9: MFA not working'),
            Notification(technician_id=3, ticket_id=6, message='You have been assigned ticket #6: New employee laptop setup'),
        ]
        db.session.add_all(notifs)
        db.session.commit()

        print('Database seeded successfully')
        print(f'  {User.query.count()} users')
        print(f'  {Technician.query.count()} technicians')
        print(f'  {Client.query.count()} clients')
        print(f'  {Ticket.query.count()} tickets')
        print(f'  {KnownIssue.query.count()} known issues')
        print(f'  {CalendarEntry.query.count()} calendar entries')
        print(f'  {Notification.query.count()} notifications')

if __name__ == '__main__':
    seed()
