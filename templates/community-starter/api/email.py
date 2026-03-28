"""
Email handler — send transactional emails via Resend.

Protected actions (CRON_SECRET required):
    POST /api/email {"action": "send_digest"}
    POST /api/email {"action": "check_recent_send", "email_action": "send_digest"}

Public:
    GET  /api/email  → health check (is Resend configured?)
"""
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

import resend

# Actions that require CRON_SECRET (called by GitHub Actions, not users)
CRON_ACTIONS = {'send_digest', 'check_recent_send'}


def _init_resend():
    key = os.environ.get('RESEND_API_KEY', '')
    if key:
        resend.api_key = key
    return bool(key)


def send_email(to: str | list, subject: str, html: str) -> str | None:
    """
    Send one email via Resend. Returns Resend email ID on success, None on failure.
    Retries once on rate limit (429).
    """
    _init_resend()
    from_addr = os.environ.get('EMAIL_FROM', 'App <noreply@example.com>')
    reply_to = os.environ.get('REPLY_TO', '')
    params = {
        'from': from_addr,
        'to': [to] if isinstance(to, str) else to,
        'subject': subject,
        'html': html,
    }
    if reply_to:
        params['reply_to'] = reply_to
    try:
        result = resend.Emails.send(params)
        return result.get('id')
    except resend.exceptions.RateLimitError:
        import time
        time.sleep(1)
        try:
            result = resend.Emails.send(params)
            return result.get('id')
        except Exception as e:
            print(f'Email retry failed: {e}')
            return None
    except Exception as e:
        print(f'Email send error: {e}')
        return None


def send_welcome_email(to_email: str, name: str):
    """Send welcome email to new member. Called from auth.py on signup."""
    site_url = os.environ.get('SITE_URL', '')
    html = f"""
    <h2>Welcome, {name}!</h2>
    <p>Your account is ready. <a href="{site_url}/dashboard">Visit your dashboard</a> to get started.</p>
    """
    return send_email(to_email, 'Welcome!', html)


def _log_bulk_send(action: str, to_emails: list, email_id: str = None):
    """Write a row to email_log for audit/idempotency checks."""
    try:
        from api._supabase import db
        db().table('email_log').insert({
            'action': action,
            'to_emails': to_emails,
            'sent_at': datetime.now(timezone.utc).isoformat(),
            'resend_email_id': email_id,
        }).execute()
    except Exception as e:
        print(f'email_log write failed: {e}')


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        configured = _init_resend()
        self._send_success({'status': 'ready' if configured else 'not_configured'})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length) or '{}')
        except Exception:
            self._send_error(400, 'Invalid JSON')
            return

        action = data.get('action', '')

        if action in CRON_ACTIONS:
            cron_secret = os.environ.get('CRON_SECRET', '')
            auth = self.headers.get('Authorization', '').replace('Bearer ', '').strip()
            if not cron_secret or auth != cron_secret:
                self._send_error(401, 'Unauthorized')
                return

        if action == 'send_digest':
            self._handle_send_digest(data)
        elif action == 'check_recent_send':
            self._handle_check_recent_send(data)
        else:
            self._send_error(400, 'Unknown action')

    def _handle_send_digest(self, data):
        """
        Example bulk send: send a weekly digest to all active members.
        Customize this for your use case.
        """
        from api._supabase import db as supabase
        result = supabase().table('members').select('email,name').execute()
        members = result.data or []
        if not members:
            self._send_success({'sent': 0, 'failed': 0})
            return

        sent = 0
        failed = 0
        errors = []
        for member in members:
            email_id = send_email(
                member['email'],
                'Weekly Digest',
                f"<p>Hi {member['name']}, here's your weekly update.</p>",
            )
            if email_id:
                sent += 1
                _log_bulk_send('send_digest', [member['email']], email_id)
            else:
                failed += 1
                errors.append(member['email'])

        if failed > 0:
            self._send_error(500, f'Partial failure', extra={'sent': sent, 'failed': failed, 'errors': errors})
        else:
            self._send_success({'sent': sent, 'failed': 0})

    def _handle_check_recent_send(self, data):
        """
        Check email_log to see if an action already ran today.
        Used by GitHub Actions to verify delivery before declaring 504 a real failure.
        """
        from api._supabase import db as supabase
        check_action = data.get('email_action', '')
        if not check_action:
            self._send_error(400, 'email_action required')
            return
        today_start = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00+00:00')
        result = supabase().table('email_log').select('resend_email_id,sent_at').eq('action', check_action).gte('sent_at', today_start).execute()
        count = len(result.data) if result.data else 0
        self._send_success({'already_sent': count > 0, 'sent': count, 'email_action': check_action})

    def _send_success(self, data: dict):
        body = json.dumps({'success': True, **data}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str, extra: dict = None):
        payload = {'success': False, 'error': message}
        if extra:
            payload.update(extra)
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
