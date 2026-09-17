"""Run a callable under a hard wall-clock deadline.

POSIX uses SIGALRM so the deadline interrupts the call itself. Windows has no
SIGALRM, so the call runs in a worker thread and the deadline is enforced by
joining with a timeout. The observable contract is the same: return the value
if it finishes inside `seconds`, otherwise raise `Timeout`. A RecursionError
raised by the callable propagates unchanged on both platforms.
"""
import signal
import threading

HAVE_SIGALRM = hasattr(signal, "SIGALRM")


class Timeout(Exception):
    pass


def _posix(seconds, fn, args, kwargs):
    def _fire(signum, frame):
        raise Timeout(f"exceeded {seconds}s")
    old = signal.signal(signal.SIGALRM, _fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn(*args, **kwargs)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def _threaded(seconds, fn, args, kwargs):
    box = {}

    def _work():
        try:
            box["value"] = fn(*args, **kwargs)
        except BaseException as exc:  # re-raised on the calling thread below
            box["error"] = exc

    worker = threading.Thread(target=_work, daemon=True)
    worker.start()
    worker.join(seconds)
    if worker.is_alive():
        raise Timeout(f"exceeded {seconds}s")
    if "error" in box:
        raise box["error"]
    return box["value"]


def under_deadline(seconds, fn, *args, **kwargs):
    runner = _posix if HAVE_SIGALRM else _threaded
    return runner(seconds, fn, args, kwargs)
