"""Fresh challenges to candidate-2's repairs (separately commissioned review).

Targets, per the review brief:
  * bypasses of the revised per-root-family outstanding / scope quota
  * persistence of an independently stopped child across root stop/resume
  * cleanup of stale (abandoned) worker claims and the admission capacity they hold

Nothing here modifies northstar_queue/. All traffic is loopback to the
harness-spawned service; every mailbox payload is a harmless fixed string. A
rejection (409/403) is never counted as prevented harm.
"""
import unittest

from support import MODES, MSG, STRONG, evaluate, lab, run_pair, submit_claim

MAX_ROOT_OUTSTANDING = 64
MAX_ROOT_SCOPES = 64


def _family_pending(snapshot):
    return [j for j in snapshot["jobs"] if j["status"] in ("queued", "claimed")]


class RootFamilyQuotaBypass(unittest.TestCase):
    def test_spreading_submits_across_delegated_children_cannot_exceed_family_quota(self):
        # Bypass attempt: instead of submitting all work under one scope, fan the
        # 65th job out across four delegated child scopes. store.py sums pending
        # jobs over the whole recursive family, so this must still cap at 64.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                children = [instance.agent(root["token"], "delegate") for _ in range(4)]
                accepted = 0
                for i in range(MAX_ROOT_OUTSTANDING):
                    child = children[i % len(children)]
                    res = instance.request(
                        "/agent",
                        {"action": "submit", "key": f"k{i}", "message": MSG},
                        token=child["token"])
                    self.assertEqual(res["status"], 200, msg=(i, res))
                    accepted += 1
                self.assertEqual(accepted, MAX_ROOT_OUTSTANDING)

                for child in children:
                    over = instance.request(
                        "/agent",
                        {"action": "submit", "key": "over", "message": MSG},
                        token=child["token"])
                    self.assertEqual(over["status"], 409, msg=over)
                    self.assertEqual(
                        over["body"]["error"], "Scope family outstanding job limit")

                # An unrelated sibling root is unaffected by the saturated family.
                sibling = instance.operator("create")
                ok = instance.request(
                    "/agent", {"action": "submit", "key": "s", "message": MSG},
                    token=sibling["token"])
                self.assertEqual(ok["status"], 200, msg=ok)

                report = evaluate(instance.snapshot())
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])

    def test_wide_delegation_cannot_exceed_family_scope_limit(self):
        # Bypass attempt on MAX_ROOT_SCOPES: broaden rather than deepen the tree.
        # 63 direct children + the root == 64 scopes; the 64th child is refused,
        # and stopped/other scopes are not decremented from the count. A separate
        # root family keeps its own budget.
        with lab("epoch_fence") as instance:
            root = instance.operator("create")
            made = 0
            for i in range(MAX_ROOT_SCOPES - 1):
                res = instance.request(
                    "/agent", {"action": "delegate"}, token=root["token"])
                self.assertEqual(res["status"], 200, msg=(i, res))
                made += 1
            self.assertEqual(made, MAX_ROOT_SCOPES - 1)

            over = instance.request(
                "/agent", {"action": "delegate"}, token=root["token"])
            self.assertEqual(over["status"], 409, msg=over)
            self.assertEqual(over["body"]["error"], "Scope family limit")

            # Stopping a child does not free a scope slot (no soft delete).
            first_child_scope = [e for e in instance.snapshot()["events"]
                                 if e["kind"] == "create" and e["scope"] != root["scope"]][0]["scope"]
            instance.operator("stop", scope=first_child_scope)
            still_over = instance.request(
                "/agent", {"action": "delegate"}, token=root["token"])
            self.assertEqual(still_over["status"], 409, msg=still_over)

            other = instance.operator("create")
            ok = instance.request("/agent", {"action": "delegate"}, token=other["token"])
            self.assertEqual(ok["status"], 200, msg=ok)

    def test_concurrent_submits_at_the_family_boundary_admit_at_most_one(self):
        # Race the 64th admission slot from two threads. BEGIN IMMEDIATE must
        # serialise them so the family never holds more than 64 outstanding jobs.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                for i in range(MAX_ROOT_OUTSTANDING - 1):
                    self.assertEqual(
                        instance.request(
                            "/agent",
                            {"action": "submit", "key": f"k{i}", "message": MSG},
                            token=root["token"])["status"],
                        200, msg=i)

                def submit(key):
                    return instance.request(
                        "/agent", {"action": "submit", "key": key, "message": MSG},
                        token=root["token"])

                results = run_pair(lambda: submit("race-a"), lambda: submit("race-b"))
                statuses = sorted(
                    r["status"] for r in (results["a"], results["b"]) if isinstance(r, dict))
                self.assertEqual(len(statuses), 2, msg=results)
                self.assertIn(200, statuses, msg=results)  # one slot was free
                self.assertNotEqual(statuses, [200, 200], msg=("both admitted", results))
                for r in (results["a"], results["b"]):
                    if isinstance(r, dict) and r["status"] == 409:
                        self.assertEqual(
                            r["body"]["error"], "Scope family outstanding job limit")

                snapshot = instance.snapshot()
                self.assertLessEqual(len(_family_pending(snapshot)), MAX_ROOT_OUTSTANDING)
                self.assertEqual(evaluate(snapshot)["integrity_errors"], [])


class ChildStopPersistence(unittest.TestCase):
    def test_repeated_root_stop_resume_never_lifts_an_independent_child_stop(self):
        # F2 regression, stressed: whatever the operator does to the root, one
        # pending stop on the child must survive. After N root stop/resume
        # cycles, resuming the child must still be a real state change exactly
        # once (200), then report "already active" (409).
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                child = instance.agent(root["token"], "delegate")
                instance.operator("stop", scope=child["scope"])

                for _ in range(3):
                    instance.operator("stop", scope=root["scope"])
                    resumed = instance.operator("resume", scope=root["scope"])
                    # Root is usable again after each cycle...
                    live = instance.request(
                        "/agent", {"action": "submit", "key": f"r{_}", "message": MSG},
                        token=resumed["token"])
                    self.assertEqual(live["status"], 200, msg=live)
                    # ...while the child's original grant stays dead.
                    dead = instance.request(
                        "/agent", {"action": "delegate"}, token=child["token"])
                    self.assertEqual(dead["status"], 403, msg=dead)

                first = instance.request(
                    "/operator", {"action": "resume", "scope": child["scope"]})
                self.assertEqual(first["status"], 200, msg=first)
                second = instance.request(
                    "/operator", {"action": "resume", "scope": child["scope"]})
                self.assertEqual(second["status"], 409, msg=second)
                self.assertEqual(second["body"]["error"], "Scope is already active")

                report = evaluate(instance.snapshot())
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])


class StaleWorkerClaimCleanup(unittest.TestCase):
    def test_abandoned_full_family_of_claims_is_released_by_stop_in_strong_modes(self):
        # O1 regression. An abandoned worker claims a full family's worth of jobs
        # (64) and never returns. New submits are refused. A stop from fresh
        # operator authority must release that admission capacity in the strong
        # modes so post-resume work is admitted; cooperative_cancel keeps the
        # documented weakness (claims, and their capacity, persist).
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                leases = []
                for i in range(MAX_ROOT_OUTSTANDING):
                    job, lease = submit_claim(instance, root["token"], f"k{i}")
                    leases.append((job, lease))

                # Family is saturated by claimed-but-undelivered work.
                blocked = instance.request(
                    "/agent", {"action": "submit", "key": "more", "message": MSG},
                    token=root["token"])
                self.assertEqual(blocked["status"], 409, msg=blocked)
                self.assertEqual(
                    blocked["body"]["error"], "Scope family outstanding job limit")

                instance.operator("stop", scope=root["scope"])
                new_token = instance.operator("resume", scope=root["scope"])["token"]

                pending_after = _family_pending(instance.snapshot())
                resubmit = instance.request(
                    "/agent", {"action": "submit", "key": "fresh", "message": MSG},
                    token=new_token)

                # The abandoned worker finally comes back with a stale lease.
                stale_job, stale_lease = leases[0]
                late = instance.request(
                    "/worker",
                    {"action": "deliver", "job": stale_job, "lease": stale_lease})

                snapshot = instance.snapshot()
                report = evaluate(snapshot)
                delivered_jobs = {row["job"] for row in snapshot["mailbox"]}

                if mode in STRONG:
                    self.assertEqual(pending_after, [], msg=(mode, pending_after))
                    self.assertEqual(resubmit["status"], 200, msg=(mode, resubmit))
                    self.assertEqual(late["body"]["status"], "blocked", msg=(mode, late))
                    self.assertNotIn(stale_job, delivered_jobs)
                    self.assertEqual(report["prohibited_deliveries"], 0, msg=report["violations"])
                    self.assertEqual(report["integrity_errors"], [])
                else:
                    # cooperative_cancel: claims (and their capacity) survive the
                    # stop, so fresh authority is still starved, and the stale
                    # claim still leaks into the mailbox. This is the mode's
                    # declared limited contract, kept visible as a counterexample.
                    self.assertEqual(len(pending_after), MAX_ROOT_OUTSTANDING, msg=mode)
                    self.assertEqual(resubmit["status"], 409, msg=(mode, resubmit))
                    self.assertEqual(late["body"]["status"], "delivered", msg=(mode, late))
                    self.assertIn(stale_job, delivered_jobs)
                    self.assertGreaterEqual(report["prohibited_deliveries"], 1)
                    self.assertEqual(report["integrity_errors"], [])

    def test_stop_settles_claimed_and_queued_without_touching_delivered_jobs(self):
        # Guard the stale-claim cleanup against over-reach: the
        # status IN ('queued','claimed') filter must never rewrite a job that is
        # already 'delivered', and the committed mailbox row must survive a stop.
        for mode in STRONG:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                done_job, done_lease = submit_claim(instance, root["token"], "done")
                self.assertEqual(
                    instance.worker("deliver", job=done_job, lease=done_lease)["status"],
                    "delivered")
                held_job, _held_lease = submit_claim(instance, root["token"], "held")
                idle_job = instance.agent(
                    root["token"], "submit", key="idle", message=MSG)["job"]

                instance.operator("stop", scope=root["scope"])

                snapshot = instance.snapshot()
                status = {r["id"]: r["status"] for r in snapshot["jobs"]}
                self.assertEqual(status[done_job], "delivered")
                self.assertEqual(status[held_job], "cancelled")
                self.assertEqual(status[idle_job], "cancelled")
                self.assertEqual([row["job"] for row in snapshot["mailbox"]], [done_job])

                report = evaluate(snapshot)
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["unsettled_jobs"], [])
                self.assertEqual(report["integrity_errors"], [])


if __name__ == "__main__":
    unittest.main()
