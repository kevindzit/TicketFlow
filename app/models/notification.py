from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    technician_id = db.Column(db.Integer, db.ForeignKey('technicians.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    message = db.Column(db.String(500), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    technician = db.relationship('Technician', backref='notifications')
    ticket = db.relationship('Ticket', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.message[:30]}>'
