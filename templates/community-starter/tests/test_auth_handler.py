"""
Tests for api/handlers/auth.py
"""
import pytest
from unittest.mock import patch, MagicMock


def make_request(method='GET', path='/api/auth', body=None, headers=None, params=None):
    """Build a request dict for handler functions."""
    return {
        'method': method,
        'path': path,
        'params': params or {},
        'headers': headers or {},
        'data': body or {},
    }


class TestLogin:
    def test_login_missing_fields(self):
        from api.handlers.auth import handle_POST
        result = handle_POST(make_request(body={'action': 'login'}))
        assert result[0] == 400

    @patch('api.handlers.auth.db')
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

        from api.handlers.auth import handle_POST
        result = handle_POST(make_request(body={'action': 'login', 'email': 'test@example.com', 'password': 'secret'}))
        assert result[0] == 200
        assert result[1]['success'] is True

    @patch('api.handlers.auth.db')
    def test_login_invalid_credentials(self, mock_db):
        mock_db.return_value.auth.sign_in_with_password.side_effect = Exception('Invalid credentials')
        from api.handlers.auth import handle_POST
        result = handle_POST(make_request(body={'action': 'login', 'email': 'test@example.com', 'password': 'wrong'}))
        assert result[0] == 401

    def test_unknown_action(self):
        from api.handlers.auth import handle_POST
        result = handle_POST(make_request(body={'action': 'unknown'}))
        assert result is None


class TestSession:
    @patch('api.handlers.auth.get_user_from_request')
    def test_session_no_token(self, mock_get_user):
        mock_get_user.return_value = None
        from api.handlers.auth import handle_GET
        result = handle_GET(make_request(headers={'Authorization': ''}, params={'action': ['session']}))
        assert result[0] == 401

    @patch('api.handlers.auth.db')
    @patch('api.handlers.auth.get_user_from_request')
    def test_session_valid(self, mock_get_user, mock_db):
        mock_user = MagicMock()
        mock_user.id = 'user-123'
        mock_get_user.return_value = mock_user

        mock_db.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={'user_id': 'user-123', 'name': 'Test', 'email': 'test@example.com'}
        )

        from api.handlers.auth import handle_GET
        result = handle_GET(make_request(headers={'Authorization': 'Bearer valid_token'}, params={'action': ['session']}))
        assert result[0] == 200


class TestSensitiveFieldStripping:
    def test_safe_member_strips_sensitive_fields(self):
        from api.handlers.auth import _safe_member
        member = {
            'user_id': '123',
            'name': 'Test',
            'email': 'test@example.com',
            'is_admin': False,
            'password_hash': 'should_be_stripped',
            'password_reset_token': 'should_be_stripped',
        }
        safe = _safe_member(member)
        assert 'password_hash' not in safe
        assert 'password_reset_token' not in safe
        assert safe['name'] == 'Test'
        assert safe['email'] == 'test@example.com'


class TestPathParsing:
    def test_parse_site_from_path(self):
        from api._supabase import parse_request_path
        site, endpoint, params = parse_request_path('/gambling/api/auth?action=session')
        assert site == 'gambling'
        assert endpoint == 'api/auth'
        assert params == {'action': ['session']}

    def test_parse_no_site(self):
        from api._supabase import parse_request_path
        site, endpoint, params = parse_request_path('/api/system')
        assert site is None
        assert endpoint == 'api/system'

    def test_parse_page_path(self):
        from api._supabase import parse_request_path
        site, endpoint, params = parse_request_path('/gambling/login')
        assert site == 'gambling'
        assert endpoint == 'login'

    def test_parse_root(self):
        from api._supabase import parse_request_path
        site, endpoint, params = parse_request_path('/')
        assert site is None
        assert endpoint == ''
