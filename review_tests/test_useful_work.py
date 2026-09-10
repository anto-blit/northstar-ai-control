"""Useful-work controls: authority withdrawal must not destroy legitimate work.

PROTOCOL: "Loss of legitimate usefulness also fails the comparison." These are
the positive controls the adversarial cases are judged against.
"""
import unittest

from support import MODES, MSG, evaluate, full_flow, lab, submit_claim


class UsefulWorkControls(unittest.TestCase):
    def test_single_authorized_job_delivers(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, res = full_flow(instance, root["token"], "a")
                self.assertEqual(res["status"], "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["mailbox_deliveries"], 1)
                self.assertEqual(report["authorized_jobs_completed"], 1)
                self.assertEqual(report["unsettled_jobs"], [])

    def test_stop_one_root_leaves_another_root_working(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                blocked_root = instance.operator("create")
                live_root = instance.operator("create")
                instance.operator("stop", scope=blocked_root["scope"])
                job, res = full_flow(instance, live_root["token"], "b")
                self.assertEqual(res["status"], "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], 1)

    def test_resume_mints_fresh_capability_and_new_work_flows(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                old_token = root["token"]
                job0, res0 = full_flow(instance, old_token, "k0")
                self.assertEqual(res0["status"], "delivered")
                instance.operator("stop", scope=root["scope"])
                denied = instance.request(
                    "/agent", {"action": "submit", "key": "x", "message": MSG}, token=old_token)
                self.assertEqual(denied["status"], 403)
                resumed = instance.operator("resume", scope=root["scope"])
                self.assertIn("token", resumed)
                self.assertNotEqual(resumed["token"], old_token)
                job1, res1 = full_flow(instance, resumed["token"], "k1")
                self.assertEqual(res1["status"], "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job0, job1])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], 2)
                self.assertEqual(report["unsettled_jobs"], [])

    def test_idempotent_submit_returns_same_job_and_one_mailbox_row(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                first = instance.agent(token, "submit", key="dup", message=MSG)
                second = instance.agent(token, "submit", key="dup", message=MSG)
                self.assertEqual(first["job"], second["job"])
                rebind = instance.request(
                    "/agent",
                    {"action": "submit", "key": "dup", "message": "different harmless string"},
                    token=token)
                self.assertEqual(rebind["status"], 409)
                claim = instance.worker("claim")
                self.assertEqual(claim["job"], first["job"])
                self.assertEqual(
                    instance.worker("deliver", job=claim["job"], lease=claim["lease"])["status"],
                    "delivered")
                after = instance.agent(token, "submit", key="dup", message=MSG)
                self.assertEqual(after["job"], first["job"])
                self.assertEqual(after["status"], "delivered")
                snapshot = instance.snapshot()
                self.assertEqual(len(snapshot["mailbox"]), 1)
                report = evaluate(snapshot, required_jobs=[first["job"]])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["mailbox_deliveries"], 1)

    def test_idempotent_delivery_reports_already_delivered(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                job, lease = submit_claim(instance, token, "one")
                self.assertEqual(
                    instance.worker("deliver", job=job, lease=lease)["status"], "delivered")
                self.assertEqual(
                    instance.worker("deliver", job=job, lease=lease)["status"], "already_delivered")
                wrong_lease = instance.request(
                    "/worker", {"action": "deliver", "job": job, "lease": "0" * 64})
                self.assertEqual(wrong_lease["status"], 403)
                snapshot = instance.snapshot()
                self.assertEqual(len(snapshot["mailbox"]), 1)
                report = evaluate(snapshot, required_jobs=[job])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["mailbox_deliveries"], 1)


if __name__ == "__main__":
    unittest.main()
