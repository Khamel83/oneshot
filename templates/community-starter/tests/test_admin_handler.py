"""
Tests for api/admin.py — verifies auth enforcement.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO


def make_handler(method='GET', path='/api/admin', body=None, headers=None):
    from api.admin import handler
    h = handler.__new__(handler)
    h.path = path
    h.headers = headers or {}

    def mock_send_response(code): h._status = code
    def mock_send_header(k, v): pass
    def mock_end_headers(): pass
    def mock_write(data): h._body = data

    h.send_response = mock_send_response
    h.send_header = mock_send_header
    h.end_headers = mock_end_headers

    body_bytes = json.dumps(body or {}).encode()
    h.headers['Content-Length'] = str(len(body_bytes))
    h.rfile = BytesIO(body_bytes)
    h.wfile = MagicMock()
    h.wfile.write = mock_write
    return h


class TestAdminAuth:
    def test_no_token_rejected(self):
        h = make_handler(path='/api/admin?action=members')
        h.do_GET()
        assert h._status == 403

    @patch('api.admin.is_admin')
    @patch('api.admin.get_user_from_request')
    def test_non_admin_rejected(self, mock_get_user, mock_is_admin):
        mock_user = MagicMock()
        mock_user.id = 'user-456'
        mock_get_user.return_value = mock_user
        mock_is_admin.return_value = False

        h = make_handler(path='/api/admin?action=members')
        h.headers['Authorization'] = 'Bearer valid_token'
        h.do_GET()
        assert h._status == 403

    @patch('api.admin.db')
    @patch('api.admin.is_admin')
    @patch('api.admin.get_user_from_request')
    def test_admin_can_list_members(self, mock_get_user, mock_is_admin, mock_db):
        mock_user = MagicMock()
        mock_user.id = 'admin-123'
        mock_get_user.return_value = mock_user
        mock_is_admin.return_value = True

        mock_db.return_value.table.return_value.select.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{'user_id': 'user-1', 'name': 'Alice', 'email': 'alice@example.com'}]
        )

        h = make_handler(path='/api/admin?action=members')
        h.headers['Authorization'] = 'Bearer admin_token'
        h.do_GET()
        assert h._status == 200

    @patch('api.admin.get_user_from_request')
    def test_post_no_token_rejected(self, mock_get_user):
        mock_get_user.return_value = None
        h = make_handler(method='POST', body={'action': 'set_admin', 'user_id': 'x'})
        h.do_POST()
        assert h._status == 403
