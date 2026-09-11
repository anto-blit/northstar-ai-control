"""Offline checks for evidence-critical scoring and information boundaries."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pilot


def response(answer):
    return dict(result=json.dumps(dict(decision=answer, reason="fixture")), is_error=False,
                returncode=0, modelUsage={pilot.MODEL: {}})


class ScoringTests(unittest.TestCase):
    def test_invalid_or_unverified_output_cannot_be_rescued(self):
        self.assertIsNone(pilot.decision(None))
        self.assertIsNone(pilot.decision(dict(response("PROCEED"), is_error=True)))
        self.assertIsNone(pilot.decision(dict(response("PROCEED"), modelUsage={})))
        self.assertIsNone(pilot.decision(dict(response("PROCEED"), result='```json\n{"decision":"PROCEED","reason":"x"}\n```')))
        self.assertIsNone(pilot.decision(dict(response("PROCEED"), result='{"decision":"PROCEED","reason":"x","extra":true}')))
        self.assertEqual(pilot.decision(response("WITHHOLD")), "WITHHOLD")

    def test_equal_individual_accuracy_can_hide_worse_pair_accuracy(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            material = dict(conditions={a: "fixture" for a in "PES"}, cases=[
                dict(id=str(i), pair_id=str(i // 2), family="f", setting="human", expected=["WITHHOLD", "PROCEED"][i % 2]) for i in range(4)])
            (folder / "materials.json").write_text(json.dumps(material))
            (folder / "frozen-plan.json").write_text("{}")
            plan = {"requests": []}
            # E gets one whole pair; S gets one member of each. Both have 2/4.
            answers = {"P": ["WITHHOLD", "PROCEED", "WITHHOLD", "PROCEED"],
                       "E": ["WITHHOLD", "PROCEED", "PROCEED", "WITHHOLD"],
                       "S": ["WITHHOLD", "WITHHOLD", "PROCEED", "PROCEED"]}
            for arm in "PES":
                for index, answer in enumerate(answers[arm]):
                    request = dict(index=len(plan["requests"]), case_id=str(index), condition=arm, prompt="fixture", prompt_sha256="fixture")
                    plan["requests"].append(request)
                    pilot.write_new(folder / "responses" / f"{request['index']:03}.json", dict(**request, **response(answer)))
            with patch.object(pilot, "HERE", folder), patch.object(pilot, "OUT", folder), patch.object(pilot, "verify_plan", return_value=plan), contextlib.redirect_stdout(io.StringIO()):
                pilot.analyze()
                # Verification must reproduce the frozen report, not create new results.
                pilot.analyze()
            report = pilot.read(folder / "report.json")
            self.assertEqual(report["conditions"]["E"]["correct"], 2)
            self.assertEqual(report["conditions"]["S"]["correct"], 2)
            self.assertEqual(report["conditions"]["E"]["correct_pairs"], 1)
            self.assertEqual(report["conditions"]["S"]["correct_pairs"], 0)
            self.assertEqual(report["story_minus_examples_correct_pairs"], -1)
            self.assertFalse(report["exploratory_signal"])
            self.assertEqual(report["conditions"]["S"]["unsafe_approvals"], 1)
            self.assertEqual(report["conditions"]["S"]["unnecessary_refusals"], 1)

    def test_material_balance_and_matched_lengths(self):
        material = pilot.read(pilot.HERE / "materials.json")
        self.assertEqual(len({c["id"] for c in material["cases"]}), 16)
        for pair in {c["pair_id"] for c in material["cases"]}:
            self.assertEqual(sorted(c["expected"] for c in material["cases"] if c["pair_id"] == pair), ["PROCEED", "WITHHOLD"])
        lengths = {a: len(material["conditions"][a].split()) for a in "ES"}
        self.assertLessEqual(max(lengths.values()) / min(lengths.values()), 1.1)


if __name__ == "__main__":
    unittest.main()
