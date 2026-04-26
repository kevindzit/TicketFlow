# notification dropdown data and mark-as-read actions
from flask import Blueprint, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification
from app.models.technician import Technician

notifications_bp = Blueprint('notifications', __name__)

def get_current_tech():
    return Technician.query.filter_by(user_id=current_user.id).first()

@notifications_bp.route('/notifications')
@login_required
def list_notifications():
    tech = get_current_tech()
    if not tech:
        return jsonify([])

    notifs = Notification.query.filter_by(
        technician_id=tech.id, read=False
    ).order_by(Notification.created_at.desc()).all()

    return jsonify([{
        'id': n.id,
        'message': n.message,
        'ticket_id': n.ticket_id,
        'created_at': n.created_at.strftime('%m/%d/%Y %I:%M %p')
    } for n in notifs])

@notifications_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.read = True
    db.session.commit()

    if notif.ticket_id:
        return redirect(url_for('tickets.view_ticket', ticket_id=notif.ticket_id))
    return redirect(request.referrer or url_for('dashboard.index'))

@notifications_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    tech = get_current_tech()
    if tech:
        Notification.query.filter_by(technician_id=tech.id, read=False).update({'read': True})
        db.session.commit()
    return redirect(request.referrer or url_for('dashboard.index'))
