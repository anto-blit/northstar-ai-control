"""Process orchestration shared by internal cases and outside reviewers."""
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from pathlib import Path
import secrets
import subprocess
import sys
import time

from .client import call


ROOT = Path(__file__).resolve().parent.parent


def redacted(value):
    if isinstance(value, dict):
        return {key: "[redacted]" if key in ("token", "lease") else redacted(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redacted(item) for item in value]
    return value


class Process:
    def __init__(self, module, config):
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        self.proc = subprocess.Popen([sys.executable, "-m", module], cwd=ROOT,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                     creationflags=flags)
        self.reader = ThreadPoolExecutor(max_workers=1)
        self.send(config)

    def send(self, data):
        self.proc.stdin.write(json.dumps(data) + "\n")
        self.proc.stdin.flush()

    def receive(self):
        pending = self.reader.submit(self.proc.stdout.readline)
        try:
            line = pending.result(timeout=15)
        except TimeoutError:
            self.close()
            raise RuntimeError("Child process exceeded response deadline") from None
        if not line:
            self.proc.wait(timeout=5)
            error = self.proc.stderr.read()
            raise RuntimeError(f"Child exited {self.proc.returncode}: {error[-2000:]}")
        return json.loads(line)

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self.reader.shutdown(wait=True, cancel_futures=True)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            stream.close()


class Lab:
    def __init__(self, directory, mode):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.database = self.directory / "queue.sqlite3"
        self.mode = mode
        self.credentials = {role: secrets.token_hex(32) for role in ("operator", "worker", "audit")}
        self.clients, self.calls, self.processes = [], [], []
        self.server = None
        self.start()

    def start(self):
        self.server = Process("northstar_queue.server", {
            "database": str(self.database), "mode": self.mode, "credentials": self.credentials})
        self.url = self.server.receive()["url"]
        self.processes.append({"role": "server", "pid": self.server.proc.pid})

    def restart(self):
        for client in self.clients:
            client.close()
        self.clients.clear()
        self.server.close()
        self.start()

    def request(self, route, body, token=None):
        token = token or self.credentials.get(route.lstrip("/"), "invalid")
        started = time.perf_counter()
        result = call(self.url, token, route, body)
        self.record(route, body, result, time.perf_counter() - started)
        return result

    def record(self, route, body, result, elapsed):
        if route == "/audit" and result["status"] == 200:
            result = {"status": 200, "body": {"snapshot_recorded_separately": True}}
        self.calls.append({"route": route, "request": redacted(body),
                           "response": redacted(result), "elapsed_seconds": elapsed})

    @staticmethod
    def ok(result):
        if result["status"] != 200:
            raise AssertionError(f"Unexpected response: {result}")
        return result["body"]

    def operator(self, action, **parameters):
        return self.ok(self.request("/operator", {"action": action, **parameters}))

    def worker(self, action, **parameters):
        return self.ok(self.request("/worker", {"action": action, **parameters}))

    def agent(self, token, action, **parameters):
        return self.ok(self.request("/agent", {"action": action, **parameters}, token))

    def process_client(self, token, route):
        proc = Process("northstar_queue.client", {"url": self.url, "token": token})
        self.clients.append(proc)
        self.processes.append({"role": route.lstrip("/"), "pid": proc.proc.pid})
        def invoke(action, **parameters):
            body = {"action": action, **parameters}
            started = time.perf_counter()
            proc.send({"route": route, "body": body})
            result = proc.receive()
            self.record(route, body, result, time.perf_counter() - started)
            return self.ok(result)
        return invoke

    def snapshot(self):
        return self.ok(self.request("/audit", {"action": "snapshot"}))

    def close(self):
        for client in self.clients:
            client.close()
        self.clients.clear()
        if self.server:
            self.server.close()
            self.server = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
