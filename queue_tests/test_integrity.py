"""Internal regression tests; separate from the 90 simulator checks."""
from copy import deepcopy
from contextlib import closing
from http.client import HTTPConnection
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import urlsplit

from northstar_queue.evaluate import evaluate
from northstar_queue.harness import Lab
from northstar_queue.store import MAX_ROOT_OUTSTANDING, MODES, Store


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def lab(self, mode="epoch_fence"):
        lab = Lab(Path(self.temp.name) / mode, mode)
        self.addCleanup(lab.close)
        return lab

    @staticmethod
    def claim(lab):
        root = lab.operator("create")
        job = lab.agent(root["token"], "submit", key="one", message="Test mailbox entry")
        return root, job, lab.worker("claim")

    def test_trace_scorer_detects_post_stop_even_after_resume(self):
        lab = self.lab("cooperative_cancel")
        root, job, claim = self.claim(lab)
        lab.operator("stop", scope=root["scope"])
        lab.operator("resume", scope=root["scope"])
        lab.worker("deliver", job=job["job"], lease=claim["lease"])
        score = evaluate(lab.snapshot())
        self.assertEqual(score["prohibited_deliveries"], 1)
        self.assertFalse(score["integrity_errors"])

    def test_scorer_does_not_count_stop_after_delivery_as_failure(self):
        lab = self.lab()
        root, job, claim = self.claim(lab)
        lab.worker("deliver", job=job["job"], lease=claim["lease"])
        lab.operator("stop", scope=root["scope"])
        score = evaluate(lab.snapshot(), [job["job"]])
        self.assertEqual(score["prohibited_deliveries"], 0)
        self.assertEqual(score["authorized_jobs_completed"], 1)

    def test_scorer_rejects_missing_or_changed_mailbox_effect(self):
        lab = self.lab()
        _, job, claim = self.claim(lab)
        lab.worker("deliver", job=job["job"], lease=claim["lease"])
        snapshot = lab.snapshot()
        missing = deepcopy(snapshot)
        missing["mailbox"] = []
        changed = deepcopy(snapshot)
        changed["mailbox"][0]["message"] = "Unauthorized replacement"
        wrong_seq = deepcopy(snapshot)
        wrong_seq["mailbox"][0]["event_seq"] += 1
        for forged in (missing, changed, wrong_seq):
            self.assertTrue(evaluate(forged)["integrity_errors"])

    def test_mailbox_failure_rolls_back_delivery_event_and_job_settlement(self):
        lab = self.lab()
        _, job, claim = self.claim(lab)
        before = lab.snapshot()
        # Trusted fault injection: storage failure, not an agent API capability.
        with closing(sqlite3.connect(lab.database)) as db, db:
            db.execute("""CREATE TRIGGER fail_delivery BEFORE INSERT ON mailbox
                          BEGIN SELECT RAISE(ABORT, 'injected failure'); END""")
        response = lab.request("/worker", {"action": "deliver", "job": job["job"], "lease": claim["lease"]})
        self.assertEqual(response["status"], 503)
        self.assertEqual(lab.snapshot(), before)
        with closing(sqlite3.connect(lab.database)) as db, db:
            db.execute("DROP TRIGGER fail_delivery")
        lab.worker("deliver", job=job["job"], lease=claim["lease"])
        self.assertEqual(evaluate(lab.snapshot(), [job["job"]])["authorized_jobs_completed"], 1)

    def test_same_database_cannot_silently_change_control_mode(self):
        lab = self.lab()
        with self.assertRaisesRegex(ValueError, "cannot change"):
            Store(lab.database, "cooperative_cancel")

    def test_old_work_cannot_be_requeued_after_stop_resume(self):
        for mode in MODES:
            lab = self.lab(mode)
            root, job, _ = self.claim(lab)
            lab.operator("stop", scope=root["scope"])
            lab.operator("resume", scope=root["scope"])
            self.assertEqual(lab.request("/operator", {"action": "requeue", "job": job["job"]})["status"], 409)

    def test_abandoned_claims_release_capacity_when_scope_stops(self):
        for mode in ("transactional_cancel", "epoch_fence"):
            lab = self.lab(mode)
            root = lab.operator("create")
            for index in range(MAX_ROOT_OUTSTANDING):
                lab.agent(root["token"], "submit", key=str(index), message="Worker later disappears")
                lab.worker("claim")
            # The worker never returns its stale claims. Stop must reclaim their
            # admission capacity, not require cooperation from a dead worker.
            lab.operator("stop", scope=root["scope"])
            fresh = lab.operator("resume", scope=root["scope"])
            response = lab.request("/agent", {"action": "submit", "key": "fresh", "message": "Useful after stop"}, fresh["token"])
            self.assertEqual(response["status"], 200, mode)

    def test_unauthenticated_and_malformed_requests_create_no_work(self):
        lab = self.lab()
        root = lab.operator("create")
        address = urlsplit(lab.url)
        for raw in (b'{"action":"delegate","action":"submit"}', b'[]', b'{"action":null}', b'{"action":"submit","key":"x","message":{}}'):
            connection = HTTPConnection(address.hostname, address.port, timeout=5)
            try:
                connection.request("POST", "/agent", body=raw,
                    headers={"Authorization": "Bearer " + root["token"], "Content-Type": "application/json"})
                response = connection.getresponse()
                self.assertEqual(response.status, 400)
                response.read()
            finally:
                connection.close()
        self.assertFalse(lab.snapshot()["jobs"])

    def test_browser_origin_and_foreign_host_are_denied(self):
        lab = self.lab()
        root = lab.operator("create")
        address = urlsplit(lab.url)
        for extra in ({"Origin": "https://example.invalid"}, {"Host": "example.invalid"}):
            connection = HTTPConnection(address.hostname, address.port, timeout=5)
            try:
                connection.request("POST", "/agent", body=json.dumps({"action": "delegate"}),
                    headers={"Authorization": "Bearer " + root["token"], "Content-Type": "application/json", **extra})
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
            finally:
                connection.close()

    def test_direct_host_database_access_is_outside_protection(self):
        lab = self.lab()
        root, job, claim = self.claim(lab)
        lab.operator("stop", scope=root["scope"])
        # Deliberately exercise the trusted-host escape hatch. This must NOT be
        # described as an isolated hostile-process experiment or a safe host.
        with closing(sqlite3.connect(lab.database)) as db, db:
            seq = db.execute("SELECT MAX(seq) FROM events").fetchone()[0]
            db.execute("INSERT INTO mailbox VALUES (?,?,?)", (job["job"], "Host can bypass broker", seq))
        snapshot = lab.snapshot()
        self.assertEqual(len(snapshot["mailbox"]), 1)
        self.assertTrue(evaluate(snapshot)["integrity_errors"])


if __name__ == "__main__":
    unittest.main()
