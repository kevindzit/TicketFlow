from app import db
import json

class Technician(db.Model):
    __tablename__ = 'technicians'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    skills = db.Column(db.Text)  # stored as json list
    ticket_count = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='technician_profile')
    tickets = db.relationship('Ticket', backref='assigned_tech', lazy=True)
    calendar = db.relationship('CalendarEntry', backref='technician', lazy=True)

    def get_skills(self):
        if self.skills:
            return json.loads(self.skills)
        return []

    def set_skills(self, skill_list):
        self.skills = json.dumps(skill_list)

    def __repr__(self):
        return f'<Technician {self.name}>'
