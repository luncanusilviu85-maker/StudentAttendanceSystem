"""
Tests for attendance model and marking routes.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from models.attendance_model import Attendance


class TestAttendanceModel:

    @patch('models.attendance_model.get_db')
    def test_mark_attendance(self, mock_get_db):
        mock_cursor = MagicMock()
        mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_get_db.return_value.__exit__  = MagicMock(return_value=False)

        Attendance.mark('STU001', 'Cloud Technologies', date.today(), 'present', 1)
        assert mock_cursor.execute.called

    @patch('models.attendance_model.get_db')
    def test_get_summary(self, mock_get_db):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'module': 'Cloud Tech', 'present': 8, 'absent': 2, 'late': 0, 'total': 10}
        ]
        mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_get_db.return_value.__exit__  = MagicMock(return_value=False)

        result = Attendance.get_summary('STU001')
        assert len(result) == 1
        assert result[0]['module'] == 'Cloud Tech'

    @patch('models.attendance_model.get_db')
    def test_low_attendance_threshold(self, mock_get_db):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'student_id': 'STU002', 'rate': 0.60}
        ]
        mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_get_db.return_value.__exit__  = MagicMock(return_value=False)

        result = Attendance.get_low_attendance(0.75)
        assert result[0]['rate'] < 0.75
