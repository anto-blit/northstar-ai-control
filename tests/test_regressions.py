"""Counterexamples found during review, plus failure injection at the audit boundary."""
from copy import deepcopy
from dataclasses import asdict, replace
import unittest

from northstar_sim.core import Ledger
from northstar_sim.irreversible_release import ReleaseBroker, reference_state as release_state
from northstar_sim.delegated_stop import (
    DelegationBroker, WeakDelegationBroker, reference_state as stop_state,
)


class FailingLedger(Ledger):
    fail_after_append = False

    def append(self, **kwargs):
        if self.fail_after_append:
            super().append(**kwargs)
        raise OSError("injected ledger write failure")


class ReleaseRegressionTests(unittest.TestCase):
    def setUp(self):
        self.state = release_state()
        self.broker = ReleaseBroker(self.state)

    def stage(self, artifact="public_report", destination="approved_site"):
        return self.broker.stage_release("agent", artifact, destination).receipt.details["token"]

    def test_consumed_token_cannot_commit_a_later_proposal(self):
        old = self.stage()
        self.broker.commit_release("agent", old)
        current = self.stage("protected_report")
        self.assertNotEqual(old, current)
        self.assertFalse(self.broker.commit_release("agent", old).allowed)
        self.assertIn(current, self.state.staged)
        self.assertEqual(len(self.state.committed_releases), 1)
        self.assertTrue(self.broker.commit_release("agent", current).allowed)

    def test_partial_drain_does_not_overwrite_pending_proposal(self):
        first = self.stage()
        second = self.stage(destination="unapproved_sink")
        original = deepcopy(self.state.staged[second])
        self.broker.commit_release("agent", first)
        third = self.stage("protected_report")
        self.assertEqual(len({first, second, third}), 3)
        self.assertEqual(self.state.staged[second], original)
        self.assertTrue(self.broker.commit_release("agent", second).allowed)
        self.assertTrue(self.broker.commit_release("agent", third).allowed)
        self.assertEqual(len(self.state.committed_releases), 3)

    def test_new_broker_preserves_token_sequence(self):
        old = self.stage()
        self.broker.commit_release("agent", old)
        self.broker = ReleaseBroker(self.state)
        self.assertNotEqual(old, self.stage())

    def test_other_actor_cannot_consume_staged_authority(self):
        token = self.stage()
        self.assertFalse(self.broker.commit_release("other-agent", token).allowed)
        self.assertIn(token, self.state.staged)
        self.assertTrue(self.broker.commit_release("agent", token).allowed)

    def test_changed_content_requires_fresh_review(self):
        token = self.stage()
        self.state.artifacts["public_report"] = replace(
            self.state.artifacts["public_report"], body="different synthetic content")
        decision = self.broker.commit_release("agent", token)
        self.assertFalse(decision.allowed)
        self.assertIn("fresh review", decision.reason)
        self.assertEqual(self.state.committed_releases, [])
        self.assertTrue(self.broker.commit_release("agent", self.stage()).allowed)

    def test_removed_object_is_rejected_without_effect(self):
        for collection, key in [("artifacts", "public_report"), ("destinations", "approved_site")]:
            with self.subTest(collection=collection):
                self.setUp()
                token = self.stage()
                del getattr(self.state, collection)[key]
                self.assertFalse(self.broker.commit_release("agent", token).allowed)
                self.assertEqual(self.state.committed_releases, [])

    def test_receipt_details_do_not_alias_effect_history(self):
        decision = self.broker.commit_release("agent", self.stage())
        decision.receipt.details["prohibited"] = True
        self.assertFalse(self.state.irreversible_failure())
        self.assertFalse(self.state.ledger.verify_chain())


class AuditAtomicityTests(unittest.TestCase):
    def assert_atomic_failure(self, state, broker, operation, after_append):
        fault = FailingLedger(deepcopy(state.ledger.receipts))
        fault.fail_after_append = after_append
        state.ledger = fault
        before = asdict(state)
        with self.assertRaisesRegex(OSError, "injected ledger"):
            operation()
        self.assertIs(broker.state, state)
        self.assertEqual(asdict(state), before)
        self.assertTrue(state.ledger.verify_chain())
        # The same operation can be retried once recording is restored.
        state.ledger = Ledger(deepcopy(state.ledger.receipts))
        result = operation()
        self.assertIsNotNone(result.receipt)
        self.assertTrue(state.ledger.verify_chain())

    def test_release_transitions_roll_back_before_and_after_failed_append(self):
        for operation_name in ["stage", "commit", "invalidate", "reject"]:
            for after_append in [False, True]:
                with self.subTest(operation=operation_name, after_append=after_append):
                    state = release_state()
                    broker = ReleaseBroker(state)
                    if operation_name == "stage":
                        operation = lambda: broker.stage_release("agent", "public_report", "approved_site")
                    elif operation_name == "reject":
                        operation = lambda: broker.stage_release("agent", "protected_report", "unapproved_sink")
                    else:
                        token = broker.stage_release("agent", "public_report", "approved_site").receipt.details["token"]
                        if operation_name == "invalidate":
                            state.permitted_pairs.remove(("public_report", "approved_site"))
                        operation = lambda: broker.commit_release("agent", token)
                    self.assert_atomic_failure(state, broker, operation, after_append)

    def test_delegation_transitions_roll_back_before_and_after_failed_append(self):
        for broker_type in [DelegationBroker, WeakDelegationBroker]:
            for operation_name in ["submit", "stop", "dispatch", "stale"]:
                for after_append in [False, True]:
                    with self.subTest(broker=broker_type.__name__, operation=operation_name, after_append=after_append):
                        state = stop_state()
                        broker = broker_type(state)
                        if operation_name == "submit":
                            operation = lambda: broker.submit_job("agent", "task-root", "synthetic")
                        else:
                            job = broker.submit_job("agent", "task-root", "synthetic").receipt.details["job_id"]
                            if operation_name == "stop":
                                operation = lambda: broker.scoped_stop("operator", "task-root")
                            else:
                                if operation_name == "stale":
                                    state.scopes["task-root"].epoch += 1
                                operation = lambda: broker.dispatch("scheduler", job)
                        self.assert_atomic_failure(state, broker, operation, after_append)

    def test_scoped_stop_does_not_cancel_other_scopes(self):
        from northstar_sim.delegated_stop import Scope
        state = stop_state()
        state.scopes["other"] = Scope("other")
        broker = DelegationBroker(state)
        stopped = broker.submit_job("agent", "task-root", "one").receipt.details["job_id"]
        live = broker.submit_job("agent", "other", "two").receipt.details["job_id"]
        broker.scoped_stop("operator", "task-root")
        self.assertFalse(broker.dispatch("scheduler", stopped).allowed)
        self.assertTrue(broker.dispatch("scheduler", live).allowed)


if __name__ == "__main__":
    unittest.main()
