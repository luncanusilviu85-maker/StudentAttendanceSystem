"""
Student management routes: list, add, edit, delete.
Role-guarded: only admin and lecturers can create/edit/delete.
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, current_app)
from routes.auth_routes import login_required, role_required
from models.student_model import Student

student_bp = Blueprint('students', __name__)


@student_bp.route('/')
@login_required
def list_students():
    page    = request.args.get('page', 1, type=int)
    search  = request.args.get('search', '').strip()
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

    students    = Student.get_all(page=page, per_page=per_page, search=search or None)
    total       = Student.count(search=search or None)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'dashboard.html',
        students=students,
        page=page,
        total_pages=total_pages,
        search=search,
        active='students',
    )


@student_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'lecturer')
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name       = request.form.get('name', '').strip()
        email      = request.form.get('email', '').strip()
        course     = request.form.get('course', '').strip()
        year       = request.form.get('year', 1, type=int)

        if not all([student_id, name, email, course]):
            flash('All fields are required.', 'danger')
        else:
            try:
                Student.create(student_id, name, email, course, year)
                flash(f"Student '{name}' added successfully.", 'success')
                return redirect(url_for('students.list_students'))
            except Exception as exc:
                flash(f"Error: {exc}", 'danger')

    return render_template('dashboard.html', active='add_student')


@student_bp.route('/edit/<string:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'lecturer')
def edit_student(student_id):
    student = Student.get_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.list_students'))

    if request.method == 'POST':
        name   = request.form.get('name', '').strip()
        email  = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()
        year   = request.form.get('year', 1, type=int)

        try:
            Student.update(student_id, name, email, course, year)
            flash('Student updated successfully.', 'success')
            return redirect(url_for('students.list_students'))
        except Exception as exc:
            flash(f"Error: {exc}", 'danger')

    return render_template('dashboard.html', student=student, active='edit_student')


@student_bp.route('/delete/<string:student_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_student(student_id):
    try:
        Student.delete(student_id)
        flash('Student deleted.', 'success')
    except Exception as exc:
        flash(f"Error: {exc}", 'danger')
    return redirect(url_for('students.list_students'))
