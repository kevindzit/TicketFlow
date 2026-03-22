from app import db
from datetime import datetime

class KnownIssue(db.Model):
    __tablename__ = 'known_issues'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active or resolved
    suggested_fix = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<KnownIssue {self.title}>'
