"""
Admin handler — admin-only operations.

All endpoints require a valid session token AND is_admin=true in members table.

GET  /api/admin?action=members      → full member list including email
POST /api/admin {"action": "set_admin", "user_id": "...", "is_admin": true}
POST /api/admin {"action": "delete_member", "user_id": "..."}
"""
import json
from http.server import BaseHTTPRequestHandler

from api._supabase import db, get_user_from_request, is_admin


def _require_admin(headers):
    """Returns user if valid admin session, None otherwise."""
    user = get_user_from_request(headers)
    if not user:
        return None
    if not is_admin(user.id):
        return None
    return user


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        user = _require_admin(self.headers)
        if not user:
            self._send_error(403, 'Admin access required')
            return

        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        action = params.get('action', [''])[0]

        if action == 'members':
            result = db().table('members').select('*').order('name').execute()
            self._send_success({'members': result.data or []})
        else:
            self._send_error(400, 'Unknown action')

    def do_POST(self):
        user = _require_admin(self.headers)
        if not user:
            self._send_error(403, 'Admin access required')
            return

        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length) or '{}')
        except Exception:
            self._send_error(400, 'Invalid JSON')
            return

        action = data.get('action', '')

        if action == 'set_admin':
            target_id = data.get('user_id', '')
            new_value = bool(data.get('is_admin', False))
            if not target_id:
                self._send_error(400, 'user_id required')
                return
            result = db().table('members').update({'is_admin': new_value}).eq('user_id', target_id).execute()
            self._send_success({'updated': bool(result.data)})

        elif action == 'delete_member':
            target_id = data.get('user_id', '')
            if not target_id:
                self._send_error(400, 'user_id required')
                return
            # Delete from members table; Supabase Auth user remains (can re-join)
            db().table('members').delete().eq('user_id', target_id).execute()
            self._send_success({'deleted': True})

        else:
            self._send_error(400, 'Unknown action')

    def _send_success(self, data: dict):
        body = json.dumps({'success': True, **data}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        body = json.dumps({'success': False, 'error': message}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
