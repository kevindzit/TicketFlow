# admin only CRUD for known issues that get matched to incoming tickets
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.known_issue import KnownIssue

known_issues_bp = Blueprint('known_issues', __name__)

@known_issues_bp.route('/known-issues')
@login_required
def list_known_issues():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    issues = KnownIssue.query.order_by(KnownIssue.created_at.desc()).all()
    return render_template('known_issues.html', issues=issues)

@known_issues_bp.route('/known-issues/add', methods=['GET', 'POST'])
@login_required
def add_known_issue():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category')
        status = request.form.get('status', 'active')
        suggested_fix = request.form.get('suggested_fix', '').strip()

        if not title or not description:
            flash('Title and description are required', 'error')
            return render_template('known_issue_form.html', issue=None)

        issue = KnownIssue(
            title=title,
            description=description,
            category=category,
            status=status,
            suggested_fix=suggested_fix
        )
        db.session.add(issue)
        db.session.commit()

        flash(f'Known issue "{title}" added', 'success')
        return redirect(url_for('known_issues.list_known_issues'))

    return render_template('known_issue_form.html', issue=None)

@known_issues_bp.route('/known-issues/edit/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def edit_known_issue(issue_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    issue = KnownIssue.query.get_or_404(issue_id)

    if request.method == 'POST':
        issue.title = request.form.get('title', '').strip()
        issue.description = request.form.get('description', '').strip()
        issue.category = request.form.get('category')
        issue.status = request.form.get('status', 'active')
        issue.suggested_fix = request.form.get('suggested_fix', '').strip()

        if not issue.title or not issue.description:
            flash('Title and description are required', 'error')
            return render_template('known_issue_form.html', issue=issue)

        db.session.commit()
        flash(f'Known issue "{issue.title}" updated', 'success')
        return redirect(url_for('known_issues.list_known_issues'))

    return render_template('known_issue_form.html', issue=issue)

@known_issues_bp.route('/known-issues/delete/<int:issue_id>', methods=['POST'])
@login_required
def delete_known_issue(issue_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard.index'))

    issue = KnownIssue.query.get_or_404(issue_id)
    db.session.delete(issue)
    db.session.commit()

    flash(f'Known issue deleted', 'success')
    return redirect(url_for('known_issues.list_known_issues'))
