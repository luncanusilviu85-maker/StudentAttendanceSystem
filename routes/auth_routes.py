"""
Authentication routes: login, logout, register.
Session-based auth guarded by role checks.
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from models.user_model import User

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: abort with 403 if user's role is not in allowed roles."""
    from functools import wraps
    from flask import abort
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('attendance.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.get_by_username(username)
        if user and User.verify_password(password, user['password']):
            session.permanent = True
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['role']     = user['role']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('attendance.dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def register():
    """Admin-only: create a new user account."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'lecturer')

        if not all([username, email, password]):
            flash('All fields are required.', 'danger')
        elif role not in User.ROLES:
            flash('Invalid role selected.', 'danger')
        else:
            try:
                User.create(username, email, password, role)
                flash(f"User '{username}' created successfully.", 'success')
                return redirect(url_for('attendance.dashboard'))
            except Exception as exc:
                flash(f"Error creating user: {exc}", 'danger')

    return render_template('login.html', register_mode=True)
