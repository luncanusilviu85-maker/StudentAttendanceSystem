"""
Student Attendance Management System
Cloud-Native Flask Application deployed on AWS
SWE5308 - Cloud Technologies Assessment 2
"""

from flask import Flask, redirect, url_for
from config import Config
# from database.db_connection import init_db
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.attendance_routes import attendance_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/students')
app.register_blueprint(attendance_bp, url_prefix='/attendance')


@app.route('/')
def index():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    # init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
