"""
Members handler — list members, view profile.

GET  /api/members                   → public member list (name, avatar only)
GET  /api/members?id=<user_id>      → public profile for one member
GET  /api/members?action=me         → full own profile (auth required)
POST /api/members  {"action": "update_profile", ...}  (auth required)
"""
import json
from http.server import BaseHTTPRequestHandler

from api._supabase import db, get_user_from_request

# Columns returned to the public (no PII)
PUBLIC_COLUMNS = 'user_id,name,avatar_url,bio,joined_at'
# Columns returned to the authenticated member viewing their own profile
OWN_COLUMNS = 'user_id,name,email,avatar_url,bio,joined_at,is_admin'


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        action = params.get('action', [''])[0]
        member_id = params.get('id', [''])[0]

        if action == 'me':
            user = get_user_from_request(self.headers)
            if not user:
                self._send_error(401, 'Authentication required')
                return
            result = db().table('members').select(OWN_COLUMNS).eq('user_id', user.id).single().execute()
            if not result.data:
                self._send_error(404, 'Member not found')
                return
            self._send_success({'member': result.data})

        elif member_id:
            result = db().table('members').select(PUBLIC_COLUMNS).eq('user_id', member_id).single().execute()
            if not result.data:
                self._send_error(404, 'Member not found')
                return
            self._send_success({'member': result.data})

        else:
            # List all members (public columns only)
            result = db().table('members').select(PUBLIC_COLUMNS).order('name').execute()
            self._send_success({'members': result.data or []})

    def do_POST(self):
        user = get_user_from_request(self.headers)
        if not user:
            self._send_error(401, 'Authentication required')
            return

        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length) or '{}')
        except Exception:
            self._send_error(400, 'Invalid JSON')
            return

        action = data.get('action', '')

        if action == 'update_profile':
            self._handle_update_profile(user, data)
        else:
            self._send_error(400, 'Unknown action')

    def _handle_update_profile(self, user, data):
        # Only allow updating safe fields
        allowed = {'name', 'bio', 'avatar_url'}
        updates = {k: v for k, v in data.items() if k in allowed}
        if not updates:
            self._send_error(400, 'No valid fields to update')
            return
        try:
            result = db().table('members').update(updates).eq('user_id', user.id).execute()
            if not result.data:
                self._send_error(500, 'Update failed')
                return
            self._send_success({'member': result.data[0]})
        except Exception as e:
            print(f'Profile update error: {e}')
            self._send_error(500, 'An unexpected error occurred')

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
