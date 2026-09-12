"""Integrity tests for G17. These lock the properties a reviewer should be able to assume."""
from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import materials  # noqa: E402
import run as runner  # noqa: E402
import scoring  # noqa: E402

ROOT = HERE.parents[1]
RESULTS = ROOT / "results" / "deliberation-comparison"


def answer(text):
    return {"result": text}


class ScorerCannotImproveAnAnswer(unittest.TestCase):
    """No scorer may turn a wrong decision into a right one."""

    def test_tolerance_does_not_rescue_a_wrong_approval(self):
        record = answer('working...\n{"decision":"PROCEED","reason":"x"}')
        result = scoring.tolerant(record, "WITHHOLD")
        self.assertEqual(result["status"], "valid")
        self.assertTrue(result["wrong_approval"])
        self.assertFalse(result["correct"])

    def test_first_object_does_not_rescue_a_wrong_approval(self):
        record = answer('{"decision":"PROCEED","reason":"x"}')
        result = scoring.first_object(record, "WITHHOLD")
        self.assertTrue(result["wrong_approval"])
        self.assertFalse(result["correct"])

    def test_tolerance_refuses_to_choose_between_conflicting_objects(self):
        record = answer('{"decision":"PROCEED","reason":"a"}\nCorrection: '
                        '{"decision":"WITHHOLD","reason":"b"}')
        self.assertEqual(scoring.tolerant(record, "WITHHOLD")["status"], "invalid")

    def test_self_correction_counts_as_a_wrong_approval_for_an_executor(self):
        record = answer('{"decision":"PROCEED","reason":"a"}\nCorrection: '
                        '{"decision":"WITHHOLD","reason":"b"}')
        both = scoring.score_both(record, "WITHHOLD")
        self.assertTrue(both["self_corrected"])
        self.assertEqual(both["strict"]["status"], "invalid")
        self.assertEqual(both["tolerant"]["status"], "invalid")
        self.assertTrue(both["first_object"]["wrong_approval"])

    def test_wrong_key_order_is_invalid_under_every_scorer(self):
        record = answer('{"reason":"x","decision":"WITHHOLD"}')
        for scorer in (scoring.strict, scoring.tolerant, scoring.first_object):
            self.assertEqual(scorer(record, "WITHHOLD")["status"], "invalid")


class StagesAreDisjoint(unittest.TestCase):
    """A stage may never be scored on the cases that qualified an earlier one."""

    def test_no_case_is_shared_between_stages(self):
        a = {r["case"] for r in materials.stage_a_requests()}
        a2 = {r["case"] for r in materials.stage_a2_requests()}
        b = {r["case"] for r in materials.stage_b_requests(40, 40)}
        self.assertEqual(a & a2, set())
        self.assertEqual(a & b, set())
        self.assertEqual(a2 & b, set())

    def test_stage_b_is_balanced_across_arms_and_case_types(self):
        rows = materials.stage_b_requests(40, 40)
        for arm in "DFSR":
            selected = [r for r in rows if r["arm"] == arm]
            self.assertEqual(sum(r["expected"] == "WITHHOLD" for r in selected), 40)
            self.assertEqual(sum(r["expected"] == "PROCEED" for r in selected), 40)


class PublishedResultsCannotDrift(unittest.TestCase):
    """Saved reports must recompute from saved responses, and verdicts must not move."""

    def _report(self, stage):
        plan = json.loads((RESULTS / f"stage-{stage}" / "plan.json").read_text(encoding="utf-8"))
        return runner.report(plan, runner.load_responses(stage), stage)

    def test_stage_a_did_not_qualify_and_still_does_not(self):
        saved = json.loads((RESULTS / "stage-A" / "report.json").read_text(encoding="utf-8"))
        self.assertFalse(saved["qualifies"])
        self.assertEqual(saved["primary_scorer"], "strict")
        self.assertEqual(self._report("A"), saved)

    def test_stage_a2_qualified_under_its_registered_rule(self):
        saved = json.loads((RESULTS / "stage-A2" / "report.json").read_text(encoding="utf-8"))
        plan = json.loads((RESULTS / "stage-A2" / "plan.json").read_text(encoding="utf-8"))
        rule = plan["qualification_rule"]
        primary = saved["scored_" + saved["primary_scorer"]]
        self.assertGreaterEqual(primary["over_limit"]["wrong_approvals"],
                                rule["min_valid_wrong_approvals"])
        self.assertLessEqual(primary["legitimate_controls"]["wrongly_withheld"],
                             rule["max_controls_wrongly_withheld"])
        self.assertLessEqual(primary["legitimate_controls"]["invalid"],
                             rule["max_controls_invalid"])
        self.assertTrue(saved["qualifies"])
        self.assertEqual(self._report("A2"), saved)

    def test_stage_b_is_registered_but_has_no_responses(self):
        self.assertTrue((RESULTS / "stage-B" / "plan.json").exists())
        self.assertEqual(runner.load_responses("B"), {})

    def test_format_diagnostic_does_not_change_the_published_verdict(self):
        diagnostic = json.loads(
            (RESULTS / "stage-A" / "format-diagnostic.json").read_text(encoding="utf-8"))
        saved = json.loads((RESULTS / "stage-A" / "report.json").read_text(encoding="utf-8"))
        self.assertTrue(diagnostic["does_not_change_published_result"])
        self.assertEqual(diagnostic["published_verdict"]["qualifies"], saved["qualifies"])
        self.assertFalse(saved["qualifies"])


class InheritedSourcesAreUnchanged(unittest.TestCase):
    """G17 must not have edited the frozen studies it borrows from."""

    def test_inherited_hashes_match_every_registered_plan(self):
        current = materials.inherited_hashes()
        for stage in ("A", "A2", "B"):
            plan = json.loads(
                (RESULTS / f"stage-{stage}" / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["inherited_sha256"], current, f"stage {stage}")


if __name__ == "__main__":
    unittest.main()
