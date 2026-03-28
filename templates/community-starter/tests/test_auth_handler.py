"""
Tests for api/auth.py
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO


def make_handler(method='POST', path='/api/auth', body=None, headers=None):
    """Build a handler instance with mocked request."""
    from api.auth import handler
    h = handler.__new__(handler)
    h.path = path
    h.headers = headers or {}
    h._responses = []

    def mock_send_response(code):
        h._status = code
    def mock_send_header(k, v):
        pass
    def mock_end_headers():
        pass
    def mock_write(data):
        h._body = data

    h.send_response = mock_send_response
    h.send_header = mock_send_header
    h.end_headers = mock_end_headers

    body_bytes = json.dumps(body or {}).encode() if body else b'{}'
    h.headers['Content-Length'] = str(len(body_bytes))
    h.rfile = BytesIO(body_bytes)
    h.wfile = MagicMock()
    h.wfile.write = mock_write
    return h


class TestLogin:
    def test_login_missing_fields(self):
        h = make_handler(body={'action': 'login'})
        h.do_POST()
        assert h._status == 400

    @patch('api.auth.db')
    def test_login_success(self, mock_db):
        mock_client = MagicMock()
        mock_db.return_value = mock_client

        mock_session = MagicMock()
        mock_session.access_token = 'test_jwt_token'
        mock_user = MagicMock()
        mock_user.id = 'user-123'
        mock_client.auth.sign_in_with_password.return_value = MagicMock(
            session=mock_session,
            user=mock_user,
        )
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={'user_id': 'user-123', 'name': 'Test', 'email': 'test@example.com', 'is_admin': False}
        )

        h = make_handler(body={'action': 'login', 'email': 'test@example.com', 'password': 'secret'})
        h.do_POST()
        assert h._status == 200

    @patch('api.auth.db')
    def test_login_invalid_credentials(self, mock_db):
        mock_db.return_value.auth.sign_in_with_password.side_effect = Exception('Invalid credentials')
        h = make_handler(body={'action': 'login', 'email': 'test@example.com', 'password': 'wrong'})
        h.do_POST()
        assert h._status == 401

    def test_unknown_action(self):
        h = make_handler(body={'action': 'unknown'})
        h.do_POST()
        assert h._status == 400


class TestSession:
    @patch('api.auth.get_user_from_request')
    def test_session_no_token(self, mock_get_user):
        mock_get_user.return_value = None
        h = make_handler(method='GET', path='/api/auth?action=session')
        h.do_GET()
        assert h._status == 401

    @patch('api.auth.db')
    @patch('api.auth.get_user_from_request')
    def test_session_valid(self, mock_get_user, mock_db):
        mock_user = MagicMock()
        mock_user.id = 'user-123'
        mock_get_user.return_value = mock_user

        mock_db.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={'user_id': 'user-123', 'name': 'Test', 'email': 'test@example.com'}
        )

        h = make_handler(method='GET', path='/api/auth?action=session')
        h.headers['Authorization'] = 'Bearer valid_token'
        h.do_GET()
        assert h._status == 200


class TestSensitiveFieldStripping:
    def test_safe_member_strips_sensitive_fields(self):
        from api.auth import handler
        h = handler.__new__(handler)
        member = {
            'user_id': '123',
            'name': 'Test',
            'email': 'test@example.com',
            'is_admin': False,
            'password_hash': 'should_be_stripped',
            'password_reset_token': 'should_be_stripped',
        }
        safe = h._safe_member(member)
        assert 'password_hash' not in safe
        assert 'password_reset_token' not in safe
        assert safe['name'] == 'Test'
        assert safe['email'] == 'test@example.com'
