"""
Tests for api/handlers/email.py — CRON_SECRET enforcement + check_recent_send.
"""
import json
import os
import pytest
from unittest.mock import patch, MagicMock


def make_request(body=None, headers=None):
    return {
        'method': 'POST',
        'path': '/api/email',
        'params': {},
        'headers': headers or {},
        'data': body or {},
    }


class TestCronSecretEnforcement:
    def test_no_auth_rejected(self):
        from api.handlers.email import handle_POST
        result = handle_POST(make_request(body={'action': 'send_digest'}))
        assert result[0] == 401

    def test_wrong_secret_rejected(self):
        from api.handlers.email import handle_POST
        result = handle_POST(make_request(
            body={'action': 'send_digest'},
            headers={'Authorization': 'Bearer wrong_secret'},
        ))
        assert result[0] == 401

    @patch('api._supabase.db')
    def test_correct_secret_accepted(self, mock_db):
        secret = os.environ['CRON_SECRET']
        mock_db.return_value.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
        from api.handlers.email import handle_POST
        result = handle_POST(make_request(
            body={'action': 'send_digest'},
            headers={'Authorization': f'Bearer {secret}'},
        ))
        # Auth passed, send_digest returns success with 0 sent (empty members)
        assert result[0] == 200
        assert result[1]['sent'] == 0


class TestCheckRecentSend:
    def test_returns_not_sent_when_empty(self):
        secret = os.environ['CRON_SECRET']
        with patch('api._supabase.db') as mock_db:
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = MagicMock(data=[])
            from api.handlers.email import handle_POST
            result = handle_POST(make_request(
                body={'action': 'check_recent_send', 'email_action': 'send_digest'},
                headers={'Authorization': f'Bearer {secret}'},
            ))
        assert result[0] == 200
        assert result[1]['already_sent'] is False
        assert result[1]['sent'] == 0

    def test_returns_sent_when_log_has_entry(self):
        secret = os.environ['CRON_SECRET']
        with patch('api._supabase.db') as mock_db:
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.execute.return_value = MagicMock(
                data=[{'resend_email_id': 'abc123', 'sent_at': '2026-03-27T10:00:00+00:00'}]
            )
            from api.handlers.email import handle_POST
            result = handle_POST(make_request(
                body={'action': 'check_recent_send', 'email_action': 'send_digest'},
                headers={'Authorization': f'Bearer {secret}'},
            ))
        assert result[0] == 200
        assert result[1]['already_sent'] is True
        assert result[1]['sent'] == 1


class TestHealthCheck:
    def test_get_returns_status(self):
        from api.handlers.email import handle_GET
        result = handle_GET(make_request())
        assert result[0] == 200
        assert result[1]['success'] is True
