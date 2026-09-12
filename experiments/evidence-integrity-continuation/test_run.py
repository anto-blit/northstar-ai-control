"""Check the precise amendment and replay through the unchanged world/oracle."""
import importlib.util
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

spec = importlib.util.spec_from_file_location("g8c_tests", Path(__file__).with_name("run.py"))
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


class AmendmentTests(unittest.TestCase):
    def test_metadata_does_not_execute_or_count_as_final_report(self):
        case = run.base.corpus.cases()[0]
        w = run.base.world.World(case)
        self.addCleanup(w.close)
        a = run.base.good_action(case)
        a.update(released=["invented"], held=["invented"])
        parsed = run.parse({"structured_output": a})
        self.assertEqual(parsed["released"], [])
        w.execute(parsed)
        self.assertIsNone(w.report)
        self.assertNotIn(["invented"], w.snapshot()["releases"])
        self.assertFalse(w.evidence("exhausted")["score"]["accurate_report"])

    def test_finish_and_action_shape_remain_strict(self):
        for a in (dict(run.base.action("finish"), statements=["SELECT 1"]),
                  dict(run.base.action("sql", statements=["SELECT 1"]), held=4),
                  dict(run.base.action("sql", statements=["SELECT 1"]), extra="unexpected")):
            self.assertIsNone(run.parse({"structured_output": a}))

    def test_original_failed_canary_is_unchanged_and_only_reinterpretable_posthoc(self):
        path = run.ROOT / "results/evidence-integrity/episodes/000/response-0.json"
        response = run.base.read(path)
        self.assertIsNone(run.original_parse(response))
        self.assertIsNotNone(run.parse(response))
        outcome = run.base.read(path.with_name("outcome.json"))
        self.assertEqual(outcome["termination"], "invalid")
        self.assertEqual(outcome["snapshot"]["releases"], [])

    def test_fresh_registration_and_full_replay(self):
        parent = run.ROOT / "study-runs/evidence-integrity-continuation/tests"
        parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=parent) as directory:
            root = Path(directory)
            for path in run.sources():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(run.ROOT / path, target)
            plan = run.register(root)
            row = plan["episodes"][0]
            out = root / run.REL / "episodes/000"
            run.base.dump(out / "attempt.json", {"row": row})
            w = run.base.world.World(run.base.case_for(row))
            self.addCleanup(w.close)
            ready, held = run.base.world.expected(w.case)
            sql = run.base.good_action(w.case)
            sql.update(released=ready, held=held)
            for i, a in enumerate((sql, run.base.action("finish", released=ready, held=held))):
                prompt = run.base.prompt(row, w)
                r = {"structured_output": a, "is_error": False, "returncode": 0,
                     "modelUsage": {run.base.transport.MODEL: {}}, "total_cost_usd": .01,
                     "requested_model": run.base.transport.MODEL, "prompt": prompt,
                     "prompt_sha256": run.base.digest(prompt.encode())}
                run.base.dump(out / f"response-{i}.json", r)
                w.execute(run.parse(r))
            run.base.dump(out / "outcome.json", w.evidence("finished"))
            self.assertTrue(run.base.replay(row, root)[0]["score"]["success"])
            report = run.base.report(root)
            self.assertEqual((report["finished"], report["planned"], report["application_calls"]), (1, 26, 2))
            r = run.base.read(out / "response-1.json")
            r["structured_output"]["released"] = []
            (out / "response-1.json").write_text(json.dumps(r), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "do not replay"):
                run.base.replay(row, root)


if __name__ == "__main__":
    unittest.main()
