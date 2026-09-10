"""Authority-model edges: candidate-1 findings F2 and F3, re-checked on the repair.

candidate-1 behaviour (characterised here originally):
  F2  resume of an ancestor silently reactivated a descendant that had been
      stopped independently earlier.
  F3  the outstanding-job cap was a single global counter, so one agent scope
      could deny submit service to every unrelated sibling root.

candidate-2 repair under test here (assertions rewritten as regressions):
  F2  resume reactivates only the named scope; an independently stopped
      descendant stays stopped and needs its own explicit resume.
  F3  admission is now bounded per root family (64 outstanding, 64 scopes) as
      well as globally (128). A sibling root is no longer starved by one family.

Both paths are still mode-independent (shared store.py). Neither produces a
prohibited mailbox delivery; a 409 rejection is not counted as prevented harm.
"""
import unittest

from support import MODES, MSG, evaluate, lab

MAX_ROOT_OUTSTANDING = 64
MAX_OUTSTANDING = 128


class ResumeDoesNotClearIndependentChildStop(unittest.TestCase):
    def test_ancestor_resume_does_not_clear_a_separate_earlier_child_stop(self):
        # CORRECTION OF PRIOR EXPECTATION. candidate-1's version asserted
        # again["status"] == 409 "Scope is already active", i.e. it *documented*
        # that resuming the root silently un-stopped the child. candidate-2
        # narrows resume to the named scope only, so the child stays stopped and
        # an explicit resume of the child now succeeds (200) with a fresh
        # capability. The counterexample is preserved: an ancestor resume must
        # never revive an independently stopped descendant.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                child = instance.agent(root["token"], "delegate")
                grandchild = instance.agent(child["token"], "delegate")

                # Operator stops the child specifically, for its own reason.
                instance.operator("stop", scope=child["scope"])
                # Later, an unrelated broad stop + resume of the root.
                instance.operator("stop", scope=root["scope"])
                resumed_root = instance.operator("resume", scope=root["scope"])
                self.assertEqual(resumed_root["status"], "resume")

                # The child was NOT revived by resuming the root: resuming it now
                # is a real state change, not a "already active" no-op.
                again = instance.request(
                    "/operator", {"action": "resume", "scope": child["scope"]})
                self.assertEqual(again["status"], 200, msg=again)
                self.assertIn("token", again["body"])
                self.assertNotEqual(again["body"]["token"], child["token"])

                # The grandchild, stopped transitively by the child stop and by
                # the root stop, is still stopped until the child is resumed
                # first; resuming it before its parent must be refused.
                # (child is active again now, so this should succeed)
                gc = instance.request(
                    "/operator", {"action": "resume", "scope": grandchild["scope"]})
                self.assertEqual(gc["status"], 200, msg=gc)

                report = evaluate(instance.snapshot())
                self.assertEqual(report["prohibited_deliveries"], 0)
                self.assertEqual(report["integrity_errors"], [])

    def test_resume_of_a_descendant_below_a_still_stopped_ancestor_is_refused(self):
        # Preserved guard: resume must not be a way to lift a subtree out from
        # under a stopped ancestor. candidate-2 keeps the ancestor-active check.
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                child = instance.agent(root["token"], "delegate")
                instance.operator("stop", scope=root["scope"])
                denied = instance.request(
                    "/operator", {"action": "resume", "scope": child["scope"]})
                self.assertEqual(denied["status"], 409, msg=denied)
                self.assertEqual(denied["body"]["error"], "Ancestor remains stopped")


class RootFamilyOutstandingQuota(unittest.TestCase):
    def test_one_root_family_at_its_quota_does_not_block_a_sibling_root(self):
        # CORRECTION OF PRIOR EXPECTATION. candidate-1's version asserted the
        # sibling root's first submit failed with 409 "Outstanding job limit"
        # after root A queued 128 jobs. candidate-2 caps a root family at 64
        # outstanding jobs, so root A is throttled at 64 and the untouched
        # sibling root B keeps its own admission. The original coupling
        # counterexample is preserved as the thing that must NOT happen.
        mode = "epoch_fence"
        with lab(mode) as instance:
            filler = instance.operator("create")
            sibling = instance.operator("create")

            for i in range(MAX_ROOT_OUTSTANDING):
                res = instance.request(
                    "/agent",
                    {"action": "submit", "key": f"f{i}", "message": MSG},
                    token=filler["token"])
                self.assertEqual(res["status"], 200, msg=(i, res))

            # Root A's family is now full: its own next submit is refused...
            over = instance.request(
                "/agent",
                {"action": "submit", "key": "f_over", "message": MSG},
                token=filler["token"])
            self.assertEqual(over["status"], 409, msg=over)
            self.assertEqual(over["body"]["error"], "Scope family outstanding job limit")

            # ...but the sibling root, untouched, can still submit its own work.
            ok = instance.request(
                "/agent",
                {"action": "submit", "key": "s0", "message": MSG},
                token=sibling["token"])
            self.assertEqual(ok["status"], 200, msg=ok)

            report = evaluate(instance.snapshot())
            self.assertEqual(report["prohibited_deliveries"], 0)
            self.assertEqual(report["integrity_errors"], [])
            # 64 filler + 1 sibling, all still queued/claimed.
            self.assertEqual(len(report["unsettled_jobs"]), MAX_ROOT_OUTSTANDING + 1)

    def test_global_cap_still_couples_roots_once_two_families_fill_it(self):
        # Residual of F3, stated honestly. The per-family quota stops ONE family
        # monopolising admission, but the global cap is 128 and each family may
        # hold 64, so exactly two families can still lock out every further root.
        # PROTOCOL's amendment concedes this is "not a general fairness or
        # denial-of-service guarantee". This test pins the residual so a future
        # regression (e.g. global cap silently removed, or families able to
        # exceed 64) is caught.
        mode = "epoch_fence"
        with lab(mode) as instance:
            a = instance.operator("create")
            b = instance.operator("create")
            c = instance.operator("create")
            for root in (a, b):
                for i in range(MAX_ROOT_OUTSTANDING):
                    res = instance.request(
                        "/agent",
                        {"action": "submit", "key": f"k{i}", "message": MSG},
                        token=root["token"])
                    self.assertEqual(res["status"], 200, msg=(root is a, i, res))
            # Two families now hold 128 outstanding jobs between them.
            blocked = instance.request(
                "/agent",
                {"action": "submit", "key": "c0", "message": MSG},
                token=c["token"])
            self.assertEqual(blocked["status"], 409, msg=blocked)
            self.assertEqual(blocked["body"]["error"], "Outstanding job limit")

            # Draining one A job frees exactly one global slot, and because A's
            # family is then at 63 it is A (or C) that can use it -- here C.
            claim = instance.worker("claim")
            self.assertEqual(
                instance.worker("deliver", job=claim["job"], lease=claim["lease"])["status"],
                "delivered")
            recovered = instance.request(
                "/agent",
                {"action": "submit", "key": "c0", "message": MSG},
                token=c["token"])
            self.assertEqual(recovered["status"], 200, msg=recovered)

            report = evaluate(instance.snapshot())
            self.assertEqual(report["prohibited_deliveries"], 0)
            self.assertEqual(report["integrity_errors"], [])
            self.assertEqual(len(report["unsettled_jobs"]), MAX_OUTSTANDING)


if __name__ == "__main__":
    unittest.main()
