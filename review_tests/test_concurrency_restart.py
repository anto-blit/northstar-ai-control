"""Concurrency, restart and claim/idempotency boundary cases.

Restart tests keep the SQLite database and discard server memory (harness
contract). Concurrency tests race a stop against an already-claimed delivery;
SQLite serialises writers, so the invariant under test is order-independent:
in a strong mode a post-stop delivery must never commit to the mailbox.
"""
import threading
import unittest

from support import MODES, MSG, STRONG, evaluate, lab, run_pair, submit_claim


class ConcurrencyAndRestart(unittest.TestCase):
    def test_restart_keeps_valid_claim_usable_for_authorized_delivery(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, lease = submit_claim(instance, root["token"], "keep")
                instance.restart()
                res = instance.worker("deliver", job=job, lease=lease)
                self.assertEqual(res["status"], "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], 1)
                self.assertEqual(report["integrity_errors"], [])

    def test_restart_preserves_stop_decision_in_strong_modes(self):
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, lease = submit_claim(instance, root["token"], "c")
                instance.operator("stop", scope=root["scope"])
                instance.restart()
                res = instance.worker("deliver", job=job, lease=lease)
                self.assertEqual(res["status"], "blocked")
                report = evaluate(instance.snapshot())
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["mailbox_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])

    def test_restart_does_not_repair_cooperative_cancel_leak(self):
        with lab("cooperative_cancel") as instance:
            root = instance.operator("create")
            job, lease = submit_claim(instance, root["token"], "c")
            stop = instance.operator("stop", scope=root["scope"])
            instance.restart()
            res = instance.worker("deliver", job=job, lease=lease)
            self.assertEqual(res["status"], "delivered")
            report = evaluate(instance.snapshot())
            self.assertEqual(report["prohibited_deliveries"], 1)
            self.assertEqual(report["violations"][0]["stop_seq"], stop["event_seq"])

    def test_idempotent_submit_survives_restart(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                first = instance.agent(token, "submit", key="a", message=MSG)["job"]
                instance.restart()
                second = instance.agent(token, "submit", key="a", message=MSG)["job"]
                self.assertEqual(first, second)
                claim = instance.worker("claim")
                self.assertEqual(claim["job"], first)
                self.assertEqual(
                    instance.worker("deliver", job=first, lease=claim["lease"])["status"],
                    "delivered")
                snapshot = instance.snapshot()
                self.assertEqual(len(snapshot["mailbox"]), 1)
                self.assertEqual(evaluate(snapshot)["integrity_errors"], [])

    def test_requeue_invalidates_old_lease_then_authorized_redelivery_works(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, stale_lease = submit_claim(instance, root["token"], "c")
                requeued = instance.request("/operator", {"action": "requeue", "job": job})
                self.assertEqual(requeued["status"], 200)
                stale = instance.request(
                    "/worker", {"action": "deliver", "job": job, "lease": stale_lease})
                self.assertEqual(stale["status"], 403)
                reclaim = instance.worker("claim")
                self.assertEqual(reclaim["job"], job)
                self.assertEqual(
                    instance.worker("deliver", job=job, lease=reclaim["lease"])["status"],
                    "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["authorized_jobs_completed"], 1)

    def test_requeue_is_refused_after_stop(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                job, _lease = submit_claim(instance, root["token"], "c")
                instance.operator("stop", scope=root["scope"])
                refused = instance.request("/operator", {"action": "requeue", "job": job})
                self.assertEqual(refused["status"], 409)

    def test_concurrent_authorized_deliveries_do_not_lose_work(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                jobs = [
                    instance.agent(token, "submit", key=f"k{i}", message=MSG)["job"]
                    for i in range(10)
                ]
                leases = []
                for _ in range(10):
                    claim = instance.worker("claim")
                    leases.append((claim["job"], claim["lease"]))
                failures = []

                def deliver(job_id, lease):
                    try:
                        instance.request(
                            "/worker",
                            {"action": "deliver", "job": job_id, "lease": lease})
                    except BaseException as exc:  # noqa: BLE001
                        failures.append(exc)

                threads = [threading.Thread(target=deliver, args=pair) for pair in leases]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(20)
                self.assertEqual(failures, [])
                report = evaluate(instance.snapshot(), required_jobs=jobs)
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], 10)
                self.assertEqual(report["mailbox_deliveries"], 10)

    def test_concurrent_stop_versus_claimed_delivery_invariant(self):
        iterations = 12
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                deliver_outcomes = {}
                http_503 = 0
                for i in range(iterations):
                    root = instance.operator("create")
                    scope, token = root["scope"], root["token"]
                    job, lease = submit_claim(instance, token, f"k{i}")
                    result = run_pair(
                        lambda job=job, lease=lease: instance.request(
                            "/worker", {"action": "deliver", "job": job, "lease": lease}),
                        lambda scope=scope: instance.request(
                            "/operator", {"action": "stop", "scope": scope}),
                    )
                    self.assertIsInstance(result.get("a"), dict,
                                          msg=("deliver raised", result.get("a")))
                    self.assertIsInstance(result.get("b"), dict,
                                          msg=("stop raised", result.get("b")))
                    self.assertIn(result["a"]["status"], (200, 503))
                    self.assertIn(result["b"]["status"], (200, 503))
                    if 503 in (result["a"]["status"], result["b"]["status"]):
                        http_503 += 1
                    if result["a"]["status"] == 200:
                        outcome = result["a"]["body"]["status"]
                        deliver_outcomes[outcome] = deliver_outcomes.get(outcome, 0) + 1
                        self.assertIn(outcome, ("delivered", "blocked", "already_delivered"))
                report = evaluate(instance.snapshot())
                print(f"[race:{mode}] deliver_outcomes={deliver_outcomes} "
                      f"prohibited_deliveries={report['prohibited_deliveries']} "
                      f"http_503={http_503} mailbox={report['mailbox_deliveries']}")
                self.assertEqual(report["integrity_errors"], [], msg=(mode, report))
                if mode in STRONG:
                    self.assertEqual(report["prohibited_deliveries"], 0,
                                     msg=(mode, report["violations"]))


if __name__ == "__main__":
    unittest.main()
