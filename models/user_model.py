"""
User model — authentication and role management.
Passwords are hashed with bcrypt before storage.
"""

import logging
import bcrypt
from database.db_connection import get_db

logger = logging.getLogger(__name__)


class User:
    ROLES = ('admin', 'lecturer', 'student')

    def __init__(self, id, username, email, role):
        self.id       = id
        self.username = username
        self.email    = email
        self.role     = role

    # ─── Auth helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    # ─── Queries ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_username(username: str):
        with get_db() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(user_id: int):
        with get_db() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()

    @staticmethod
    def create(username: str, email: str, plain_password: str, role: str = 'lecturer'):
        hashed = User.hash_password(plain_password)
        sql = """
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, %s)
        """
        with get_db() as cursor:
            cursor.execute(sql, (username, email, hashed, role))
        logger.info("Created user %s (%s)", username, role)

    @staticmethod
    def get_all():
        with get_db() as cursor:
            cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY id")
            return cursor.fetchall()
