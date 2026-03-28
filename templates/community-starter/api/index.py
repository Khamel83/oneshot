"""
Router — single Vercel function that handles all /{site}/api/* requests.

Parses the request path to extract the site slug and handler name,
sets the Supabase schema context, and dispatches to the appropriate handler module.
"""
import json
from http.server import BaseHTTPRequestHandler

from api._supabase import (
    set_site, db, get_user_from_request,
    parse_request_path, site_exists,
)


HANDLERS = {
    'auth': 'api.handlers.auth',
    'members': 'api.handlers.members',
    'admin': 'api.handlers.admin',
    'email': 'api.handlers.email',
}


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        site, endpoint, params = parse_request_path(self.path)
        request = {'headers': self.headers, 'params': params, 'data': {}}

        # Root path or no site → landing page
        if not site:
            self._serve_file('public/index.html')
            return

        # Unknown site → 404
        if not site_exists(site):
            self._send_error(404, 'Site not found')
            return

        # Set site context for all Supabase queries
        set_site(site)

        # Route to handler
        result = self._dispatch('GET', endpoint, request)
        if result:
            self._send_response(result)
        else:
            self._send_error(400, 'Unknown action')

    def do_POST(self):
        site, endpoint, params = parse_request_path(self.path)

        # Parse JSON body
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length) or '{}')
        except Exception:
            self._send_error(400, 'Invalid JSON')
            return

        # Root POST without site context
        if not site:
            self._send_error(400, 'Site slug required')
            return

        # Unknown site → 404
        if not site_exists(site):
            self._send_error(404, 'Site not found')
            return

        # Set site context
        set_site(site)

        request = {'headers': self.headers, 'params': params, 'data': data}
        result = self._dispatch('POST', endpoint, request)
        if result:
            self._send_response(result)
        else:
            self._send_error(400, 'Unknown action')

    def _dispatch(self, method, endpoint, request):
        """Route to the appropriate handler module."""
        # endpoint is like 'auth' or 'auth?action=session'
        handler_name = endpoint.split('/')[0].split('?')[0]

        module_path = HANDLERS.get(handler_name)
        if not module_path:
            return None

        try:
            parts = module_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[parts[-1]])
            handler_fn = getattr(module, f'handle_{method}', None)
            if handler_fn:
                return handler_fn(request)
        except Exception as e:
            print(f'Handler error ({handler_name}): {e}')
            return (500, {'success': False, 'error': 'Internal server error'})
        return None

    def _serve_file(self, filepath):
        """Serve a static HTML file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            body = content.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self._send_error(404, 'Not found')

    def _send_response(self, result):
        """Send a response from a handler tuple (status_code, body_dict)."""
        status_code, body_dict = result
        body = json.dumps(body_dict).encode()
        self.send_response(status_code)
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
