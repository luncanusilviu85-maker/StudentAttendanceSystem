"""
Tests for authentication routes.
Run: pytest tests/
"""

import pytest
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        yield client


def test_login_page_loads(client):
    rv = client.get('/auth/login')
    assert rv.status_code == 200
    assert b'Attendance System' in rv.data


def test_login_redirects_when_authenticated(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        sess['role'] = 'lecturer'
    rv = client.get('/auth/login')
    assert rv.status_code == 302


@patch('routes.auth_routes.User')
def test_login_invalid_credentials(mock_user, client):
    mock_user.get_by_username.return_value = None
    rv = client.post('/auth/login', data={'username': 'bad', 'password': 'wrong'})
    assert rv.status_code == 200
    assert b'Invalid' in rv.data


def test_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    rv = client.get('/auth/logout')
    assert rv.status_code == 302
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
