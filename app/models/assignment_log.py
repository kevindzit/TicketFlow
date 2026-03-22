from app import db
from datetime import datetime

class AssignmentLog(db.Model):
    __tablename__ = 'assignment_logs'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    assigned_by = db.Column(db.String(50))  # system or admin username
    old_tech_id = db.Column(db.Integer, db.ForeignKey('technicians.id'))
    new_tech_id = db.Column(db.Integer, db.ForeignKey('technicians.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship('Ticket', backref='assignment_history')

    def __repr__(self):
        return f'<AssignmentLog Ticket {self.ticket_id}>'
