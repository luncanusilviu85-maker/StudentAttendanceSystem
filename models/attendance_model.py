"""
Attendance model — records and reporting.
Stores data in AWS RDS; exports uploaded to S3 via s3_upload.py.
"""

import logging
from datetime import date
from database.db_connection import get_db

logger = logging.getLogger(__name__)


class Attendance:

    @staticmethod
    def mark(student_id: str, module: str, att_date: date,
             status: str, marked_by: int, notes: str = ''):
        """
        Insert or update an attendance record (upsert pattern).
        The UNIQUE constraint on (student_id, module, date) prevents duplicates.
        """
        sql = """
            INSERT INTO attendance (student_id, module, date, status, marked_by, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status    = VALUES(status),
                marked_by = VALUES(marked_by),
                notes     = VALUES(notes)
        """
        with get_db() as cursor:
            cursor.execute(sql, (student_id, module, att_date, status, marked_by, notes))
        logger.info("Attendance marked: %s | %s | %s | %s", student_id, module, att_date, status)

    @staticmethod
    def get_by_student(student_id: str, module: str = None):
        sql    = "SELECT * FROM attendance WHERE student_id = %s"
        params = [student_id]
        if module:
            sql   += " AND module = %s"
            params.append(module)
        sql += " ORDER BY date DESC"
        with get_db() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    @staticmethod
    def get_by_date(att_date: date, module: str = None):
        sql    = "SELECT a.*, s.name FROM attendance a JOIN students s USING(student_id) WHERE a.date = %s"
        params = [att_date]
        if module:
            sql   += " AND a.module = %s"
            params.append(module)
        sql += " ORDER BY s.name"
        with get_db() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    @staticmethod
    def get_summary(student_id: str):
        """Returns per-module counts of present / absent / late."""
        sql = """
            SELECT module,
                   SUM(status = 'present') AS present,
                   SUM(status = 'absent')  AS absent,
                   SUM(status = 'late')    AS late,
                   COUNT(*)                AS total
            FROM attendance
            WHERE student_id = %s
            GROUP BY module
        """
        with get_db() as cursor:
            cursor.execute(sql, (student_id,))
            return cursor.fetchall()

    @staticmethod
    def get_overall_stats():
        """Dashboard statistics: totals across all students."""
        sql = """
            SELECT
                COUNT(DISTINCT student_id) AS total_students,
                SUM(status = 'present')    AS total_present,
                SUM(status = 'absent')     AS total_absent,
                SUM(status = 'late')       AS total_late,
                COUNT(*)                   AS total_records
            FROM attendance
        """
        with get_db() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()

    @staticmethod
    def get_low_attendance(threshold: float = 0.75):
        """Students whose attendance rate falls below `threshold`."""
        sql = """
            SELECT student_id,
                   SUM(status = 'present') / COUNT(*) AS rate
            FROM attendance
            GROUP BY student_id
            HAVING rate < %s
            ORDER BY rate ASC
        """
        with get_db() as cursor:
            cursor.execute(sql, (threshold,))
            return cursor.fetchall()
