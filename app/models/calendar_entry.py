from app import db
from datetime import datetime

class CalendarEntry(db.Model):
    __tablename__ = 'calendar_entries'

    id = db.Column(db.Integer, primary_key=True)
    technician_id = db.Column(db.Integer, db.ForeignKey('technicians.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='busy')  # busy, out_of_office, free

    def __repr__(self):
        return f'<CalendarEntry {self.title}>'
