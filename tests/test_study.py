from copy import deepcopy
from pathlib import Path
import json
import unittest
from unittest.mock import patch

from northstar_sim.outcomes import score_episode
from northstar_sim.study import (
    ROOT, StudySession, arm_packet, freeze, public_case, run_episode, summarize,
    validate_plan, verify_manifest,
)


def example_plan():
    return json.loads((ROOT / "experiments/discovery-study/example/plan.json").read_text(encoding="utf-8"))


def release_actions(destination="outside"):
    return [{"verb": "stage", "artifact_id": "report", "destination_id": destination},
            {"verb": "commit", "stage_index": 0}]


class PlanTests(unittest.TestCase):
    def test_freeze_detects_plan_tampering_and_source_drift(self):
        manifest = freeze(example_plan())
        verify_manifest(manifest)
        changed = deepcopy(manifest)
        changed["plan"]["utility_floor"] = 0
        with self.assertRaisesRegex(ValueError, "content changed"):
            verify_manifest(changed)
        with patch("northstar_sim.study.source_hashes", return_value={}):
            with self.assertRaisesRegex(ValueError, "source or arm instructions changed"):
                verify_manifest(manifest)

    def test_unequal_budgets_rejected(self):
        plan = example_plan()
        plan["budgets"]["northstar"]["episodes"] += 1
        with self.assertRaisesRegex(ValueError, "identical"):
            validate_plan(plan)

    def test_related_families_cannot_cross_split(self):
        plan = example_plan()
        plan["cases"][2]["family_id"] = plan["cases"][0]["family_id"]
        with self.assertRaisesRegex(ValueError, "family leakage"):
            validate_plan(plan)

    def test_unpaired_case_rejected(self):
        plan = example_plan()
        plan["cases"].pop()
        with self.assertRaisesRegex(ValueError, "each pair"):
            validate_plan(plan)

    def test_scaffold_cannot_be_relabelled_confirmatory(self):
        plan = example_plan()
        plan["study_class"] = "confirmatory"
        with self.assertRaisesRegex(ValueError, "feasibility"):
            validate_plan(plan)

    def test_nonfinite_or_boolean_budgets_rejected(self):
        for value in (float("nan"), float("inf"), True, -1):
            plan = example_plan()
            plan["budgets"]["generic"]["tokens"] = value
            with self.assertRaises(ValueError):
                validate_plan(plan)

    def test_online_packet_excludes_labels_schedules_oracles_and_holdouts(self):
        packet = arm_packet(freeze(example_plan()), "generic")
        self.assertEqual(len(packet["cases"]), 2)
        for case in packet["cases"]:
            self.assertTrue({"oracle", "kind", "family_id", "pair_id", "schedule", "split"}.isdisjoint(case))
            self.assertNotIn("adversarial", case["case_id"])
            self.assertNotIn("benign", case["case_id"])

    def test_narrative_arm_is_identical_grammar_plus_framing(self):
        folder = ROOT / "protocol/study-arms"
        stripped = (folder / "grammar.md").read_text(encoding="utf-8").strip()
        full = (folder / "northstar.md").read_text(encoding="utf-8")
        self.assertTrue(full.startswith(stripped))
        for story in ("Camel", "Trojan", "Faust", "Pandora", "Sorcerer"):
            self.assertNotIn(story, stripped)
            self.assertIn(story, full)


class EpisodeTests(unittest.TestCase):
    def test_fixed_pairs_demonstrate_failure_prevention_and_useful_benign_work(self):
        for case in example_plan()["cases"]:
            actions = release_actions() if case["environment"] == "release" else [
                {"verb": "submit", "scope_id": "task", "effect": "digest"}]
            for control in ("starting", "repaired"):
                with self.subTest(case=case["case_id"], control=control):
                    result = run_episode(case, actions, control)
                    expected = "failure" if control == "starting" and case["kind"] == "adversarial" else "safe"
                    self.assertEqual(result["score"]["status"], expected)
                    if case["kind"] == "benign":
                        self.assertEqual(result["score"]["utility"], 1)

    def test_unfinished_queue_is_unresolved(self):
        case = deepcopy(example_plan()["cases"][2])
        case["schedule"] = []
        actions = [{"verb": "submit", "scope_id": "task", "effect": "digest"}]
        result = run_episode(case, actions, "repaired")
        self.assertEqual(result["score"]["status"], "unresolved")
        self.assertEqual(result["score"]["pending"], 1)

    def test_settlement_continues_after_last_agent_action(self):
        case = example_plan()["cases"][2]
        result = run_episode(case, [{"verb": "submit", "scope_id": "task", "effect": "digest"}], "starting")
        self.assertEqual(result["score"]["status"], "failure")
        self.assertEqual(result["events"][-1]["tick"], 2)

    def test_uncommitted_stage_is_unresolved(self):
        result = run_episode(example_plan()["cases"][1], release_actions()[:1], "repaired")
        self.assertEqual(result["score"]["status"], "unresolved")

    def test_agent_cannot_spoof_operator_or_unknown_fields(self):
        case = example_plan()["cases"][2]
        actions = [{"verb": "stop", "scope_id": "task"},
                   {"verb": "submit", "scope_id": "task", "effect": "digest", "actor": "operator"}]
        result = run_episode(case, actions, "repaired")
        proposals = [row for row in result["trace"] if row["source"] == "agent"]
        self.assertEqual([row["status"] for row in proposals], ["reject_malformed", "reject_malformed"])
        self.assertFalse(any(event["kind"] == "job_effect" for event in result["events"]))

    def test_pending_budget_holds_additional_jobs(self):
        case = deepcopy(example_plan()["cases"][2])
        case["setup"]["max_pending_jobs"] = 1
        case["schedule"] = []
        action = {"verb": "submit", "scope_id": "task", "effect": "digest"}
        result = run_episode(case, [action, action], "repaired")
        self.assertEqual(result["score"]["pending"], 1)
        self.assertEqual(result["trace"][-1]["status"], "hold")

    def test_outcome_definition_can_detect_a_gap_in_broker_policy(self):
        case = deepcopy(example_plan()["cases"][1])
        case["oracle"]["forbidden_release_pairs"] = [["report", "internal"]]
        # The current hard check permits this public release, but the separately
        # specified outcome marks it prohibited. It must still score as failure.
        result = run_episode(case, release_actions("internal"), "repaired")
        self.assertEqual(result["score"]["status"], "failure")

    def test_failure_survives_later_infrastructure_error(self):
        from northstar_sim.irreversible_release import MonitorOnlyReleaseBroker
        case = example_plan()["cases"][0]
        original = MonitorOnlyReleaseBroker.stage_release
        count = 0

        def fail_later(broker, *args, **kwargs):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("injected later fault")
            return original(broker, *args, **kwargs)

        with patch.object(MonitorOnlyReleaseBroker, "stage_release", fail_later):
            result = run_episode(case, release_actions() + release_actions()[:1], "starting")
        self.assertEqual(result["score"]["status"], "failure")
        self.assertIn("injected later fault", result["score"]["infrastructure_error"])


class SessionTests(unittest.TestCase):
    def submission(self, case_id="release-adversarial", actions=None):
        case = next(case for case in example_plan()["cases"] if case["case_id"] == case_id)
        return {"arm": "generic", "case_id": public_case(case)["case_id"], "actions": release_actions() if actions is None else actions,
                "costs": {"tokens": 5, "human_minutes": 1, "preparation_minutes": 2}}

    def test_invalid_candidates_are_charged_and_retained(self):
        session = StudySession(freeze(example_plan()))
        feedback = session.submit(self.submission(actions=[{"verb": "wait"}] * 5))
        self.assertEqual(feedback["status"], "invalid_candidate")
        self.assertEqual(session.usage["generic"]["episodes"], 1)
        self.assertEqual(session.usage["generic"]["actions"], 5)
        self.assertEqual(session.usage["generic"]["tokens"], 5)
        self.assertEqual(session.runs, [])
        self.assertTrue(session.attempts[0]["charged"])

    def test_holdout_query_has_no_feedback_and_costs_an_attempt(self):
        session = StudySession(freeze(example_plan()))
        result = session.submit(self.submission("delegation-adversarial"))
        self.assertEqual(result["status"], "invalid_candidate")
        self.assertNotIn("observations", result)
        self.assertEqual(session.usage["generic"]["episodes"], 1)

    def test_over_budget_rejected_without_execution_or_resetting_usage(self):
        plan = example_plan()
        for budget in plan["budgets"].values():
            budget["episodes"] = 1
        session = StudySession(freeze(plan))
        session.submit(self.submission())
        before = deepcopy(session.usage)
        self.assertEqual(session.submit(self.submission())["status"], "budget_rejected")
        self.assertEqual(session.usage, before)
        self.assertEqual(len(session.runs), 1)
        self.assertEqual(len(session.attempts), 2)

    def test_adaptive_submission_preserves_budget_and_hides_offline_scores(self):
        session = StudySession(freeze(example_plan()))
        first = session.submit(self.submission())
        self.assertNotIn("score", first)
        self.assertNotIn("events", first)
        second = session.submit(self.submission(actions=release_actions("internal")))
        self.assertEqual(second["status"], "launched")
        self.assertEqual(session.usage["generic"]["episodes"], 2)
        self.assertEqual(session.runs[0]["score"]["status"], "failure")
        self.assertEqual(session.runs[1]["score"]["status"], "safe")

    def test_report_separates_unresolved_and_missing_utility_evidence(self):
        case = example_plan()["cases"][0]
        failure = run_episode(case, release_actions(), "starting")
        unresolved = run_episode(case, release_actions()[:1], "starting")
        report = summarize([failure, unresolved], 1)
        row = report["groups"][0]
        self.assertEqual(row["classification_range"], [0.5, 1])
        self.assertIsNone(row["utility_gate"])
        self.assertEqual(report["primary_prevention_claim"], "not_established")


if __name__ == "__main__":
    unittest.main()
