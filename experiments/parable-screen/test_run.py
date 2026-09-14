"""Scientific and operational failure cases; all answers are synthetic."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import materials
import run as runner


class ParableScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = materials.build_plan()

    def folder(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return Path(temp.name) / "demo"

    def bound_records(self, answers):
        return {i: {**value, "kind": runner.KIND, "index": i,
                    "request_sha256": runner.digest(self.plan["requests"][i])}
                for i, value in answers.items()}

    def test_case_inventory_and_balanced_order(self):
        plan = materials.validate_plan(self.plan)
        self.assertEqual(plan["budget"]["maximum_calls"], 428)
        self.assertEqual(len(plan["arms"]), 8)
        self.assertEqual(plan["model_calls_authorized"], 0)
        baseline = {r["case"] for r in plan["requests"] if r["phase"] == "baseline"}
        screen = {r["case"] for r in plan["requests"] if r["phase"] == "screen"}
        self.assertFalse(baseline & screen)
        for arm in plan["arms"]:
            slots = [r["index"] % 8 for r in plan["requests"] if r["phase"] == "screen" and r["arm"] == arm]
            self.assertEqual([slots.count(i) for i in range(8)], [6] * 8)

    def test_swap_changes_only_that_story_packet(self):
        catalog = copy.deepcopy(self.plan["catalog"])
        catalog["candidates"][2]["story"] += " She returned the seal to its owner."
        catalog["candidates"][2]["version"] = "2"
        changed = materials.build_plan(catalog)
        differing = [old["arm"] for old, new in zip(self.plan["requests"], changed["requests"])
                     if old != new]
        self.assertEqual(differing, ["S:seal"] * 48)
        materials.validate_plan(changed)
        tampered = copy.deepcopy(self.plan)
        tampered["requests"][50]["prompt"] += " changed"
        with self.assertRaises(ValueError):
            materials.validate_plan(tampered)

    def test_other_family_and_live_plan_rejected(self):
        for key, value in (("live_registered", True), ("model_calls_authorized", 428)):
            changed = copy.deepcopy(self.plan)
            changed[key] = value
            with self.assertRaises(ValueError):
                materials.validate_plan(changed)
        catalog = copy.deepcopy(self.plan["catalog"])
        catalog["family"] = "withdrawn-consent"
        with self.assertRaises(ValueError):
            materials.build_plan(catalog)

    def test_full_sequence_replays_and_preserves_repair_contract(self):
        folder = self.folder()
        result = runner.execute(self.plan, folder, runner.fixtures(self.plan))
        self.assertEqual(runner.verify(folder), result)
        self.assertEqual(result["recorded"], 428)
        self.assertEqual(result["provider_calls"], 0)
        self.assertFalse(result["scientific_claims_enabled"])
        repair = result["views"]["strict"]["arms"]["R"]
        self.assertEqual(repair["over_limit"]["invalid"], 0)
        self.assertEqual(repair["over_limit"]["wrong_approvals"], 2)
        self.assertEqual(result["fixture_selection_check"]["hypothetical_nomination"], "keeper")
        with self.assertRaises(FileExistsError):
            runner.execute(self.plan, folder, runner.fixtures(self.plan))

    def test_zero_error_baseline_blocks_all_story_fixtures(self):
        folder = self.folder()
        result = runner.execute(self.plan, folder, runner.fixtures(self.plan, "all-correct"))
        self.assertEqual(result["recorded"], 44)
        self.assertEqual(result["missing"], 384)
        self.assertFalse(result["baseline_gate"]["passes"])
        self.assertIsNone(result["fixture_selection_check"]["hypothetical_nomination"])
        self.assertEqual(runner.verify(folder), result)

    def test_invalid_comparator_cannot_nominate_a_story(self):
        answers = runner.fixtures(self.plan)
        request = next(r for r in self.plan["requests"] if r["phase"] == "screen" and r["arm"] == "F:keeper")
        answers[request["index"]]["text"] = "not an answer"
        result = runner.report(self.plan, self.bound_records(answers))
        self.assertFalse(result["fixture_selection_check"]["evaluable"])
        self.assertIsNone(result["fixture_selection_check"]["hypothetical_nomination"])

    def test_blocking_legitimate_work_cannot_pass(self):
        answers = runner.fixtures(self.plan)
        for request in self.plan["requests"]:
            if request["arm"] == "S:keeper":
                answers[request["index"]]["text"] = '{"decision":"WITHHOLD","reason":"Blocked everything."}'
        result = runner.report(self.plan, self.bound_records(answers))
        self.assertEqual(result["views"]["first_object"]["arms"]["S:keeper"]["legitimate"]["wrongly_withheld"], 16)
        self.assertIsNone(result["fixture_selection_check"]["hypothetical_nomination"])

    def test_current_screen_baseline_must_still_fail(self):
        answers = runner.fixtures(self.plan)
        for request in self.plan["requests"]:
            if request["phase"] == "screen" and request["arm"] == "D":
                answers[request["index"]]["text"] = json.dumps({"decision": request["expected"], "reason": "Fixture"})
        result = runner.report(self.plan, self.bound_records(answers))
        self.assertFalse(result["fixture_selection_check"]["screen_baseline_sensitive"])
        self.assertIsNone(result["fixture_selection_check"]["hypothetical_nomination"])

    def test_equal_candidates_are_not_declared_a_winner(self):
        answers = runner.fixtures(self.plan)
        for request in self.plan["requests"]:
            if request["arm"] == "S:seal":
                answers[request["index"]]["text"] = json.dumps({"decision": request["expected"], "reason": "Fixture"})
        result = runner.report(self.plan, self.bound_records(answers))
        self.assertEqual(result["fixture_selection_check"]["tied_top_candidates"], ["keeper", "seal"])
        self.assertIsNone(result["fixture_selection_check"]["hypothetical_nomination"])

    def test_service_errors_and_unknown_metadata_stop_without_retry(self):
        changes = [{"status": "service_error", "usage": None, "cost_usd": None},
                   {"usage": None}, {"cost_usd": None}, {"target": {"provider": "live"}},
                   {"cost_usd": 0.11}]
        for change in changes:
            with self.subTest(change=change):
                answers = runner.fixtures(self.plan)
                answers[2].update(change)
                folder = self.folder()
                result = runner.execute(self.plan, folder, answers)
                self.assertEqual(result["recorded"], 3)
                self.assertEqual(runner.verify(folder), result)
                self.assertIsNone(result["fixture_selection_check"]["hypothetical_nomination"])

    def test_service_error_in_screen_preserves_partial_denominators(self):
        answers = runner.fixtures(self.plan)
        answers[50].update(status="service_error", text="", usage=None, cost_usd=None)
        folder = self.folder()
        result = runner.execute(self.plan, folder, answers)
        self.assertEqual(result["recorded"], 51)
        self.assertEqual(result["missing"], 377)
        self.assertEqual(runner.verify(folder), result)

    def test_budget_stops_before_another_reservation(self):
        answers = runner.fixtures(self.plan)
        for answer in answers.values():
            answer["cost_usd"] = 0.10
        folder = self.folder()
        result = runner.execute(self.plan, folder, answers)
        self.assertEqual(result["recorded"], 100)
        self.assertEqual(runner.read(folder / "completion.json")["reason"], "budget_limit")
        self.assertEqual(runner.verify(folder), result)

    def test_unanswered_reservation_recovers_but_never_resumes(self):
        folder = self.folder()
        folder.mkdir()
        (folder / "records").mkdir()
        (folder / "attempts").mkdir()
        runner.write_new(folder / "plan.json", self.plan)
        request = self.plan["requests"][0]
        runner.write_new(folder / "attempts/000.json", {
            "kind": runner.KIND, "index": 0, "request_sha256": runner.digest(request)})
        result = runner.recover(folder)
        self.assertEqual(result["recorded"], 0)
        self.assertEqual(result["missing"], 428)
        checkpoint = runner.read(next(folder.glob("recovery-*.json")))
        self.assertEqual(checkpoint["unresolved_attempts"], [0])
        self.assertFalse(checkpoint["automatic_resume_allowed"])

    def test_response_mutation_is_detected(self):
        folder = self.folder()
        runner.execute(self.plan, folder, runner.fixtures(self.plan, "all-correct"))
        path = folder / "records/000.json"
        path.write_text(path.read_text() + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            runner.verify(folder)


if __name__ == "__main__":
    unittest.main()
