"""Finite-game recoverability: solver soundness and the measured intervention windows."""
import unittest

from northstar_sim.analysis.recoverability import (
    DelegationGame, Game, NOOP, ReleaseGame, TURN_ORDERS,
    analyze, latest_intervention_tick, solve,
)
from northstar_sim.delegated_stop import DelegationBroker, WeakDelegationBroker
from northstar_sim.irreversible_release import MonitorOnlyReleaseBroker, ReleaseBroker

HORIZON = 5


class SolverTests(unittest.TestCase):
    def test_already_violated_state_is_not_recoverable(self):
        game = DelegationGame(WeakDelegationBroker, max_pending=1)
        state = game.initial()
        state.effects.append({"job_id": "job-1", "scope_id": "task-root",
                              "effect": "consequential", "executed_after_stop": False})
        state.scopes["task-root"].active = False
        self.assertFalse(solve(game, HORIZON, initial_state=state)[0])

    def test_zero_horizon_requires_an_existing_safe_fallback(self):
        game = DelegationGame(DelegationBroker, max_pending=1)
        self.assertFalse(solve(game, 0)[0])
        stopped = game.apply(game.initial(), ("stop", "task-root"))
        self.assertTrue(solve(game, 0, initial_state=stopped)[0])

    def test_expiring_with_a_possible_pending_effect_is_not_recovery(self):
        for broker in (WeakDelegationBroker, DelegationBroker):
            game = DelegationGame(broker, max_pending=1)
            self.assertFalse(solve(game, 1, first_active_tick=1)[0])
            pending = game.apply(game.initial(), ("submit", "task-root", "consequential"))
            self.assertFalse(solve(game, 0, initial_state=pending)[0])
            self.assertTrue(game.violated(game.apply(pending, ("dispatch", "job-1"))))

    def test_time_budget_must_allow_reaching_every_required_scope(self):
        game = DelegationGame(DelegationBroker, scope_ids=("a", "b"))
        self.assertFalse(solve(game, 1)[0])

    def test_invalid_time_and_order_inputs_are_rejected(self):
        game = DelegationGame(DelegationBroker)
        for horizon, start, order in ((-1, 0, "operator_first"),
                                      (True, 0, "operator_first"),
                                      (2, 3, "operator_first"),
                                      (2, 0, "unspecified")):
            with self.assertRaises(ValueError):
                solve(game, horizon, start, order)

    def test_apply_never_mutates_the_caller_state(self):
        game = DelegationGame(DelegationBroker, max_pending=1)
        state = game.initial()
        successor = game.apply(state, ("submit", "task-root", "consequential"))
        self.assertEqual(len(state.jobs), 0)
        self.assertEqual(len(successor.jobs), 1)

    def test_passive_operator_loses_when_intervention_is_required(self):
        game = DelegationGame(DelegationBroker, max_pending=1)
        self.assertTrue(solve(game, HORIZON, first_active_tick=0)[0])
        self.assertFalse(solve(game, HORIZON, first_active_tick=HORIZON)[0])


class ChoiceGame(Game):
    """Guard a left/right choice. Moving first cannot predict the other choice."""
    def initial(self):
        return (None, None)

    def key(self, state):
        return state

    def violated(self, state):
        return None not in state and state[0] != state[1]

    def safe(self, state):
        return None not in state and state[0] == state[1]

    def operator_moves(self, state):
        return [("guard", "left"), ("guard", "right")] if state[1] is None else [NOOP]

    def scheduler_moves(self, state):
        return [("choose", "left"), ("choose", "right")] if state[0] is None else [NOOP]

    def adversary_moves(self, state):
        return [NOOP]

    def apply(self, state, move):
        if move == NOOP:
            return state
        return (move[1], state[1]) if move[0] == "choose" else (state[0], move[1])


class QuantifierTests(unittest.TestCase):
    def test_operator_cannot_choose_a_different_earlier_move_for_each_future_reply(self):
        self.assertFalse(solve(ChoiceGame(), 1, turn_order="operator_first")[0])

    def test_operator_can_respond_to_an_already_observed_choice(self):
        self.assertTrue(solve(ChoiceGame(), 1, turn_order="scheduler_first")[0])

    def test_adversarial_order_requires_winning_both_possible_orders(self):
        self.assertFalse(solve(ChoiceGame(), 1, turn_order="adversarial_order")[0])


class DelegationWindowTests(unittest.TestCase):
    def test_repair_widens_the_operator_intervention_window(self):
        weak = latest_intervention_tick(DelegationGame(WeakDelegationBroker, max_pending=1), HORIZON)
        repaired = latest_intervention_tick(DelegationGame(DelegationBroker, max_pending=1), HORIZON)
        self.assertTrue(weak["recoverable"] and repaired["recoverable"])
        self.assertEqual(weak["deadline"], 0)
        self.assertEqual(repaired["deadline"], 1)
        self.assertGreater(repaired["deadline"], weak["deadline"])

    def test_window_is_stable_across_queue_depth(self):
        deadlines = {depth: latest_intervention_tick(
            DelegationGame(DelegationBroker, max_pending=depth), HORIZON)["deadline"]
            for depth in (1, 2, 3)}
        self.assertEqual(set(deadlines.values()), {1})

    def test_dispatch_before_stop_removes_the_extra_tick(self):
        game = DelegationGame(DelegationBroker, max_pending=1)
        for order in ("scheduler_first", "adversarial_order"):
            self.assertEqual(latest_intervention_tick(game, HORIZON, order)["deadline"], 0)

    def test_in_flight_job_is_recoverable_only_if_stop_wins_the_race(self):
        game = DelegationGame(DelegationBroker, max_pending=1)
        pending = game.apply(game.initial(), ("submit", "task-root", "consequential"))
        self.assertTrue(solve(game, HORIZON, initial_state=pending)[0])
        for order in ("scheduler_first", "adversarial_order"):
            self.assertFalse(solve(game, HORIZON, turn_order=order, initial_state=pending)[0])

    def test_stopped_scope_with_weak_queued_work_is_not_a_safe_target(self):
        game = DelegationGame(WeakDelegationBroker)
        pending = game.apply(game.initial(), ("submit", "task-root", "useful"))
        stopped = game.apply(pending, ("stop", "task-root"))
        self.assertFalse(game.safe(stopped))
        self.assertFalse(solve(game, HORIZON, initial_state=stopped)[0])

    def test_repaired_safe_target_is_closed_under_declared_moves(self):
        game = DelegationGame(DelegationBroker)
        pending = game.apply(game.initial(), ("submit", "task-root", "consequential"))
        stopped = game.apply(pending, ("stop", "task-root"))
        for moves in (game.operator_moves, game.scheduler_moves, game.adversary_moves):
            for move in moves(stopped):
                successor = game.apply(stopped, move)
                self.assertTrue(game.safe(successor))
                self.assertFalse(game.violated(successor))


class ReleaseWindowTests(unittest.TestCase):
    def test_hard_invariant_needs_no_operator_intervention(self):
        window = latest_intervention_tick(ReleaseGame(ReleaseBroker, max_staged=1), HORIZON)
        self.assertTrue(window["recoverable"])
        self.assertFalse(window["requires_intervention"])
        self.assertIsNone(window["deadline"])

    def test_monitor_only_control_leaves_a_one_tick_window(self):
        window = latest_intervention_tick(ReleaseGame(MonitorOnlyReleaseBroker, max_staged=1), HORIZON)
        self.assertTrue(window["recoverable"])
        self.assertTrue(window["requires_intervention"])
        self.assertEqual(window["deadline"], 1)

    def test_staged_danger_is_not_safe_merely_because_time_expires(self):
        game = ReleaseGame(MonitorOnlyReleaseBroker)
        pending = game.apply(game.initial(), ("stage", "protected_report", "unapproved_sink"))
        self.assertFalse(solve(game, 0, initial_state=pending)[0])
        self.assertFalse(solve(game, 1, first_active_tick=1)[0])
        self.assertTrue(solve(game, 1, initial_state=pending)[0])

    def test_revoked_staged_token_cannot_escape_a_release_fallback(self):
        game = ReleaseGame(MonitorOnlyReleaseBroker)
        pending = game.apply(game.initial(), ("stage", "protected_report", "unapproved_sink"))
        safe = game.apply(pending, ("revoke", "protected_report", "unapproved_sink"))
        self.assertTrue(game.safe(safe))
        self.assertEqual(len(safe.staged), 1)
        for move in game.adversary_moves(safe):
            successor = game.apply(safe, move)
            self.assertTrue(game.safe(successor))
            self.assertFalse(game.violated(successor))

    def test_repaired_release_target_preserves_benign_work(self):
        game = ReleaseGame(ReleaseBroker)
        state = game.apply(game.initial(), ("stage", "public_report", "approved_site"))
        state = game.apply(state, ("commit", "stage-1"))
        self.assertTrue(game.safe(state))
        self.assertEqual(len(state.committed_releases), 1)


class ReportTests(unittest.TestCase):
    def test_analyze_covers_both_environments_and_controls(self):
        report = analyze(horizon=4, depths=(1, 2))
        self.assertEqual(len(report["delegation"]), 4 * len(TURN_ORDERS))
        self.assertEqual(len(report["release"]), 4)
        for row in report["delegation"] + report["release"]:
            self.assertIn(row["control"], ("starting", "repaired"))
            self.assertIn(row["turn_order"], TURN_ORDERS)
            self.assertEqual(row["recoverable"], row["operator_can_reach_safe_fallback"])
        self.assertEqual(set(report["safe_fallbacks"]), {"delegation", "release"})
        self.assertTrue(report["scope_limits"])

    def test_analysis_is_deterministic(self):
        self.assertEqual(analyze(horizon=3, depths=(1,)), analyze(horizon=3, depths=(1,)))


if __name__ == "__main__":
    unittest.main()
