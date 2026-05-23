"""
Configuration module for Student Attendance Management System.
Loads settings from environment variables (set via AWS Systems Manager / .env).
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ─── Security ────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')

    # ─── Database (AWS RDS MySQL) ─────────────────────────────────────────────
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_PORT     = int(os.environ.get('DB_PORT', 3306))
    DB_NAME     = os.environ.get('DB_NAME', 'attendance_db')
    DB_USER     = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─── AWS S3 (report storage) ──────────────────────────────────────────────
    AWS_REGION        = os.environ.get('AWS_REGION', 'eu-west-1')
    S3_BUCKET_NAME    = os.environ.get('S3_BUCKET_NAME', 'attendance-reports-bucket')
    S3_REPORT_PREFIX  = 'reports/'

    # ─── AWS CloudWatch ───────────────────────────────────────────────────────
    CLOUDWATCH_LOG_GROUP  = '/attendance-system/app'
    CLOUDWATCH_LOG_STREAM = 'flask-app'

    # ─── Session ─────────────────────────────────────────────────────────────
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # ─── Pagination ──────────────────────────────────────────────────────────
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
