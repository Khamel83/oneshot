"""
Tests for api/email.py — CRON_SECRET enforcement + check_recent_send.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO


def make_handler(body=None, headers=None):
    from api.email import handler
    h = handler.__new__(handler)
    h.path = '/api/email'
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


class TestCronSecretEnforcement:
    def test_no_auth_rejected(self):
        h = make_handler(body={'action': 'send_digest'})
        h.do_POST()
        assert h._status == 401

    def test_wrong_secret_rejected(self):
        h = make_handler(body={'action': 'send_digest'})
        h.headers['Authorization'] = 'Bearer wrong_secret'
        h.do_POST()
        assert h._status == 401

    def test_correct_secret_accepted(self):
        import os
        secret = os.environ['CRON_SECRET']
        h = make_handler(body={'action': 'send_digest'})
        h.headers['Authorization'] = f'Bearer {secret}'
        # Patch the instance method so it doesn't hit DB
        h._handle_send_digest = lambda data: h._send_success({'sent': 0, 'failed': 0})
        h.do_POST()
        # Should not be 401
        assert h._status != 401


class TestCheckRecentSend:
    def test_returns_not_sent_when_empty(self):
        import os
        secret = os.environ['CRON_SECRET']
        with patch('api._supabase.db') as mock_db:
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = MagicMock(data=[])
            h = make_handler(body={'action': 'check_recent_send', 'email_action': 'send_digest'})
            h.headers['Authorization'] = f'Bearer {secret}'
            h.do_POST()
        assert h._status == 200
        body = json.loads(h._body)
        assert body['already_sent'] is False
        assert body['sent'] == 0

    def test_returns_sent_when_log_has_entry(self):
        import os
        secret = os.environ['CRON_SECRET']
        with patch('api._supabase.db') as mock_db:
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = MagicMock(
                data=[{'resend_email_id': 'abc123', 'sent_at': '2026-03-27T10:00:00+00:00'}]
            )
            h = make_handler(body={'action': 'check_recent_send', 'email_action': 'send_digest'})
            h.headers['Authorization'] = f'Bearer {secret}'
            h.do_POST()
        assert h._status == 200
        body = json.loads(h._body)
        assert body['already_sent'] is True
        assert body['sent'] == 1


class TestHealthCheck:
    def test_get_returns_status(self):
        from api.email import handler
        h = handler.__new__(handler)
        h.path = '/api/email'
        h.headers = {}
        h._status = None
        h._body = None

        def mock_send_response(code): h._status = code
        h.send_response = mock_send_response
        h.send_header = lambda k, v: None
        h.end_headers = lambda: None
        h.wfile = MagicMock()
        h.wfile.write = lambda data: setattr(h, '_body', data)
        h.do_GET()
        assert h._status == 200
