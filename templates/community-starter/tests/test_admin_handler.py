"""
Tests for api/handlers/admin.py — verifies auth enforcement.
"""
import pytest
from unittest.mock import patch, MagicMock


def make_request(method='GET', body=None, headers=None, params=None):
    return {
        'method': method,
        'path': '/api/admin',
        'params': params or {},
        'headers': headers or {},
        'data': body or {},
    }


class TestAdminAuth:
    def test_no_token_rejected(self):
        from api.handlers.admin import handle_GET
        result = handle_GET(make_request())
        assert result[0] == 403

    @patch('api.handlers.admin.is_admin')
    @patch('api.handlers.admin.get_user_from_request')
    def test_non_admin_rejected(self, mock_get_user, mock_is_admin):
        from api.handlers.admin import handle_GET
        mock_user = MagicMock()
        mock_user.id = 'user-456'
        mock_get_user.return_value = mock_user
        mock_is_admin.return_value = False

        result = handle_GET(make_request(headers={'Authorization': 'Bearer valid_token'}))
        assert result[0] == 403

    @patch('api.handlers.admin.db')
    @patch('api.handlers.admin.is_admin')
    @patch('api.handlers.admin.get_user_from_request')
    def test_admin_can_list_members(self, mock_get_user, mock_is_admin, mock_db):
        from api.handlers.admin import handle_GET
        mock_user = MagicMock()
        mock_user.id = 'admin-123'
        mock_get_user.return_value = mock_user
        mock_is_admin.return_value = True

        mock_db.return_value.table.return_value.select.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{'user_id': 'user-1', 'name': 'Alice', 'email': 'alice@example.com'}]
        )

        result = handle_GET(make_request(headers={'Authorization': 'Bearer admin_token'}, params={'action': ['members']}))
        assert result[0] == 200

    @patch('api.handlers.admin.get_user_from_request')
    def test_post_no_token_rejected(self, mock_get_user):
        mock_get_user.return_value = None
        from api.handlers.admin import handle_POST
        result = handle_POST(make_request(body={'action': 'set_admin', 'user_id': 'x'}))
        assert result[0] == 403
