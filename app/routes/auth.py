from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
import secrets
from datetime import datetime, timedelta
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()

        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            # in a real app this would send an email
            flash(f'Password reset link: /reset-password/{token}', 'success')
        else:
            flash('If that email exists, a reset link has been sent', 'success')

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if len(new_pw) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('reset_password.html', token=token)

        if new_pw != confirm_pw:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)

        user.password_hash = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@auth_bp.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if not bcrypt.checkpw(current_pw.encode('utf-8'), current_user.password_hash.encode('utf-8')):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('auth.profile'))

    if len(new_pw) < 6:
        flash('New password must be at least 6 characters', 'error')
        return redirect(url_for('auth.profile'))

    if new_pw != confirm_pw:
        flash('New passwords do not match', 'error')
        return redirect(url_for('auth.profile'))

    current_user.password_hash = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()
    flash('Password updated successfully', 'success')
    return redirect(url_for('auth.profile'))
