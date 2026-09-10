"""Shared helpers for the separately commissioned skeptical review.

A different AI wrote the implementation under northstar_queue/. Nothing here
modifies it; these helpers only drive the documented HTTP surface and the
documented reviewer harness (northstar_queue.harness.Lab) plus the scorer
(northstar_queue.evaluate.evaluate). All traffic is loopback (127.0.0.1) to the
harness-spawned local service. Mailbox payloads are harmless fixed strings.
"""
import contextlib
import json
import threading
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from northstar_queue.harness import Lab
from northstar_queue.evaluate import evaluate  # re-exported for the test modules

MODES = ("cooperative_cancel", "transactional_cancel", "epoch_fence")
STRONG = ("transactional_cancel", "epoch_fence")
MSG = "harmless test string"


@contextlib.contextmanager
def lab(mode):
    """A fresh temp dir + Lab for one mode.

    candidate-2 closes the Store bootstrap connection (contextlib.closing in
    store.py) and the server-side subprocess is terminated and joined by
    Lab.close() before this context exits, so every SQLite handle on
    queue.sqlite3 (plus -wal/-shm) is released before TemporaryDirectory runs
    its cleanup. The previous ``ignore_cleanup_errors=True`` masked the leaked
    bootstrap handle and is intentionally dropped: a resurfaced cleanup error is
    now a real regression and should fail loudly.
    """
    with TemporaryDirectory() as work:
        with Lab(work, mode) as instance:
            yield instance


def submit_claim(instance, token, key, message=MSG):
    """Submit one job and immediately claim it; assert the claim is that job."""
    job = instance.agent(token, "submit", key=key, message=message)["job"]
    claim = instance.worker("claim")
    assert claim.get("job") == job, ("unexpected claim", job, claim)
    return job, claim["lease"]


def full_flow(instance, token, key, message=MSG):
    """Submit -> claim -> deliver a single job; return (job_id, deliver_body)."""
    job, lease = submit_claim(instance, token, key, message=message)
    return job, instance.worker("deliver", job=job, lease=lease)


def raw_post(url, route, token, body_bytes, content_type="application/json",
             extra_headers=None):
    """Loopback HTTP POST with a hand-built body, bypassing client.py framing."""
    headers = {"Authorization": "Bearer " + token}
    if content_type is not None:
        headers["Content-Type"] = content_type
    if extra_headers:
        headers.update(extra_headers)
    request = Request(url + route, data=body_bytes, headers=headers, method="POST")
    opener = build_opener(ProxyHandler({}))
    try:
        with opener.open(request, timeout=10) as response:
            return response.status, json.load(response)
    except HTTPError as response:
        try:
            return response.code, json.load(response)
        finally:
            response.close()


def run_pair(fn_a, fn_b):
    """Run two callables from two threads released together; collect results.

    A raised exception is stored in place of the result so the caller can assert
    on it instead of losing it in a dead thread.
    """
    results = {}
    barrier = threading.Barrier(2, timeout=15)

    def wrap(name, fn):
        def inner():
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                pass
            try:
                results[name] = fn()
            except BaseException as exc:  # noqa: BLE001 - deliberately surfaced
                results[name] = exc
        return inner

    thread_a = threading.Thread(target=wrap("a", fn_a))
    thread_b = threading.Thread(target=wrap("b", fn_b))
    thread_a.start()
    thread_b.start()
    thread_a.join(20)
    thread_b.join(20)
    return results
