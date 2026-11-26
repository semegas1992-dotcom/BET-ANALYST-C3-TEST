"""Loopback-only experimental Android/desktop bridge. No remote service."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from p32_dynamic import generate_registered

ROOT = Path(__file__).with_name("p32_local_ui")
SPORTS = {"football", "nba", "tennis"}
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get("Host") not in {"127.0.0.1:8767", "localhost:8767"}:
            self.send_error(403)
            return
        if self.path == "/":
            self.reply(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path.startswith("/report/") and self.path[8:] in SPORTS:
            try:
                data = generate_registered(self.path[8:])
                self.reply(200, json.dumps(data, ensure_ascii=False).encode(), "application/json; charset=utf-8")
            except Exception:
                self.send_error(422, "Synthetic generation refused")
        else:
            self.send_error(404)
    def reply(self, code, body, mime):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8767), Handler).serve_forever()
