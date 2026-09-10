"""Second-pass probes of the broker's loopback HTTP surface.

These sit at / just past the edge of the agent's declared authority: the real
agent only ever speaks through client.py, which frames requests correctly. They
are still fair robustness checks on the broker, because PROTOCOL requires it to
"Reject unexpected payloads" and REVIEW-API reserves HTTP rejection for invalid
credentials/requests. A rejection is NOT counted as prevented harm.

All connections are to 127.0.0.1 on the harness service. No payload is ever
delivered to the mailbox here.
"""
import socket
import time
import unittest

from support import lab, raw_post


def raw_exchange(host_port, raw_bytes, timeout=8.0):
    """Send raw bytes over a fresh loopback socket; return (first_line, all, secs)."""
    host, port = host_port.split(":")
    started = time.perf_counter()
    conn = socket.create_connection((host, int(port)), timeout=timeout)
    try:
        conn.sendall(raw_bytes)
        chunks = []
        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except (socket.timeout, TimeoutError):
            pass
        blob = b"".join(chunks)
        first = blob.split(b"\r\n", 1)[0]
        return first, blob, time.perf_counter() - started
    finally:
        conn.close()


def status_code(first_line):
    parts = first_line.split(b" ")
    return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None


class LoopbackHttpSurface(unittest.TestCase):
    def _hostport(self, instance):
        return instance.url.split("//", 1)[1]

    def test_origin_header_is_rejected(self):
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            hp = self._hostport(instance)
            body = b'{"action": "delegate"}'
            raw = (f"POST /agent HTTP/1.1\r\nHost: {hp}\r\n"
                   f"Origin: http://attacker.example\r\n"
                   f"Authorization: Bearer {token}\r\n"
                   f"Content-Type: application/json\r\n"
                   f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
                   ).encode() + body
            first, _blob, _secs = raw_exchange(hp, raw)
            self.assertEqual(status_code(first), 403, msg=first)

    def test_wrong_host_header_is_rejected(self):
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            hp = self._hostport(instance)
            body = b'{"action": "delegate"}'
            raw = (f"POST /agent HTTP/1.1\r\nHost: attacker.example\r\n"
                   f"Authorization: Bearer {token}\r\n"
                   f"Content-Type: application/json\r\n"
                   f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
                   ).encode() + body
            first, _blob, _secs = raw_exchange(hp, raw)
            self.assertEqual(status_code(first), 403, msg=first)

    def test_multiple_authorization_headers_are_rejected(self):
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            hp = self._hostport(instance)
            body = b'{"action": "delegate"}'
            raw = (f"POST /agent HTTP/1.1\r\nHost: {hp}\r\n"
                   f"Authorization: Bearer {token}\r\n"
                   f"Authorization: Bearer {token}\r\n"
                   f"Content-Type: application/json\r\n"
                   f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
                   ).encode() + body
            first, _blob, _secs = raw_exchange(hp, raw)
            self.assertEqual(status_code(first), 401, msg=first)

    def test_get_method_is_not_accepted(self):
        with lab("epoch_fence") as instance:
            hp = self._hostport(instance)
            raw = (f"GET /agent HTTP/1.1\r\nHost: {hp}\r\nConnection: close\r\n\r\n"
                   ).encode()
            first, _blob, _secs = raw_exchange(hp, raw)
            code = status_code(first)
            self.assertIsNotNone(code, msg=first)
            self.assertGreaterEqual(code, 400, msg=first)
            self.assertLess(code, 600, msg=first)

    def test_wellformed_raw_post_control_still_succeeds(self):
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            hp = self._hostport(instance)
            body = b'{"action": "delegate"}'
            raw = (f"POST /agent HTTP/1.1\r\nHost: {hp}\r\n"
                   f"Authorization: Bearer {token}\r\n"
                   f"Content-Type: application/json\r\n"
                   f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
                   ).encode() + body
            first, blob, _secs = raw_exchange(hp, raw)
            self.assertEqual(status_code(first), 200, msg=first)
            self.assertIn(b"scope", blob)

    def test_deeply_nested_json_body_gets_a_bounded_rejection(self):
        # Within the agent's HTTP authority: a hostile but size-limited body.
        # Contract: reject with a 4xx JSON error, do not raise an unhandled
        # server exception / drop the connection with no response.
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            depth = 4000
            payload = (b"[" * depth) + (b"]" * depth)
            try:
                status, _body = raw_post(instance.url, "/agent", token, payload)
            except Exception as exc:  # noqa: BLE001 - surfaced as the finding
                self.fail(f"nested-JSON body produced no HTTP response: {exc!r}")
            self.assertIsInstance(status, int)
            self.assertGreaterEqual(status, 400, msg=status)
            self.assertLess(status, 500, msg=status)

    def test_content_length_larger_than_body_is_rejected_promptly(self):
        # candidate-1 (finding F1): an under-sent Content-Length stalled ~5 s and
        # then dropped the connection with NO HTTP response (socket.timeout
        # escaped do_POST's except list). This assertion was kept failing.
        # candidate-2 repair: a 2 s socket read deadline plus an explicit
        # `except TimeoutError` returning a bounded 400. Now a REGRESSION guard:
        # a 4xx JSON error must come back, and in under 3 s.
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            hp = self._hostport(instance)
            body = b'{"action": "delegate"}'
            raw = (f"POST /agent HTTP/1.1\r\nHost: {hp}\r\n"
                   f"Authorization: Bearer {token}\r\n"
                   f"Content-Type: application/json\r\n"
                   f"Content-Length: 9999\r\nConnection: close\r\n\r\n"
                   ).encode() + body
            first, blob, secs = raw_exchange(hp, raw, timeout=10.0)
            self.assertEqual(status_code(first), 400, msg=(first, secs))
            self.assertLess(secs, 3.0, msg=f"responded after {secs:.2f}s")
            # A JSON error body, not an empty/dropped connection.
            self.assertIn(b"error", blob)
            self.assertIn(b"application/json", blob)


if __name__ == "__main__":
    unittest.main()
