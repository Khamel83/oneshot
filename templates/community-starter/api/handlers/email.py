"""Email handler — send transactional emails via Resend."""
import json
import os
from datetime import datetime, timezone

import resend

CRON_ACTIONS = {'send_digest', 'check_recent_send'}


def _init_resend():
    key = os.environ.get('RESEND_API_KEY', '')
    if key:
        resend.api_key = key
    return bool(key)


def send_email(to, subject, html):
    """Send one email via Resend. Returns Resend email ID on success, None on failure."""
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


def send_welcome_email(to_email, name):
    site_url = os.environ.get('SITE_URL', '')
    html = f'<h2>Welcome, {name}!</h2><p>Your account is ready. <a href="{site_url}/dashboard">Visit your dashboard</a> to get started.</p>'
    return send_email(to_email, 'Welcome!', html)


def _log_bulk_send(action, to_emails, email_id=None):
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


def handle_GET(request):
    configured = _init_resend()
    return (200, {'success': True, 'status': 'ready' if configured else 'not_configured'})


def handle_POST(request):
    data = request['data']
    action = data.get('action', '')

    if action in CRON_ACTIONS:
        cron_secret = os.environ.get('CRON_SECRET', '')
        auth = request['headers'].get('Authorization', '').replace('Bearer ', '').strip()
        if not cron_secret or auth != cron_secret:
            return (401, {'success': False, 'error': 'Unauthorized'})
        if action == 'send_digest':
            return _handle_send_digest()
        elif action == 'check_recent_send':
            return _handle_check_recent_send(data)

    return (400, {'success': False, 'error': 'Unknown action'})


def _handle_send_digest():
    from api._supabase import db as supabase
    result = supabase().table('members').select('email,name').execute()
    members = result.data or []
    if not members:
        return (200, {'success': True, 'sent': 0, 'failed': 0})

    sent, failed, errors = 0, 0, []
    for member in members:
        email_id = send_email(member['email'], 'Weekly Digest', f"<p>Hi {member['name']}, here's your weekly update.</p>")
        if email_id:
            sent += 1
            _log_bulk_send('send_digest', [member['email']], email_id)
        else:
            failed += 1
            errors.append(member['email'])

    if failed > 0:
        return (500, {'success': False, 'error': f'Partial failure', 'sent': sent, 'failed': failed, 'errors': errors})
    return (200, {'success': True, 'sent': sent, 'failed': 0})


def _handle_check_recent_send(data):
    from api._supabase import db as supabase
    check_action = data.get('email_action', '')
    if not check_action:
        return (400, {'success': False, 'error': 'email_action required'})
    today_start = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00+00:00')
    result = supabase().table('email_log').select('resend_email_id,sent_at').eq('action', check_action).gte('sent_at', today_start).execute()
    count = len(result.data) if result.data else 0
    return (200, {'success': True, 'already_sent': count > 0, 'sent': count, 'email_action': check_action})
