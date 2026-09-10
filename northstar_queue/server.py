"""Loopback-only HTTP service. Private configuration arrives on stdin."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
import sqlite3
import sys

from .store import Store, Rejected, fields


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Do not log bearer capabilities or arbitrary agent payloads.

    def setup(self):
        super().setup()
        self.connection.settimeout(2)

    def do_POST(self):
        try:
            if self.headers.get("Origin") or self.headers.get("Host") != self.server.host:
                raise Rejected(403, "Loopback research client required")
            if len(self.headers.get_all("Authorization", [])) != 1:
                raise Rejected(401, "One bearer authorization header required")
            authorization = self.headers["Authorization"]
            if not authorization.startswith("Bearer ") or len(authorization) > 256:
                raise Rejected(401, "Bearer authorization required")
            token = authorization[7:]
            if self.path not in ("/agent", "/operator", "/worker", "/audit"):
                raise Rejected(404, "Unknown route")
            if self.path != "/agent":
                expected = self.server.credentials[self.path[1:]]
                if not secrets.compare_digest(token, expected):
                    raise Rejected(403, "Role credential required")
            if (self.headers.get("Transfer-Encoding") or
                    len(self.headers.get_all("Content-Length", [])) != 1 or
                    self.headers.get("Content-Type") != "application/json"):
                raise Rejected(400, "One JSON body with a declared length required")
            length = int(self.headers["Content-Length"])
            if not 0 < length <= 16384:
                raise Rejected(413, "Body size outside research limits")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise Rejected(400, "Incomplete body")
            body = json.loads(raw, object_pairs_hook=unique_object)
            if self.path == "/agent":
                result = self.server.store.agent(token, body)
            elif self.path == "/operator":
                result = self.server.store.operator(body)
            elif self.path == "/worker":
                result = self.server.store.worker(body)
            else:
                fields(body, ("action",))
                if body["action"] != "snapshot":
                    raise Rejected(400, "Unknown audit action")
                result = self.server.store.snapshot()
            self.respond(200, result)
        except Rejected as exc:
            self.respond(exc.status, {"error": exc.reason})
        except (ValueError, UnicodeError, TypeError, RecursionError):
            self.respond(400, {"error": "Invalid request"})
        except TimeoutError:
            self.respond(400, {"error": "Incomplete request body before the local read deadline"})
        except sqlite3.Error:
            # An unavailable database must never be mistaken for authorization.
            self.respond(503, {"error": "Database transaction unavailable"})

    def respond(self, status, result):
        encoded = json.dumps(result).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(encoded)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass  # A committed result can be retried using its idempotency key.


def main():
    config = json.loads(sys.stdin.readline())
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        server.daemon_threads = True
        server.store = Store(config["database"], config["mode"])
        server.credentials = config["credentials"]
        server.host = f"127.0.0.1:{server.server_port}"
        print(json.dumps({"url": f"http://{server.host}"}), flush=True)
        server.serve_forever(poll_interval=0.05)


if __name__ == "__main__":
    main()
