"""
Attendance routes: dashboard, mark attendance, reports.
Reports are generated and uploaded to AWS S3.
"""

import csv
import io
from datetime import date, datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash, send_file, jsonify)
from routes.auth_routes import login_required, role_required
from models.attendance_model import Attendance
from models.student_model import Student
from aws.s3_upload import upload_report_to_s3

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/dashboard')
@login_required
def dashboard():
    stats       = Attendance.get_overall_stats()
    low_att     = Attendance.get_low_attendance(threshold=0.75)
    today_recs  = Attendance.get_by_date(date.today())
    return render_template(
        'dashboard.html',
        stats=stats,
        low_attendance=low_att,
        today_records=today_recs,
        active='dashboard',
    )


@attendance_bp.route('/mark', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'lecturer')
def mark_attendance():
    students = Student.get_all()

    if request.method == 'POST':
        module     = request.form.get('module', '').strip()
        att_date   = request.form.get('date', str(date.today()))
        marked_by  = session['user_id']
        errors     = []

        for student in students:
            sid    = student['student_id']
            status = request.form.get(f'status_{sid}')
            notes  = request.form.get(f'notes_{sid}', '')
            if status not in ('present', 'absent', 'late'):
                continue
            try:
                Attendance.mark(sid, module, att_date, status, marked_by, notes)
            except Exception as exc:
                errors.append(str(exc))

        if errors:
            flash(f"Saved with {len(errors)} error(s): {'; '.join(errors)}", 'warning')
        else:
            flash('Attendance marked successfully.', 'success')
        return redirect(url_for('attendance.dashboard'))

    return render_template(
        'attendance.html',
        students=students,
        today=str(date.today()),
        active='mark',
    )


@attendance_bp.route('/report')
@login_required
def report():
    student_id = request.args.get('student_id')
    module     = request.args.get('module')

    if student_id:
        records  = Attendance.get_by_student(student_id, module)
        summary  = Attendance.get_summary(student_id)
        student  = Student.get_by_id(student_id)
    else:
        records  = []
        summary  = []
        student  = None

    return render_template(
        'reports.html',
        records=records,
        summary=summary,
        student=student,
        active='reports',
    )


@attendance_bp.route('/report/export')
@login_required
def export_csv():
    """Generate a CSV report and upload it to S3; return download link."""
    student_id = request.args.get('student_id', '')
    module     = request.args.get('module', '')
    records    = Attendance.get_by_student(student_id, module) if student_id else []

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=['student_id', 'module', 'date', 'status', 'notes'],
    )
    writer.writeheader()
    for row in records:
        writer.writerow({k: row.get(k, '') for k in writer.fieldnames})

    csv_bytes = buffer.getvalue().encode('utf-8')
    filename  = f"attendance_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    # Upload to S3 and get a pre-signed URL (7-day expiry)
    s3_url = upload_report_to_s3(csv_bytes, filename)
    if s3_url:
        flash(f'Report exported to S3. <a href="{s3_url}" target="_blank">Download here</a>', 'success')
    else:
        # Fallback: serve directly
        return send_file(
            io.BytesIO(csv_bytes),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename,
        )

    return redirect(url_for('attendance.report', student_id=student_id, module=module))


@attendance_bp.route('/api/stats')
@login_required
def api_stats():
    """JSON endpoint consumed by the dashboard Chart.js widget."""
    stats = Attendance.get_overall_stats()
    return jsonify(stats)
