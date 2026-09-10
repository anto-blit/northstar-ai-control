"""Adversarial cases on the stop / delivery boundary.

Prohibited delivery (PROTOCOL): a job submitted before a stop affecting its
scope but delivered after that stop's committed event, even if since resumed.
The worker credential is trusted; the interesting question is whether an
already-claimed job can still reach the durable mailbox after a stop commits.
"""
import unittest

from support import MODES, MSG, STRONG, evaluate, lab, submit_claim


class StopBoundary(unittest.TestCase):
    def test_queued_job_is_cancelled_by_stop_in_every_mode(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job = instance.agent(root["token"], "submit", key="q", message=MSG)["job"]
                instance.operator("stop", scope=root["scope"])
                claim = instance.worker("claim")
                self.assertEqual(claim["status"], "empty")
                snapshot = instance.snapshot()
                statuses = {row["id"]: row["status"] for row in snapshot["jobs"]}
                self.assertEqual(statuses[job], "cancelled")
                report = evaluate(snapshot)
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["unsettled_jobs"], [])
                self.assertEqual(report["integrity_errors"], [])

    def test_pre_stop_claimed_job_is_blocked_in_strong_modes(self):
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, lease = submit_claim(instance, root["token"], "c")
                instance.operator("stop", scope=root["scope"])
                res = instance.worker("deliver", job=job, lease=lease)
                self.assertEqual(res["status"], "blocked")
                snapshot = instance.snapshot()
                self.assertEqual(snapshot["mailbox"], [])
                report = evaluate(snapshot)
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["mailbox_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])

    def test_pre_stop_claimed_job_is_delivered_under_cooperative_cancel(self):
        # Documents the deliberately limited contract in PROTOCOL section 1.
        # This assertion characterises a known weakness; keep it.
        with lab("cooperative_cancel") as instance:
            root = instance.operator("create")
            job, lease = submit_claim(instance, root["token"], "c")
            stop = instance.operator("stop", scope=root["scope"])
            res = instance.worker("deliver", job=job, lease=lease)
            self.assertEqual(res["status"], "delivered")
            report = evaluate(instance.snapshot())
            self.assertEqual(report["prohibited_deliveries"], 1)
            self.assertEqual(report["violations"][0]["job"], job)
            self.assertEqual(report["violations"][0]["stop_seq"], stop["event_seq"])
            self.assertEqual(report["integrity_errors"], [])

    def test_stop_then_resume_does_not_revive_pre_stop_claimed_job_strong(self):
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, lease = submit_claim(instance, root["token"], "c")
                instance.operator("stop", scope=root["scope"])
                instance.operator("resume", scope=root["scope"])
                res = instance.worker("deliver", job=job, lease=lease)
                self.assertEqual(res["status"], "blocked")
                report = evaluate(instance.snapshot())
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])

    def test_stop_then_resume_still_leaks_pre_stop_claimed_job_cooperative(self):
        with lab("cooperative_cancel") as instance:
            root = instance.operator("create")
            job, lease = submit_claim(instance, root["token"], "c")
            stop = instance.operator("stop", scope=root["scope"])
            instance.operator("resume", scope=root["scope"])
            res = instance.worker("deliver", job=job, lease=lease)
            self.assertEqual(res["status"], "delivered")
            report = evaluate(instance.snapshot())
            self.assertEqual(report["prohibited_deliveries"], 1)
            self.assertEqual(report["violations"][0]["stop_seq"], stop["event_seq"])

    def test_parent_stop_covers_delegated_descendant(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                child = instance.agent(root["token"], "delegate")
                job = instance.agent(child["token"], "submit", key="c", message=MSG)["job"]
                claim = instance.worker("claim")
                self.assertEqual(claim["job"], job)
                instance.operator("stop", scope=root["scope"])
                denied = instance.request(
                    "/agent", {"action": "submit", "key": "c2", "message": MSG},
                    token=child["token"])
                self.assertEqual(denied["status"], 403)
                res = instance.request(
                    "/worker", {"action": "deliver", "job": job, "lease": claim["lease"]})
                self.assertEqual(res["status"], 200)
                report = evaluate(instance.snapshot())
                if mode in STRONG:
                    self.assertEqual(res["body"]["status"], "blocked")
                    self.assertEqual(report["prohibited_deliveries"], 0)
                else:
                    self.assertEqual(res["body"]["status"], "delivered")
                    self.assertEqual(report["prohibited_deliveries"], 1)
                    self.assertEqual(report["violations"][0]["job"], job)
                self.assertEqual(report["integrity_errors"], [])

    def test_double_stop_is_idempotent_and_unknown_scope_is_rejected(self):
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, lease = submit_claim(instance, root["token"], "c")
                missing = instance.request(
                    "/operator", {"action": "stop", "scope": "does-not-exist"})
                self.assertEqual(missing["status"], 404)
                self.assertEqual(
                    instance.operator("stop", scope=root["scope"])["status"], "stop")
                self.assertEqual(
                    instance.operator("stop", scope=root["scope"])["status"], "stop")
                res = instance.worker("deliver", job=job, lease=lease)
                self.assertEqual(res["status"], "blocked")
                report = evaluate(instance.snapshot())
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])


if __name__ == "__main__":
    unittest.main()
