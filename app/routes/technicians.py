from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import bcrypt
import json
from app import db
from app.models.technician import Technician
from app.models.user import User
from app.models.ticket import Ticket

technicians_bp = Blueprint('technicians', __name__)

@technicians_bp.route('/technicians')
@login_required
def list_technicians():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    techs = Technician.query.all()
    return render_template('technicians.html', technicians=techs)

@technicians_bp.route('/technicians/add', methods=['GET', 'POST'])
@login_required
def add_technician():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        skills = request.form.getlist('skills')

        if not name or not email:
            flash('Name and email are required', 'error')
            return render_template('technician_form.html', tech=None)

        # create user account for the technician
        pw = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(name=name, email=email, password_hash=pw, role='technician')
        db.session.add(user)
        db.session.commit()

        tech = Technician(
            user_id=user.id,
            name=name,
            email=email,
            skills=json.dumps(skills)
        )
        db.session.add(tech)
        db.session.commit()

        flash(f'Technician {name} added', 'success')
        return redirect(url_for('technicians.list_technicians'))

    return render_template('technician_form.html', tech=None)

@technicians_bp.route('/technicians/edit/<int:tech_id>', methods=['GET', 'POST'])
@login_required
def edit_technician(tech_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    tech = Technician.query.get_or_404(tech_id)

    if request.method == 'POST':
        tech.name = request.form.get('name', '').strip()
        tech.email = request.form.get('email', '').strip()
        skills = request.form.getlist('skills')
        tech.skills = json.dumps(skills)

        if not tech.name or not tech.email:
            flash('Name and email are required', 'error')
            return render_template('technician_form.html', tech=tech)

        # update the linked user too
        user = User.query.get(tech.user_id)
        if user:
            user.name = tech.name
            user.email = tech.email

        db.session.commit()
        flash(f'Technician {tech.name} updated', 'success')
        return redirect(url_for('technicians.list_technicians'))

    return render_template('technician_form.html', tech=tech)

@technicians_bp.route('/technicians/delete/<int:tech_id>', methods=['POST'])
@login_required
def delete_technician(tech_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    tech = Technician.query.get_or_404(tech_id)

    # unassign all their open tickets
    Ticket.query.filter_by(assigned_tech_id=tech.id).update({'assigned_tech_id': None})

    db.session.delete(tech)
    db.session.commit()

    flash(f'Technician {tech.name} deleted', 'success')
    return redirect(url_for('technicians.list_technicians'))
