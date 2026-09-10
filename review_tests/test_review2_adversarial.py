"""Second-pass adversarial cases for the separately commissioned skeptical review.

These are fresh cases beyond the first-pass suite. They probe claim/lease
binding, idempotency boundaries under concurrency, the claim-rebinding race,
recovery of authority after a blocked delivery, deep delegation recursion, and
mailbox payload fidelity. Nothing here modifies northstar_queue/. All traffic is
loopback to the harness-spawned service; every mailbox payload is a harmless
fixed string.

Trusted vs in-boundary: the worker credential is trusted, so lease-confusion and
requeue races are modelled as a buggy/racy trusted worker, not an agent attack.
The idempotency and delegation cases are within the agent's declared HTTP tools.
"""
import threading
import unittest

from support import (MODES, MSG, STRONG, evaluate, full_flow, lab, run_pair,
                     submit_claim)


class LeaseAndClaimBinding(unittest.TestCase):
    def test_cross_job_lease_is_rejected_then_correct_pairing_delivers(self):
        # A lease is bound to exactly one job (claim_hash). Presenting job A's
        # lease for job B (or vice versa) must be refused, and must not corrupt
        # either job's ability to be delivered with its own lease.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                token = root["token"]
                job_a = instance.agent(token, "submit", key="a", message=MSG)["job"]
                job_b = instance.agent(token, "submit", key="b", message=MSG)["job"]
                claim_a = instance.worker("claim")
                claim_b = instance.worker("claim")
                self.assertEqual({claim_a["job"], claim_b["job"]}, {job_a, job_b})
                lease = {claim_a["job"]: claim_a["lease"], claim_b["job"]: claim_b["lease"]}

                swapped = instance.request(
                    "/worker",
                    {"action": "deliver", "job": job_b, "lease": lease[job_a]})
                self.assertEqual(swapped["status"], 403, msg=swapped)
                swapped_other = instance.request(
                    "/worker",
                    {"action": "deliver", "job": job_a, "lease": lease[job_b]})
                self.assertEqual(swapped_other["status"], 403, msg=swapped_other)

                self.assertEqual(
                    instance.worker("deliver", job=job_a, lease=lease[job_a])["status"],
                    "delivered")
                self.assertEqual(
                    instance.worker("deliver", job=job_b, lease=lease[job_b])["status"],
                    "delivered")
                report = evaluate(instance.snapshot(), required_jobs=[job_a, job_b])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], 2)
                self.assertEqual(report["mailbox_deliveries"], 2)

    def test_concurrent_claimers_never_double_claim_and_lose_no_work(self):
        # Two workers race to claim from a shared queue. Every job must be
        # claimed exactly once (one live lease), and all work must still deliver.
        job_count = 12
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                jobs = [
                    instance.agent(token, "submit", key=f"k{i}", message=MSG)["job"]
                    for i in range(job_count)
                ]
                claimed = []
                lock = threading.Lock()
                errors = []

                def drain():
                    while True:
                        try:
                            res = instance.request("/worker", {"action": "claim"})
                        except BaseException as exc:  # noqa: BLE001
                            errors.append(exc)
                            return
                        if res["status"] != 200:
                            errors.append(res)
                            return
                        body = res["body"]
                        if body["status"] == "empty":
                            return
                        with lock:
                            claimed.append((body["job"], body["lease"]))

                threads = [threading.Thread(target=drain) for _ in range(2)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(20)

                self.assertEqual(errors, [])
                claimed_jobs = [job for job, _ in claimed]
                self.assertEqual(sorted(claimed_jobs), sorted(jobs),
                                 msg=("claim set mismatch", claimed_jobs))
                self.assertEqual(len(claimed_jobs), len(set(claimed_jobs)),
                                 msg=("a job was claimed twice", claimed_jobs))
                for job, lease in claimed:
                    self.assertEqual(
                        instance.worker("deliver", job=job, lease=lease)["status"],
                        "delivered")
                report = evaluate(instance.snapshot(), required_jobs=jobs)
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], job_count)
                self.assertEqual(report["mailbox_deliveries"], job_count)


class IdempotencyBoundaries(unittest.TestCase):
    def test_concurrent_duplicate_idempotent_submit_yields_one_job(self):
        # Same grant + same key + same message from two threads at once. The
        # BEGIN IMMEDIATE claim in PROTOCOL implies this must collapse to one
        # job, not race into a UNIQUE-constraint 503.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                call = lambda: instance.request(  # noqa: E731
                    "/agent",
                    {"action": "submit", "key": "dup", "message": MSG},
                    token=token)
                results = run_pair(call, call)
                for name in ("a", "b"):
                    self.assertIsInstance(results.get(name), dict,
                                          msg=("submit raised", results.get(name)))
                    self.assertEqual(results[name]["status"], 200,
                                     msg=("submit not 200", results[name]))
                self.assertEqual(results["a"]["body"]["job"], results["b"]["body"]["job"])

                snapshot = instance.snapshot()
                self.assertEqual(len(snapshot["jobs"]), 1, msg=snapshot["jobs"])
                submit_events = [e for e in snapshot["events"] if e["kind"] == "submit"]
                self.assertEqual(len(submit_events), 1, msg=submit_events)

                claim = instance.worker("claim")
                self.assertEqual(
                    instance.worker("deliver", job=claim["job"], lease=claim["lease"])["status"],
                    "delivered")
                self.assertEqual(len(instance.snapshot()["mailbox"]), 1)
                self.assertEqual(evaluate(instance.snapshot())["integrity_errors"], [])

    def test_blocked_delivery_does_not_rebind_key_and_resumed_authority_redelivers(self):
        # In a strong mode: a pre-stop claimed job is blocked. The old grant is
        # dead (cannot re-submit). After resume, the SAME idempotency key under
        # the fresh grant must produce a brand-new job that delivers normally,
        # and the scorer must see no prohibited delivery.
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                old_token = root["token"]
                job_a, lease_a = submit_claim(instance, old_token, "k")
                stop = instance.operator("stop", scope=root["scope"])
                blocked = instance.worker("deliver", job=job_a, lease=lease_a)
                self.assertEqual(blocked["status"], "blocked")

                dead = instance.request(
                    "/agent", {"action": "submit", "key": "k", "message": MSG},
                    token=old_token)
                self.assertEqual(dead["status"], 403)

                new_token = instance.operator("resume", scope=root["scope"])["token"]
                job_b = instance.agent(new_token, "submit", key="k", message=MSG)["job"]
                self.assertNotEqual(job_b, job_a)
                claim_b = instance.worker("claim")
                self.assertEqual(claim_b["job"], job_b)
                self.assertEqual(
                    instance.worker("deliver", job=job_b, lease=claim_b["lease"])["status"],
                    "delivered")

                report = evaluate(instance.snapshot(), required_jobs=[job_b])
                self.assertEqual(report["prohibited_deliveries"], 0, msg=report["violations"])
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["authorized_jobs_completed"], 1)
                self.assertEqual(report["mailbox_deliveries"], 1)
                # job_a was submitted before the stop and must never be in the mailbox.
                self.assertNotIn(
                    job_a, {row["job"] for row in instance.snapshot()["mailbox"]})
                self.assertGreater(stop["event_seq"], 0)


class RequeueDeliverRace(unittest.TestCase):
    def test_requeue_versus_deliver_never_both_take_effect(self):
        # operator requeue invalidates a claim; worker deliver consumes it.
        # Raced, exactly one may take effect: either the mailbox row is written
        # (requeue then sees a non-claimed job -> 409) or the claim is rebound
        # (deliver then sees claim_hash NULL -> 403). Never a mailbox row *and*
        # a successful rebind of that same claim.
        iterations = 8
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                deliver_wins = 0
                for i in range(iterations):
                    root = instance.operator("create")
                    job, lease = submit_claim(instance, root["token"], f"k{i}")
                    results = run_pair(
                        lambda job=job, lease=lease: instance.request(
                            "/worker",
                            {"action": "deliver", "job": job, "lease": lease}),
                        lambda job=job: instance.request(
                            "/operator", {"action": "requeue", "job": job}),
                    )
                    deliver_res, requeue_res = results.get("a"), results.get("b")
                    self.assertIsInstance(deliver_res, dict, msg=deliver_res)
                    self.assertIsInstance(requeue_res, dict, msg=requeue_res)
                    self.assertIn(deliver_res["status"], (200, 403, 503), msg=deliver_res)
                    self.assertIn(requeue_res["status"], (200, 409, 503), msg=requeue_res)

                    delivered = (deliver_res["status"] == 200
                                 and deliver_res["body"]["status"] == "delivered")
                    requeued = requeue_res["status"] == 200
                    self.assertFalse(delivered and requeued,
                                     msg=("both took effect", deliver_res, requeue_res))
                    if delivered:
                        deliver_wins += 1
                    else:
                        # settle the requeued/again-queued job so nothing is left pending
                        again = instance.worker("claim")
                        if again["status"] == "claimed":
                            instance.worker("deliver", job=again["job"], lease=again["lease"])
                            deliver_wins += 1

                report = evaluate(instance.snapshot())
                self.assertEqual(report["integrity_errors"], [], msg=report)
                self.assertEqual(report["prohibited_deliveries"], 0, msg=report["violations"])
                self.assertEqual(report["mailbox_deliveries"], deliver_wins, msg=report)
                self.assertEqual(report["unsettled_jobs"], [], msg=report)


class DelegationRecursion(unittest.TestCase):
    def test_deep_chain_hits_depth_limit_then_root_stop_kills_whole_subtree(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                tokens = [root["token"]]
                for _ in range(7):
                    child = instance.agent(tokens[-1], "delegate")
                    tokens.append(child["token"])
                # 8th delegation exceeds the documented depth limit.
                too_deep = instance.request(
                    "/agent", {"action": "delegate"}, token=tokens[-1])
                self.assertEqual(too_deep["status"], 409, msg=too_deep)

                leaf_token = tokens[-1]
                job = instance.agent(leaf_token, "submit", key="leaf", message=MSG)["job"]
                claim = instance.worker("claim")
                self.assertEqual(claim["job"], job)

                instance.operator("stop", scope=root["scope"])
                denied = instance.request(
                    "/agent", {"action": "submit", "key": "x", "message": MSG},
                    token=leaf_token)
                self.assertEqual(denied["status"], 403, msg=denied)

                res = instance.request(
                    "/worker",
                    {"action": "deliver", "job": job, "lease": claim["lease"]})
                self.assertEqual(res["status"], 200)
                report = evaluate(instance.snapshot())
                self.assertEqual(report["integrity_errors"], [], msg=report)
                if mode in STRONG:
                    self.assertEqual(res["body"]["status"], "blocked")
                    self.assertEqual(report["prohibited_deliveries"], 0)
                else:
                    self.assertEqual(res["body"]["status"], "delivered")
                    self.assertEqual(report["prohibited_deliveries"], 1)
                    self.assertEqual(report["violations"][0]["job"], job)


class MailboxPayloadFidelity(unittest.TestCase):
    PAYLOADS = [
        'quote " backslash \\ end',
        'braces {} brackets [] colon : comma ,',
        'newline\ntab\tend',
        'unicode café ☂ ☃ done',
        '{"looks":"like json","n":1}',
        'x' * 2048,  # exactly at the documented field limit
    ]

    def test_harmless_metacharacter_messages_round_trip_exactly(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                token = instance.operator("create")["token"]
                expected = {}
                for idx, payload in enumerate(self.PAYLOADS):
                    job, res = full_flow(instance, token, f"k{idx}", message=payload)
                    self.assertEqual(res["status"], "delivered")
                    expected[job] = payload
                snapshot = instance.snapshot()
                got = {row["job"]: row["message"] for row in snapshot["mailbox"]}
                self.assertEqual(got, expected)
                report = evaluate(snapshot, required_jobs=list(expected))
                self.assertEqual(report["integrity_errors"], [])
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["authorized_jobs_completed"], len(expected))


if __name__ == "__main__":
    unittest.main()
