# Student Attendance Management System
**SWE5308 Cloud Technologies – Assessment 2 Portfolio**

A cloud-native web application built with Python/Flask and deployed on AWS, implementing full CRUD operations for student attendance tracking.

## Architecture

```
Internet → CloudFront → EC2 (Flask App) → RDS MySQL
                                        ↘ S3 (Reports)
                                        ↘ CloudWatch (Logs)
```

## AWS Services Used

| Service | Purpose |
|---------|---------|
| EC2 (t3.micro) | Hosts the Flask web application |
| RDS MySQL | Stores students, users, and attendance records |
| S3 | Stores exported CSV attendance reports |
| CloudWatch | Application logging and monitoring |
| IAM | Role-based access; no hard-coded credentials |
| CloudFront | CDN + HTTPS termination |

## Features

- **Authentication**: Session-based login with bcrypt password hashing
- **Role-based access**: Admin / Lecturer / Student roles
- **Student management**: Full CRUD (Create, Read, Update, Delete)
- **Attendance marking**: Per-session bulk attendance with Present / Absent / Late status
- **Reports**: Per-student, per-module summaries with Chart.js visualisations
- **CSV export**: Reports uploaded to S3 with 7-day pre-signed download links
- **Low attendance alerts**: Dashboard flags students below 75% attendance

## Project Structure

```
StudentAttendanceSystem/
├── app.py                  # Flask app factory & entry point
├── config.py               # Environment-based configuration
├── requirements.txt        # Python dependencies
├── templates/              # Jinja2 HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── attendance.html
│   └── reports.html
├── static/
│   ├── css/style.css
│   └── js/attendance.js
├── routes/
│   ├── auth_routes.py      # Login / logout / register
│   ├── student_routes.py   # Student CRUD
│   └── attendance_routes.py# Mark, report, export
├── models/
│   ├── student_model.py
│   ├── attendance_model.py
│   └── user_model.py
├── database/
│   └── db_connection.py    # PyMySQL + context manager
├── aws/
│   ├── s3_upload.py        # Boto3 S3 helper
│   ├── cloudwatch.py       # Watchtower logging handler
│   └── iam_config.md       # IAM policy documentation
└── tests/
    ├── test_auth.py
    ├── test_attendance.py
    └── test_database.py
```

## Local Setup

```bash
git clone https://github.com/your-username/student-attendance-system
cd StudentAttendanceSystem
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DB_HOST, DB_PASSWORD, S3_BUCKET_NAME …
python app.py
```

## AWS Deployment

1. Launch EC2 (Amazon Linux 2023, t3.micro) with an IAM instance profile granting S3 + CloudWatch + RDS access.
2. Create RDS MySQL instance (db.t3.micro, Multi-AZ disabled for dev, enabled for prod). Set `Publicly Accessible = false`.
3. Create S3 bucket with Block Public Access enabled.
4. SSH into EC2, clone repo, install dependencies, configure `.env`, run with Gunicorn behind Nginx.
5. Point CloudFront distribution to the EC2 public DNS for HTTPS termination.

## Running Tests

```bash
pytest tests/ -v
```

## Security

- Passwords hashed with bcrypt (work factor 12)
- IAM instance role — no long-lived access keys in code
- S3 reports served via pre-signed URLs (7-day expiry)
- RDS in private subnet; no public endpoint
- Session cookies: Secure + HttpOnly + SameSite=Lax

## References

- Bhowmik, S. (2017) *Cloud Computing*. Cambridge University Press.
- Erl, T., Mahmood, Z. & Puttini, R. (2013) *Cloud Computing: Concepts, Technology & Architecture*. Pearson.
- AWS Documentation — https://docs.aws.amazon.com
- Mell, P. & Grance, T. (2011) *The NIST Definition of Cloud Computing*. NIST SP 800-145.
