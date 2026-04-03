"""
System handler — health check, site listing, bug reports.

GET  /api/system                    → health check (DB + email status)
GET  /api/system?action=sites      → list all sites
POST /api/system {"action": "report_bug", "message": "..."}   (auth required)
POST /api/system {"action": "check_email_connectivity"}        (CRON_SECRET required)
"""
import json
import os
from http.server import BaseHTTPRequestHandler

from api._supabase import db, get_user_from_request, _raw_db


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        action = params.get('action', [''])[0]

        if action == 'config':
            return self._handle_site_config()
        if action == 'sites':
            return self._handle_list_sites()

        return self._handle_health_check()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length) or '{}')
        except Exception:
            self._send_error(400, 'Invalid JSON')
            return

        action = data.get('action', '')

        if action == 'report_bug':
            return self._handle_report_bug(data)
        elif action == 'check_email_connectivity':
            return self._handle_check_email_connectivity()

        self._send_error(400, 'Unknown action')

    def _handle_site_config(self):
        """Return theme config for the current site (from public.sites.config)."""
        from api._supabase import get_site
        site = get_site()
        if not site:
            self._send_error(400, 'No site context')
            return
        try:
            result = _raw_db().table('sites').select('slug,name,config').eq('slug', site).single().execute()
            if not result.data:
                self._send_error(404, 'Site not found')
                return
            site_data = result.data
            self._send_success({
                'slug': site_data['slug'],
                'name': site_data.get('name', site_data['slug']),
                'config': site_data.get('config', {}),
            })
        except Exception as e:
            print(f'Site config failed: {e}')
            self._send_error(500, 'Failed to load site config')

    def _handle_health_check(self):
        status = {}
        try:
            # Query public.sites table (always exists) instead of schema-specific table
            _raw_db().table('sites').select('slug').limit(1).execute()
            status['db'] = 'ok'
        except Exception as e:
            print(f'DB health check failed: {e}')
            status['db'] = 'error'

        resend_key = os.environ.get('RESEND_API_KEY', '')
        status['email'] = 'configured' if resend_key else 'not_configured'

        all_ok = all(v in ('ok', 'configured') for v in status.values())
        self._send_success({'status': status, 'healthy': all_ok})

    def _handle_list_sites(self):
        """List all sites from the public.sites table."""
        try:
            result = _raw_db().table('sites').select('slug,name,created_at').order('created_at').execute()
            self._send_success({'sites': result.data or []})
        except Exception as e:
            print(f'Sites list failed: {e}')
            self._send_error(500, 'Failed to list sites')

    def _handle_report_bug(self, data):
        user = get_user_from_request(self.headers)
        if not user:
            self._send_error(401, 'Authentication required')
            return

        message = (data.get('message') or '').strip()
        if not message:
            self._send_error(400, 'Message required')
            return

        admin_email = os.environ.get('ADMIN_EMAIL', '')
        if admin_email:
            try:
                from html import escape as html_escape
                from api.handlers.email import send_email
                send_email(
                    admin_email,
                    'Bug Report',
                    f'<p><strong>From:</strong> {html_escape(user.email)}</p><p>{html_escape(message)}</p>',
                )
            except Exception as e:
                print(f'Bug report email failed: {e}')

        self._send_success({'message': 'Bug report received'})

    def _handle_check_email_connectivity(self):
        cron_secret = os.environ.get('CRON_SECRET', '')
        auth = self.headers.get('Authorization', '').replace('Bearer ', '').strip()
        if not cron_secret or auth != cron_secret:
            self._send_error(401, 'Unauthorized')
            return

        try:
            import resend
            resend.api_key = os.environ.get('RESEND_API_KEY', '')
            resend.ApiKeys.list()
            self._send_success({'email': 'ok'})
        except Exception as e:
            print(f'Email connectivity check failed: {e}')
            self._send_error(500, 'Email not configured or key invalid')

    def _send_success(self, data):
        body = json.dumps({'success': True, **data}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, message):
        body = json.dumps({'success': False, 'error': message}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
