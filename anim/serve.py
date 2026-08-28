"""Локальный сервер для работы над произведением.

Две работы:
1) отдаёт страницы с charset=utf-8 (обычный http.server отдаёт html без него,
   и кириллица приезжает крокозябрами);
2) принимает записи голоса: POST /golos/<имя> кладёт тело запроса в golos/<имя>.
   Микрофон в браузере требует защищённого контекста — http://localhost им считается,
   поэтому запись работает без всякого https.
"""
import json
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
GOLOS = os.path.join(ROOT, "golos")
SAFE = set("abcdefghijklmnopqrstuvwxyz0123456789-_.")


class H(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        t = super().guess_type(path)
        if t in ("text/html", "text/css", "application/javascript", "text/javascript"):
            return t + "; charset=utf-8"
        return t

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/golos/list":
            os.makedirs(GOLOS, exist_ok=True)
            files = {}
            for n in sorted(os.listdir(GOLOS)):
                p = os.path.join(GOLOS, n)
                if os.path.isfile(p):
                    files[n] = os.path.getsize(p)
            return self._json(files)
        return super().do_GET()

    def do_POST(self):
        if not self.path.startswith("/golos/"):
            return self._json({"error": "unknown"}, 404)
        name = self.path[len("/golos/"):]
        if not name or any(c not in SAFE for c in name.lower()) or ".." in name:
            return self._json({"error": "bad name"}, 400)
        n = int(self.headers.get("Content-Length", 0))
        if n <= 0 or n > 40_000_000:
            return self._json({"error": "bad length"}, 400)
        os.makedirs(GOLOS, exist_ok=True)
        data = self.rfile.read(n)
        with open(os.path.join(GOLOS, name), "wb") as f:
            f.write(data)
        print(f"  ← принято {name}: {n} байт", flush=True)
        return self._json({"ok": True, "name": name, "bytes": n})


port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8796
print(f"произведение: http://localhost:{port}/kolobok.html")
print(f"запись голоса: http://localhost:{port}/zapis.html")
ThreadingHTTPServer(("127.0.0.1", port), partial(H, directory=ROOT)).serve_forever()
