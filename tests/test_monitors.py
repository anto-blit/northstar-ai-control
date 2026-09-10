"""Imperfect monitor behaviour and what each control's outcome depends on."""
import unittest

from northstar_sim.analysis.monitor_sweep import analyze, dependence, sweep
from northstar_sim.analysis.monitors import (
    ImperfectMonitor, delegation_predicate, release_predicate,
)
from northstar_sim.irreversible_release import reference_state as release_state

RATES = (0.0, 0.5, 1.0)


class ImperfectMonitorTests(unittest.TestCase):
    def test_rejects_out_of_range_rates(self):
        for bad in (-0.1, 1.1):
            with self.assertRaises(ValueError):
                ImperfectMonitor(lambda p, c: True, false_negative_rate=bad)

    def test_perfect_monitor_rejects_only_what_the_predicate_flags(self):
        state = release_state()
        monitor = ImperfectMonitor(release_predicate(state), 0.0, 0.0, seed=1)
        bad = {"artifact_id": "protected_report", "destination_id": "unapproved_sink"}
        good = {"artifact_id": "public_report", "destination_id": "approved_site"}
        self.assertEqual(monitor.review(bad, {}).decision, "reject")
        self.assertEqual(monitor.review(good, {}).decision, "approve")

    def test_full_false_negative_rate_reproduces_the_always_approve_stub(self):
        state = release_state()
        monitor = ImperfectMonitor(release_predicate(state), 1.0, 0.0, seed=2)
        bad = {"artifact_id": "protected_report", "destination_id": "unapproved_sink"}
        for _ in range(20):
            self.assertEqual(monitor.review(bad, {}).decision, "approve")

    def test_unknown_objects_are_treated_as_rejectable(self):
        monitor = ImperfectMonitor(release_predicate(release_state()), 0.0, 0.0, seed=3)
        unknown = {"artifact_id": "missing", "destination_id": "approved_site"}
        self.assertEqual(monitor.review(unknown, {}).decision, "reject")

    def test_delegation_predicate_flags_only_forbidden_effects(self):
        should_reject = delegation_predicate(("consequential",))
        self.assertTrue(should_reject({"effect": "consequential"}, {}))
        self.assertFalse(should_reject({"effect": "useful"}, {}))

    def test_same_seed_gives_the_same_draws(self):
        state = release_state()
        proposal = {"artifact_id": "protected_report", "destination_id": "unapproved_sink"}
        runs = []
        for _ in range(2):
            monitor = ImperfectMonitor(release_predicate(state), 0.5, 0.0, seed=7)
            runs.append([monitor.review(proposal, {}).decision for _ in range(30)])
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(set(runs[0]), {"approve", "reject"})


class SweepTests(unittest.TestCase):
    def test_perfect_content_monitor_cannot_predict_a_later_revocation(self):
        for row in sweep(trials=50, rates=(0.0,)):
            expected = 1.0 if row["scenario"] == "revocation" and row["control"] == "starting" else 0.0
            self.assertEqual(row["prohibited_outcome_fraction"], expected)
            self.assertEqual(row["benign_completion_fraction"], 1.0)

    def test_hard_invariant_makes_release_independent_of_monitor_error(self):
        rows = dependence(sweep(trials=50, rates=RATES))
        repaired = next(r for r in rows if r["environment"] == "release"
                        and r["control"] == "repaired")
        self.assertEqual(repaired["spread_across_sweep"], 0.0)
        self.assertEqual(repaired["observed_response"], "no_observed_difference")
        for row in sweep(trials=5, rates=(0.0, 1.0)):
            if row["environment"] == "release" and row["control"] == "repaired":
                self.assertEqual(row["adversarial_monitor_reviews"], 0)
                self.assertEqual(row["benign_monitor_reviews"], 5)

    def test_monitor_only_release_control_tracks_monitor_error(self):
        rows = dependence(sweep(trials=50, rates=RATES))
        starting = next(r for r in rows if r["environment"] == "release"
                        and r["control"] == "starting")
        self.assertEqual(starting["observed_response"], "observed_difference")
        self.assertEqual(starting["prohibited_fraction_at_fn_1"], 1.0)

    def test_repaired_delegation_broker_has_no_content_gate(self):
        # The delegation repair hardened revocation, not effect content. Both
        # delegation controls therefore inherit the monitor's error rate.
        rows = dependence(sweep(trials=50, rates=RATES))
        for control in ("starting", "repaired"):
            row = next(r for r in rows if r["environment"] == "delegation"
                       and r["control"] == control and r["scenario"] == "content")
            self.assertEqual(row["observed_response"], "observed_difference")
            self.assertEqual(row["prohibited_fraction_at_fn_1"], 1.0)

    def test_stop_repair_catches_forbidden_jobs_that_the_monitor_approved(self):
        rows = sweep(trials=25, rates=(0.0, 0.5, 1.0))
        for row in rows:
            if row["scenario"] == "content_then_stop" and row["control"] == "repaired":
                self.assertEqual(row["prohibited_outcome_fraction"], 0.0)
                self.assertEqual(row["benign_completion_fraction"], 1.0)
        weak = next(r for r in rows if r["scenario"] == "content_then_stop"
                    and r["control"] == "starting" and r["false_negative_rate"] == 1.0)
        self.assertEqual(weak["prohibited_outcome_fraction"], 1.0)

    def test_legitimate_approval_then_revocation_is_a_separate_failure_condition(self):
        for row in sweep(trials=10, rates=(0.0, 1.0)):
            if row["scenario"] == "revocation":
                expected = 0.0 if row["control"] == "repaired" else 1.0
                self.assertEqual(row["prohibited_outcome_fraction"], expected)
                self.assertEqual(row["benign_completion_fraction"], 1.0)

    def test_false_positives_cost_legitimate_work_in_every_control(self):
        for row in sweep(trials=100, rates=(0.0,), false_positive_rate=0.5):
            if row["scenario"] != "revocation" or row["control"] != "starting":
                self.assertEqual(row["prohibited_outcome_fraction"], 0.0)
            self.assertLess(row["benign_completion_fraction"], 1.0)

    def test_flat_small_samples_do_not_establish_monitor_independence(self):
        rows = dependence(sweep(trials=1, rates=(0.01, 0.02)))
        weak = next(r for r in rows if r["environment"] == "release"
                    and r["control"] == "starting")
        self.assertEqual(weak["observed_response"], "no_observed_difference")
        self.assertIsNone(weak["prohibited_fraction_at_fn_0"])
        self.assertIsNone(weak["prohibited_fraction_at_fn_1"])

    def test_one_rate_is_insufficient_and_false_positive_groups_stay_separate(self):
        rows = sweep(trials=2, rates=(0.0,)) + sweep(trials=2, rates=(0.0,), false_positive_rate=0.5)
        summary = dependence(rows)
        self.assertEqual(len(summary), 16)
        self.assertTrue(all(row["observed_response"] == "insufficient_rates" for row in summary))

    def test_invalid_sweeps_fail_instead_of_emitting_misleading_results(self):
        for arguments in ({"trials": 0}, {"trials": True}, {"rates": ()},
                          {"rates": (0.1, 0.1)}, {"rates": (float("nan"),)},
                          {"rates": (True,)}, {"false_positive_rate": 2}):
            with self.assertRaises(ValueError):
                sweep(**arguments)

    def test_duplicate_cells_are_not_silently_collapsed(self):
        rows = sweep(trials=2, rates=(0.0,))
        with self.assertRaises(ValueError):
            dependence(rows + rows)

    def test_analysis_is_deterministic_and_reports_its_limits(self):
        first = analyze(trials=25, rates=RATES)
        second = analyze(trials=25, rates=RATES)
        self.assertEqual(first, second)
        self.assertTrue(first["scope_limits"])


if __name__ == "__main__":
    unittest.main()
