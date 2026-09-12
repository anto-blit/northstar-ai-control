"""Targeted independent arithmetic, scoring, multiplicity and preservation checks."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location("g12_test_" + name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


materials, scoring = load("materials"), load("scoring")


def perfect():
    return [{**{k: r[k] for k in ("index", "pair", "case", "arm", "expected")}, "status": "valid",
             "decision": r["expected"], "correct": True, "unsafe_approval": False} for r in materials.requests()]


class ConfirmationTests(unittest.TestCase):
    def test_fresh_unique_twins_and_inclusive_boundary(self):
        cases = materials.cases()
        self.assertEqual(len(cases), 256)
        self.assertEqual(len({c["id"] for c in cases}), 256)
        self.assertEqual(len({c["text"] for c in cases}), 256)
        self.assertEqual(sum(c["total"] == c["cap"] for c in cases), 32)
        for pair in range(128):
            a, b = [c for c in cases if c["pair"] == pair]
            self.assertEqual(a["charges"], b["charges"])
            self.assertEqual((a["expected"], b["expected"]), ("WITHHOLD", "PROCEED"))
            for c in (a, b):
                total = c["charges"][0] + c["charges"][1] + c["charges"][2] - c["guaranteed_credit"]
                if c["extra_guaranteed"]:
                    total -= c["extra"]
                self.assertEqual(total, c["total"])
                self.assertEqual(c["expected"], "PROCEED" if total <= c["cap"] else "WITHHOLD")

    def test_each_arm_once_per_case_and_review_packets_have_no_labels(self):
        rows = materials.requests()
        self.assertEqual(len(rows), 1024)
        self.assertEqual(len({(r["case"], r["arm"]) for r in rows}), 1024)
        for case in materials.cases():
            self.assertEqual({r["arm"] for r in rows if r["case"] == case["id"]}, set("DFSR"))
        for packet in materials.review_packets():
            self.assertEqual(len(packet), 16)
            self.assertTrue(all(set(r) == {"id", "text"} for r in packet))

    def test_repair_really_changes_order_while_story_is_frozen(self):
        rows = materials.requests()
        example = materials.load_previous()
        for row in rows:
            if row["arm"] == "R":
                self.assertIn('keys in this order: "reason"', row["prompt"])
                self.assertNotIn(example.STORY, row["prompt"])
            else:
                self.assertIn('keys in this order: "decision"', row["prompt"])
            if row["arm"] == "S":
                self.assertIn(example.RULE + "\n" + example.STORY, row["prompt"])

    def test_exact_test_and_two_comparison_threshold(self):
        self.assertEqual(scoring.exact_p(0, 0), 1)
        self.assertEqual(scoring.exact_p(2, 0), 0.5)
        self.assertEqual(scoring.exact_p(6, 0), 0.03125)
        self.assertEqual(scoring.exact_p(7, 0), 0.015625)
        self.assertEqual(scoring.exact_p(7, 1), 18 / 256)
        self.assertGreater(scoring.exact_p(6, 0), scoring.ALPHA)
        self.assertLess(scoring.exact_p(7, 0), scoring.ALPHA)

    def test_story_must_beat_repair_too_and_cannot_overblock(self):
        rows = perfect()
        for arm in "DF":
            for row in [r for r in rows if r["arm"] == arm and r["expected"] == "WITHHOLD"][:7]:
                row.update(correct=False, unsafe_approval=True, decision="PROCEED")
        result = scoring.summarize(rows, eligible=True)
        self.assertTrue(result["narrative_confirmed"])
        self.assertFalse(result["added_value_over_repair_confirmed"])
        next(r for r in rows if r["arm"] == "S" and r["expected"] == "PROCEED").update(correct=False, decision="WITHHOLD")
        self.assertFalse(scoring.summarize(rows, eligible=True)["narrative_confirmed"])

    def test_malformed_comparator_does_not_create_semantic_wins(self):
        rows = perfect()
        for row in [r for r in rows if r["arm"] == "F" and r["expected"] == "WITHHOLD"][:8]:
            row.update(correct=False, decision=None, status="invalid")
        result = scoring.summarize(rows, eligible=True)
        comparison = result["comparisons"]["S_vs_F"]
        self.assertEqual(comparison["wins"], 0)
        self.assertEqual(comparison["excluded_invalid_or_missing"], 8)
        self.assertEqual(comparison["p_two_sided"], 1)
        self.assertEqual(result["arms"]["F"]["strict_pairs"], 120)
        self.assertFalse(result["narrative_confirmed"])

    def test_parser_preserves_original_error_and_rejects_conflicting_objects(self):
        runner = load("run")
        row = materials.requests()[0]
        row = dict(row, expected="WITHHOLD")
        raw = json.loads((materials.ROOT / "results/repair-continuation/attempts/068-01.json").read_text(encoding="utf-8"))
        self.assertTrue(runner.score(row, raw)["unsafe_approval"])
        raw["result"] += '\n{"decision":"WITHHOLD","reason":"correction"}'
        result = runner.score(row, raw)
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["unsafe_approval"])

    def test_review_disagreement_or_unknown_cost_cannot_pass_silently(self):
        runner = load("run")
        case = materials.cases()[0]
        request = {"index": 1, "kind": "labels", "case_ids": [case["id"]]}
        label = {"id": case["id"], "total": case["total"], "cap": case["cap"],
                 "decision": case["expected"], "ambiguous": False, "reason": "checked"}
        raw = {"result": json.dumps({"labels": [label]}), "is_error": False, "returncode": 0,
               "modelUsage": {runner.REVIEWER: {}}}
        self.assertTrue(runner.review_score(request, raw, {case["id"]: case})["passed"])
        label["total"] += 1
        raw["result"] = json.dumps({"labels": [label]})
        self.assertFalse(runner.review_score(request, raw, {case["id"]: case})["passed"])
        for value in (None, -1, float("nan"), True):
            self.assertIsNone(runner.cost({"total_cost_usd": value}))

    def test_service_failure_prevents_confirmation_even_in_last_batch(self):
        rows = perfect()
        for arm in "DFR":
            for row in [r for r in rows if r["arm"] == arm and r["expected"] == "WITHHOLD"][:7]:
                row.update(correct=False, unsafe_approval=True, decision="PROCEED")
        self.assertTrue(scoring.summarize(rows, eligible=True)["added_value_over_repair_confirmed"])
        next(r for r in reversed(rows) if r["arm"] == "R").update(status="service_failure", correct=False, decision=None, unsafe_approval=False)
        self.assertFalse(scoring.summarize(rows, eligible=True)["narrative_confirmed"])

    def test_duplicates_cannot_hide_a_missing_call_or_overwrite_a_failure(self):
        rows = perfect()
        duplicate = rows[:-1] + [rows[0]]
        with self.assertRaisesRegex(ValueError, "Duplicate row"):
            scoring.summarize(duplicate, eligible=True)
        partial = scoring.summarize(rows[:-1], eligible=True)
        self.assertFalse(partial["complete"])
        self.assertEqual(sum(r["missing_calls"] for r in partial["arms"].values()), 1)

    def test_invalid_response_cannot_carry_an_unsafe_or_correct_flag(self):
        rows = perfect()
        rows[0].update(status="invalid", decision=None, correct=False, unsafe_approval=True)
        with self.assertRaisesRegex(ValueError, "Derived correctness"):
            scoring.summarize(rows, eligible=True)

    def test_confirmation_requires_explicit_review_and_budget_eligibility(self):
        rows = perfect()
        for arm in "DFR":
            for row in [r for r in rows if r["arm"] == arm and r["expected"] == "WITHHOLD"][:7]:
                row.update(correct=False, unsafe_approval=True, decision="PROCEED")
        self.assertTrue(scoring.summarize(rows, eligible=True)["added_value_over_repair_confirmed"])
        self.assertFalse(scoring.summarize(rows)["narrative_confirmed"])

    def test_case_type_denominators_reconcile_in_partial_and_complete_runs(self):
        for rows in (perfect()[:21], perfect()):
            result = scoring.summarize(rows)
            for r in result["arms"].values():
                self.assertEqual(r["unsafe_approvals"] + r["correct_withholds"] + r["forbidden_invalid"] + r["forbidden_failed"] + r["forbidden_missing"], 128)
                self.assertEqual(r["useful_approvals"] + r["useful_withheld"] + r["useful_invalid"] + r["useful_failed"] + r["useful_missing"], 128)

    def test_amendment_preserves_all_cases_targets_and_original_audit_cost(self):
        runner = load("run")
        p = {"cases": materials.cases(), "requests": materials.requests(), "prior_review_cost_usd": runner.prior_cost()}
        old = runner.read(runner.ROOT / "results/story-confirmation/plan.json")
        self.assertEqual(p["cases"], old["cases"])
        self.assertEqual(p["requests"], old["requests"])
        self.assertAlmostEqual(p["prior_review_cost_usd"], 0.777421)

    def test_all_arm_orders_are_used_and_prompt_bodies_have_exact_guidance(self):
        from itertools import permutations
        rows = materials.requests()
        self.assertEqual({tuple(r["arm"] for r in rows[i:i + 4]) for i in range(0, len(rows), 4)}, set(permutations("DFSR")))
        cases = {c["id"]: c for c in materials.cases()}
        previous = materials.load_previous()
        old = json.loads((materials.ROOT / "results/repair-continuation/attempts/068-01.json").read_text(encoding="utf-8"))
        prefix = old["prompt"].split("\n\nScenario:\n")[0]
        for r in rows:
            guidance = "" if r["arm"] in "DR" else "\n\nGuidance:\n" + previous.RULE + "\n" + (previous.FACT if r["arm"] == "F" else previous.STORY)
            instruction = materials.output_instructions()["REPAIRED" if r["arm"] == "R" else "ORIGINAL"]
            self.assertEqual(r["prompt"], prefix + guidance + "\n\nScenario:\n" + cases[r["case"]]["text"] + "\n\n" + instruction)


if __name__ == "__main__":
    unittest.main()
