"""Offline accounting, preservation and stop-rule tests; no provider calls."""
import importlib.util
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

spec = importlib.util.spec_from_file_location("g5c_test_run", Path(__file__).with_name("run.py"))
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


def answer(action):
    return dict(result=json.dumps({"reason": "Fixture", "action": action}), is_error=False,
                returncode=0, modelUsage={"fixture": {}}, total_cost_usd=0.01)


def refusal():
    return dict(result="API Error: Sonnet 5 can't help with this. Start a new session to continue.\n"
                "https://www.anthropic.com/legal/aup\nDetails: `[bio]`", is_error=True,
                returncode=1, modelUsage={"fixture": {}}, total_cost_usd=0.01)


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in ("curriculum", "northstar_ethics", "experiments/story-distillation",
                         "experiments/story-continuation", "results/story-distillation"):
            shutil.copytree(run.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))
        transport = "experiments/guidance-pilot/model_io.py"
        (self.root / transport).parent.mkdir(parents=True)
        shutil.copy2(run.ROOT / transport, self.root / transport)
        run.register(self.root)
        self.g5 = run.original(self.root)
        self.rows = self.g5.checked_plan(self.root)["episodes"]
        self.out = self.root / run.REL

    def execute(self, index, results):
        sequence = iter(results)
        def fake_call(prompt):
            record = next(sequence)
            return dict(record, prompt=prompt, prompt_sha256=run.sha256(prompt.encode()).hexdigest(),
                        requested_model=self.g5.MODEL, system_sha256=run.sha256(self.g5.SYSTEM.encode()).hexdigest())
        return run.run_episode(self.rows[index], self.g5, self.out, fake_call)

    def test_inherited_refusal_is_terminal_and_not_a_behavioral_loss(self):
        report = run.verify(self.root)
        self.assertEqual(report["summary"]["D"]["provider_refusal"], 1)
        self.assertEqual(report["summary"]["D"]["correct"], 1)
        self.assertEqual(report["summary"]["D"]["planned"], 12)
        self.assertEqual(report["comparisons"]["S_vs_D"]["wins"], 0)
        self.assertEqual(report["comparisons"]["S_vs_D"]["ties"], 1)
        self.assertEqual(len(report["comparisons"]["S_vs_D"]["excluded"]), 11)
        self.assertFalse(report["all_adjudicated"])

    def test_new_refusal_ends_episode_but_allows_next_independent_case(self):
        records = self.execute(6, [refusal()])
        self.assertEqual(len(records), 1)
        self.assertFalse(run.should_stop(records, .01))
        self.execute(7, [answer("inspect"), answer("failure")])
        report = run.verify(self.root)
        self.assertEqual(report["observations"][6]["status"], "provider_refusal")
        self.assertTrue(report["observations"][7]["correct"])
        self.assertEqual(report["observations"][6]["effects"], [])

    def test_refusal_and_any_started_episode_cannot_be_retried(self):
        self.execute(6, [refusal()])
        before = (self.out / "episodes/006/response-0.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.execute(6, [answer("inspect"), answer("failure")])
        self.assertEqual((self.out / "episodes/006/response-0.json").read_bytes(), before)
        with self.assertRaisesRegex(ValueError, "retained"):
            self.execute(5, [answer("inspect")])

    def test_quota_auth_timeout_unknown_errors_and_unknown_cost_stop(self):
        for record in (dict(refusal(), result="API Error: quota exceeded"),
                       dict(refusal(), result="authentication failed"),
                       dict(refusal(), returncode=None, error="timeout"),
                       dict(refusal(), result="Unclassified API Error"),
                       dict(refusal(), total_cost_usd=None),
                       dict(answer("inspect"), total_cost_usd=float("nan")),
                       dict(answer("inspect"), total_cost_usd=-1)):
            self.assertTrue(run.should_stop([record], .01))
        self.assertTrue(run.should_stop([answer("inspect")], 5))
        self.assertFalse(run.should_stop([answer("inspect")], 4.99))

    def test_quoted_refusal_in_an_operational_answer_is_not_provider_error(self):
        record = dict(answer("inspect"), result=refusal()["result"])
        self.assertFalse(run.provider_refusal(record))
        self.execute(6, [record])
        self.assertEqual(run.verify(self.root)["observations"][6]["status"], "invalid")

    def test_wrong_and_unsafe_choices_remain_model_failures(self):
        self.execute(6, [answer("inspect"), answer("green")])
        report = run.verify(self.root)
        row = report["observations"][6]
        self.assertEqual(row["status"], "valid_decision")
        self.assertFalse(row["correct"])
        self.assertTrue(row["unsafe_proposal"])
        self.assertEqual(row["effects"], [])

    def test_finished_inventory_does_not_erase_refusal_or_claim_all_answered(self):
        for row in self.rows[6:]:
            case = next(c for c in self.g5.cases() if c["id"] == row["case"])
            self.execute(row["index"], [answer("inspect"), answer(case["expected"])])
        report = run.verify(self.root)
        self.assertTrue(report["all_adjudicated"])
        self.assertFalse(report["all_answered"])
        self.assertFalse(report["all_valid_decisions"])
        self.assertEqual([report["summary"][a]["correct"] for a in "DFS"], [11, 12, 12])
        self.assertEqual(report["comparisons"]["S_vs_D"]["ties"], 11)
        self.assertEqual(report["comparisons"]["S_vs_D"]["wins"], 0)
        self.assertEqual(report["comparisons"]["S_vs_F"]["ties"], 12)

    def test_source_and_original_evidence_are_frozen(self):
        path = self.root / "results/story-distillation/episodes/005/response-1.json"
        path.write_text(json.dumps(answer("full")), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Frozen continuation input changed"):
            run.verify(self.root)

    def test_report_and_effect_tampering_are_rejected(self):
        self.execute(6, [answer("inspect"), answer("failure")])
        report = run.verify(self.root)
        run.dump(self.out / "report.json", report)
        self.assertEqual(run.verify(self.root), report)
        path = self.out / "episodes/006/ledger.json"
        ledger = run.read(path)
        ledger["effects"] = []
        path.write_text(json.dumps(ledger), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Local effects"):
            run.verify(self.root)

    def test_unexpected_episode_or_attempt_cannot_be_hidden(self):
        folder = self.out / "episodes/005"
        folder.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "Unexpected continuation episode"):
            run.verify(self.root)

    def test_incomplete_attempt_reservation_cannot_look_unstarted(self):
        (self.out / "episodes/006").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            run.verify(self.root)


if __name__ == "__main__":
    unittest.main()
