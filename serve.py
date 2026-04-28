import http.server, socketserver, os, json, urllib.parse
from pathlib import Path

PORT = 4242
BASE_DIR = Path(__file__).parent
STATE_FILE     = BASE_DIR / "VELOCITY_STATE.md"
MEMORY_FILE    = Path(r"C:\Users\User\.openclaw\workspace\MEMORY.md")
HEARTBEAT_FILE = Path(r"C:\Users\User\.openclaw\workspace\HEARTBEAT.md")
ALLOWED = {
    "VELOCITY_STATE.md": STATE_FILE,
    "MEMORY.md":         MEMORY_FILE,
    "HEARTBEAT.md":      HEARTBEAT_FILE,
}

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(BASE_DIR), **k)

    def _json(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p  = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(p.query)
        if p.path == "/api/file":
            name = qs.get("name", [""])[0]
            fp   = ALLOWED.get(name)
            if fp and fp.exists():
                self._json({"content": fp.read_text(encoding="utf-8", errors="replace"), "file": name})
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"not found: {name}"}).encode())
            return
        super().do_GET()

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/append":
            n    = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n))
            line = data.get("line", "").strip()
            if line:
                with open(STATE_FILE, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            self._json({"ok": True})

    def log_message(self, fmt, *a):
        print(f"  {a[0]} {a[1]}")

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    print(f"\n  VELOCITY COMMAND  http://localhost:{PORT}\n  Ctrl+C to stop\n")
    with socketserver.TCPServer(("", PORT), H) as s:
        try:
            s.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")
