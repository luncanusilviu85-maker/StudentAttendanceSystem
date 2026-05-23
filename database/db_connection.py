"""
Database connection module.
Connects to AWS RDS (MySQL) using PyMySQL.
Falls back to SQLite for local development.
"""

import os
import logging
import pymysql
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'port':     int(os.environ.get('DB_PORT', 3306)),
    'user':     os.environ.get('DB_USER', 'admin'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'attendance_db'),
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': False,
}


def get_connection():
    """Open and return a raw PyMySQL connection."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        logger.debug("DB connection established to %s", DB_CONFIG['host'])
        return conn
    except pymysql.MySQLError as exc:
        logger.error("Failed to connect to RDS: %s", exc)
        raise


@contextmanager
def get_db():
    """Context manager: yields a cursor, commits on success, rolls back on error."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't already exist (idempotent)."""
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            username    VARCHAR(80)  NOT NULL UNIQUE,
            email       VARCHAR(120) NOT NULL UNIQUE,
            password    VARCHAR(200) NOT NULL,
            role        ENUM('admin','lecturer','student') NOT NULL DEFAULT 'student',
            created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS students (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            student_id    VARCHAR(20)  NOT NULL UNIQUE,
            name          VARCHAR(100) NOT NULL,
            email         VARCHAR(120) NOT NULL UNIQUE,
            course        VARCHAR(100) NOT NULL,
            year          TINYINT UNSIGNED NOT NULL DEFAULT 1,
            created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            student_id   VARCHAR(20)  NOT NULL,
            module       VARCHAR(100) NOT NULL,
            date         DATE         NOT NULL,
            status       ENUM('present','absent','late') NOT NULL,
            marked_by    INT          NOT NULL,
            notes        TEXT,
            created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (marked_by)  REFERENCES users(id),
            UNIQUE KEY uq_student_module_date (student_id, module, date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ]

    with get_db() as cursor:
        for stmt in ddl_statements:
            cursor.execute(stmt)
    logger.info("Database schema initialised.")
