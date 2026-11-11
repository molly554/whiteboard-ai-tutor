"""Local static server for Whiteboard AI Tutor.

  python serve.py [port]      then open http://localhost:8811/

Serves the repository root with caching disabled (so edited scripts show up immediately).
Also accepts POST /save/<relative path>, restricted to results/ — the player uses it to store
lint results, rendered boards and animation frames. GitHub Pages does not need this server.
"""
import http.server
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SAVE_BASE = os.path.join(ROOT, "results")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if not self.path.startswith("/save/"):
            self.send_error(404)
            return
        rel = self.path[len("/save/"):].split("?")[0]
        if not re.fullmatch(r"[A-Za-z0-9_.\-/]+", rel) or ".." in rel:
            self.send_error(400, "bad name")
            return
        dest = os.path.normpath(os.path.join(SAVE_BASE, rel))
        if not dest.startswith(SAVE_BASE + os.sep):
            self.send_error(400, "bad path")
            return
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8811
    print("Whiteboard AI Tutor: http://localhost:%d/" % port)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
