"""
Tests for database connection module.
"""

import pytest
from unittest.mock import patch, MagicMock


@patch('database.db_connection.pymysql.connect')
def test_get_connection_success(mock_connect):
    from database.db_connection import get_connection
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    conn = get_connection()
    assert conn is mock_conn
    mock_connect.assert_called_once()


@patch('database.db_connection.pymysql.connect')
def test_get_connection_failure(mock_connect):
    import pymysql
    from database.db_connection import get_connection
    mock_connect.side_effect = pymysql.MySQLError("Connection refused")
    with pytest.raises(pymysql.MySQLError):
        get_connection()
