"""
Student model — CRUD operations against the students table (AWS RDS).
"""

import logging
from database.db_connection import get_db

logger = logging.getLogger(__name__)


class Student:
    """Represents a student record and provides database helpers."""

    def __init__(self, student_id, name, email, course, year, created_at=None):
        self.student_id = student_id
        self.name       = name
        self.email      = email
        self.course     = course
        self.year       = year
        self.created_at = created_at

    # ─── Queries ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_all(page=1, per_page=20, search=None):
        offset = (page - 1) * per_page
        base   = "SELECT * FROM students"
        params = []

        if search:
            base  += " WHERE name LIKE %s OR student_id LIKE %s OR course LIKE %s"
            term   = f"%{search}%"
            params = [term, term, term]

        base += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params += [per_page, offset]

        with get_db() as cursor:
            cursor.execute(base, params)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(student_id: str):
        with get_db() as cursor:
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            return cursor.fetchone()

    @staticmethod
    def create(student_id, name, email, course, year):
        sql = """
            INSERT INTO students (student_id, name, email, course, year)
            VALUES (%s, %s, %s, %s, %s)
        """
        with get_db() as cursor:
            cursor.execute(sql, (student_id, name, email, course, year))
        logger.info("Created student %s", student_id)

    @staticmethod
    def update(student_id, name, email, course, year):
        sql = """
            UPDATE students
               SET name=%s, email=%s, course=%s, year=%s
             WHERE student_id=%s
        """
        with get_db() as cursor:
            cursor.execute(sql, (name, email, course, year, student_id))
        logger.info("Updated student %s", student_id)

    @staticmethod
    def delete(student_id: str):
        with get_db() as cursor:
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        logger.info("Deleted student %s", student_id)

    @staticmethod
    def count(search=None):
        """Total record count (used for pagination)."""
        sql    = "SELECT COUNT(*) AS total FROM students"
        params = []
        if search:
            sql   += " WHERE name LIKE %s OR student_id LIKE %s OR course LIKE %s"
            term   = f"%{search}%"
            params = [term, term, term]
        with get_db() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row['total']
