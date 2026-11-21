#!/usr/bin/env python3
"""Lekki serwer statyczny dla katalogu web/ (używany w Dockerze i lokalnie).

W porównaniu z `python -m http.server` dodaje:
- kompresję gzip dla places.json (podaje gotowy plik .gz, ~5× mniej danych),
- nagłówki cache (dane: 1 h, pozostałe pliki: 5 min),
- poprawne typy MIME.
"""

from __future__ import annotations

import argparse
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "web"


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".json": "application/json",
    }

    def send_head(self):  # noqa: D401
        path = Path(self.translate_path(self.path))
        gz = path.with_name(path.name + ".gz")
        if path.suffix == ".json" and gz.exists() and "gzip" in self.headers.get("Accept-Encoding", ""):
            body = gz.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Vary", "Accept-Encoding")
            self.end_headers()
            return _Bytes(body)
        return super().send_head()

    def end_headers(self):
        if "Cache-Control" not in "".join(map(str, getattr(self, "_headers_buffer", []))):
            self.send_header("Cache-Control", "public, max-age=300")
        super().end_headers()


class _Bytes:
    def __init__(self, data: bytes):
        self.data = data

    def read(self, *_):
        data, self.data = self.data, b""
        return data

    def close(self):
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Serwer aplikacji Miejsca Pamięci")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), partial(Handler, directory=str(ROOT)))
    print(f"Miejsca Pamięci: http://localhost:{args.port}  (Ctrl+C aby zakończyć)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
