from app import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tickets = db.relationship('Ticket', backref='client', lazy=True)

    def __repr__(self):
        return f'<Client {self.name}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    category = db.Column(db.String(50))  # Network, Hardware, Software, Security, Email, Other
    urgency = db.Column(db.String(20), default='Medium')
    ai_summary = db.Column(db.Text)
    ai_classified = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(30), default='New')  # New, Assigned, In Progress, Waiting on Client, Escalated, Resolved
    assigned_tech_id = db.Column(db.Integer, db.ForeignKey('technicians.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = db.relationship('TicketNote', backref='ticket', lazy=True)

    def __repr__(self):
        return f'<Ticket {self.subject}>'

class TicketNote(db.Model):
    __tablename__ = 'ticket_notes'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='notes')

    def __repr__(self):
        return f'<Note on Ticket {self.ticket_id}>'
