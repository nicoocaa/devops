import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

DEFAULT_PORT = 8080


class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ping":
            headers = dict(self.headers)
            body = json.dumps(headers, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_POST(self): self._not_found()
    def do_PUT(self): self._not_found()
    def do_DELETE(self): self._not_found()
    def do_PATCH(self): self._not_found()

    def _not_found(self):
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


def main():
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = HTTPServer(("", port), PingHandler)
    print(f"Listening on port {port}  (set PORT to override)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()