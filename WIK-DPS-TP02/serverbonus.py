import json
import os
import socket
import time
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler, HTTPServer

DEFAULT_PORT = 8080


class CounterStore(ABC):
    @abstractmethod
    def increment(self) -> int:

    @abstractmethod
    def get(self) -> int:


class InMemoryCounterStore(CounterStore):

    def __init__(self):
        self._count = 0

    def increment(self) -> int:
        self._count += 1
        return self._count

    def get(self) -> int:
        return self._count


class PingHandler(BaseHTTPRequestHandler):
    counter: CounterStore
    start_time: float
    instance_id: str

    def do_GET(self):
        self.counter.increment()

        if self.path == "/ping":
            self._handle_ping()
        elif self.path == "/stats":
            self._handle_stats()
        else:
            self._not_found()

    def _handle_ping(self):
        body = json.dumps(dict(self.headers), indent=2).encode()
        self._send_json(200, body)

    def _handle_stats(self):
        payload = {
            "total_requests": self.counter.get(),
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "instance_id": self.instance_id,
        }
        body = json.dumps(payload, indent=2).encode()
        self._send_json(200, body)


    def _send_json(self, status: int, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self):
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


def find_free_port(start: int, max_attempts: int = 10) -> int:
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise OSError(
        f"No free port found in range {start}–{start + max_attempts - 1}"
    )


def main():
    requested_port = int(os.environ.get("PORT", DEFAULT_PORT))
    instance_id = os.environ.get("INSTANCE_ID", socket.gethostname())

    PingHandler.counter = InMemoryCounterStore()
    PingHandler.start_time = time.time()
    PingHandler.instance_id = instance_id

    port = find_free_port(requested_port)
    if port != requested_port:
        print(f"Port {requested_port} already in use, using port {port} instead.")

    server = HTTPServer(("", port), PingHandler)
    print(f"Listening on port {port}  |  instance={instance_id}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
