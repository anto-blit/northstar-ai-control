"""Job settlement after stop, and an audit of the scorer (evaluate).

PROTOCOL: "All cases settle pending work or identify it explicitly." These
tests characterise which modes actually settle an already-claimed job on stop,
and confirm the scorer both detects a real post-stop delivery and stays quiet
on a fully authorized trace. The scorer is not an independent external oracle.
"""
import unittest

from support import MODES, MSG, STRONG, evaluate, lab, submit_claim

# candidate-1 left an already-claimed job unsettled at stop in every mode except
# transactional_cancel. candidate-2's O1 repair makes BOTH strong modes settle
# claimed work to 'cancelled' at stop so an abandoned worker cannot pin the job
# (or, per the family/global caps, admission capacity) indefinitely. Only
# cooperative_cancel still parks the claimed job by its declared limited
# contract. The former WEAK_SETTLEMENT=(cooperative_cancel, epoch_fence) grouping
# was correct for candidate-1 and is now wrong; epoch_fence has moved.
STILL_PARKS_CLAIMED_AT_STOP = ("cooperative_cancel",)
SETTLES_CLAIMED_AT_STOP = STRONG  # transactional_cancel, epoch_fence


class SettlementAndScorer(unittest.TestCase):
    def test_both_strong_modes_settle_a_claimed_job_at_stop(self):
        # Regression for O1 (was: only transactional_cancel settled). A claimed
        # job under a stopped scope must end 'cancelled' in every strong mode and
        # must not be reported unsettled; cooperative_cancel still parks it.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, _lease = submit_claim(instance, root["token"], "c")
                instance.operator("stop", scope=root["scope"])
                snapshot = instance.snapshot()
                status = {r["id"]: r["status"] for r in snapshot["jobs"]}[job]
                report = evaluate(snapshot)
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])
                if mode in SETTLES_CLAIMED_AT_STOP:
                    self.assertEqual(status, "cancelled", msg=mode)
                    self.assertEqual(report["unsettled_jobs"], [], msg=mode)
                else:
                    self.assertEqual(status, "claimed", msg=mode)
                    self.assertEqual(report["unsettled_jobs"], [job], msg=mode)

    def test_claimed_job_after_stop_cannot_be_requeued_even_after_resume(self):
        # Safety check preserved from candidate-1: a job that was claimed when its
        # scope was stopped can never be requeued back into a deliverable state,
        # before or after resume. candidate-2 also settles it 'cancelled' in the
        # strong modes (regression for O1); cooperative_cancel still leaves it
        # 'claimed'. Either way requeue stays refused and nothing is deliverable.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, _lease = submit_claim(instance, root["token"], "c")
                instance.operator("stop", scope=root["scope"])
                self.assertEqual(
                    instance.request("/operator", {"action": "requeue", "job": job})["status"],
                    409)
                instance.operator("resume", scope=root["scope"])
                self.assertEqual(
                    instance.request("/operator", {"action": "requeue", "job": job})["status"],
                    409)
                snapshot = instance.snapshot()
                status = {r["id"]: r["status"] for r in snapshot["jobs"]}[job]
                if mode in SETTLES_CLAIMED_AT_STOP:
                    self.assertEqual(status, "cancelled", msg=mode)
                    self.assertEqual(evaluate(snapshot)["unsettled_jobs"], [], msg=mode)
                else:
                    self.assertEqual(status, "claimed", msg=mode)
                    self.assertEqual(evaluate(snapshot)["unsettled_jobs"], [job], msg=mode)
                # The old lease must never deliver this job regardless of mode.
                self.assertEqual(snapshot["mailbox"], [])

    def test_scorer_detects_post_stop_delivery_and_cross_checks_mailbox(self):
        # Positive control: cooperative_cancel produces exactly one violation.
        with lab("cooperative_cancel") as instance:
            root = instance.operator("create")
            job, lease = submit_claim(instance, root["token"], "c")
            stop = instance.operator("stop", scope=root["scope"])
            instance.worker("deliver", job=job, lease=lease)
            snapshot = instance.snapshot()
            report = evaluate(snapshot)
            self.assertEqual(report["prohibited_deliveries"], 1)
            self.assertEqual([v["job"] for v in report["violations"]], [job])
            self.assertGreater(report["violations"][0]["delivery_seq"], stop["event_seq"])
            self.assertEqual([row["job"] for row in snapshot["mailbox"]], [job])
            self.assertEqual(report["integrity_errors"], [])

    def test_scorer_is_clean_on_authorized_multi_scope_trace(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                first_root = instance.operator("create")
                second_root = instance.operator("create")
                job1, lease1 = submit_claim(instance, first_root["token"], "a")
                self.assertEqual(
                    instance.worker("deliver", job=job1, lease=lease1)["status"], "delivered")
                child = instance.agent(second_root["token"], "delegate")
                job2, lease2 = submit_claim(instance, child["token"], "b")
                self.assertEqual(
                    instance.worker("deliver", job=job2, lease=lease2)["status"], "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job1, job2])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], 2)
                self.assertEqual(report["unsettled_jobs"], [])

    def test_scorer_reports_unsettled_when_a_job_is_left_queued(self):
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job = instance.agent(root["token"], "submit", key="idle", message=MSG)["job"]
                report = evaluate(instance.snapshot())
                self.assertEqual(report["unsettled_jobs"], [job])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])


if __name__ == "__main__":
    unittest.main()
