#!/usr/bin/env python3
"""
Serves the investor report analyzer and proxies Anthropic API calls.
Run with: python3 server.py
Then open: http://localhost:8080/investor-report-analyzer.html
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.request
import urllib.error

PORT = 8080

class Handler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/chat':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        api_key = data.pop('api_key', '')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=json.dumps(data).encode(),
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read()
            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        pass  # silence request logs

if __name__ == '__main__':
    server = HTTPServer(('', PORT), Handler)
    print(f'Open this in your browser:  http://localhost:{PORT}/investor-report-analyzer.html')
    print('Press Ctrl+C to stop.')
    server.serve_forever()
