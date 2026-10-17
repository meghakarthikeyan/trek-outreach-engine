#!/usr/bin/env python3
"""
Local engine bridge for the Trek Outreach app.

- Serves index.html (and any static files) on http://localhost:8000
- POST /submit  -> saves whatever the user pasted in the web app to submission.json
                   (Claude Code reads this to know what to research)
- GET  /results -> returns results.json once Claude Code has written it,
                   otherwise {"ready": false} so the app keeps waiting.
"""
import json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

DIR = os.path.dirname(os.path.abspath(__file__))
SUB = os.path.join(DIR, "submission.json")
RES = os.path.join(DIR, "results.json")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIR, **k)

    def _send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.rstrip("/") == "/submit":
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n).decode() if n else "{}"
            try:
                payload = json.loads(raw)
            except Exception:
                payload = {"raw": raw}
            with open(SUB, "w") as f:
                json.dump(payload, f, indent=2)
            # NOTE: we keep any existing results.json so the app can display the
            # last engine run immediately. The engine refreshes it for a new list.
            print("\n>>> New submission received:", json.dumps(payload))
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_GET(self):
        if self.path.rstrip("/") == "/results":
            if os.path.exists(RES):
                try:
                    with open(RES) as f:
                        self._send_json(200, json.load(f))
                    return
                except Exception:
                    pass
            self._send_json(200, {"ready": False})
            return
        return super().do_GET()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("Trek Outreach engine running at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
