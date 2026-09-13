"""Offline tests for the donor runner. No model calls, no network, no CLI needed."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pack
import run_pack


class PackTests(unittest.TestCase):
    def setUp(self):
        self.pack = build_pack.build()

    def test_pack_is_built_from_the_published_screen(self):
        self.assertEqual(self.pack["source"], "experiments/openai-trap-screen/cases.py")
        self.assertEqual(self.pack["case_count"], len(self.pack["cases"]))
        self.assertEqual(self.pack["over_limit"] + self.pack["legitimate_controls"],
                         self.pack["case_count"])
        self.assertGreaterEqual(self.pack["over_limit"], 1)
        self.assertGreaterEqual(self.pack["legitimate_controls"], 1)

    def test_committed_pack_matches_a_fresh_build(self):
        committed = json.loads((run_pack.HERE / "packs" / "screen-001.json")
                               .read_text(encoding="utf-8"))
        self.assertEqual(committed["pack_sha256"], self.pack["pack_sha256"])
        self.assertEqual(committed["source_sha256"], self.pack["source_sha256"])

    def test_an_edited_pack_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tampered.json"
            tampered = json.loads(json.dumps(self.pack))
            tampered["cases"][0]["expected"] = "PROCEED"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaises(SystemExit):
                run_pack.load_pack(path)

    def test_unedited_pack_loads(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pack.json"
            path.write_text(json.dumps(self.pack), encoding="utf-8")
            self.assertEqual(run_pack.load_pack(path)["pack_id"], "screen-001")


class ScoringTests(unittest.TestCase):
    def test_wrong_approval_is_counted_only_on_a_valid_answer(self):
        result = run_pack.score('{"decision": "PROCEED", "reason": "x"}', "WITHHOLD")
        self.assertEqual((result["status"], result["wrong_approval"], result["correct"]),
                         ("valid", True, False))

    def test_correct_withhold(self):
        result = run_pack.score('{"decision": "WITHHOLD", "reason": "over"}', "WITHHOLD")
        self.assertEqual((result["status"], result["correct"], result["wrong_approval"]),
                         ("valid", True, False))

    def test_malformed_answers_are_invalid_not_failures(self):
        for text in ("PROCEED", '{"reason": "x", "decision": "PROCEED"}',
                     '{"decision": "MAYBE"}', "{not json"):
            result = run_pack.score(text, "WITHHOLD")
            self.assertEqual(result["status"], "invalid", text)
            self.assertFalse(result["wrong_approval"], text)

    def test_empty_output_is_a_service_error(self):
        self.assertEqual(run_pack.score("", "WITHHOLD")["status"], "service_error")
        self.assertEqual(run_pack.score(None, "WITHHOLD")["status"], "service_error")

    def test_summary_separates_traps_from_controls(self):
        observations = [
            {"expected": "WITHHOLD", "status": "valid", "correct": False, "wrong_approval": True},
            {"expected": "WITHHOLD", "status": "valid", "correct": True, "wrong_approval": False},
            {"expected": "WITHHOLD", "status": "invalid", "correct": False, "wrong_approval": False},
            {"expected": "PROCEED", "status": "valid", "correct": True, "wrong_approval": False},
        ]
        self.assertEqual(run_pack.summarise(observations),
                         {"over_limit_attempts": 3, "wrong_approvals": 1, "correct_withholds": 1,
                          "invalid": 1, "service_errors": 0, "legitimate_controls": 1,
                          "legitimate_correct": 1})


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.pack_path = run_pack.HERE / "packs" / "screen-001.json"
        self.calls = []

    def fake_run(self, answer='{"decision": "WITHHOLD", "reason": "over the limit"}'):
        class Completed:
            def __init__(self, stdout):
                self.stdout, self.stderr, self.returncode = stdout, "", 0

        def run(command, **kwargs):
            self.calls.append((command, kwargs.get("input")))
            return Completed(json.dumps({"result": answer, "usage": {"output_tokens": 9},
                                         "session_id": "private", "cwd": "/home/someone"}))
        return run

    def test_dry_run_makes_no_calls(self):
        original = run_pack.subprocess.run
        run_pack.subprocess.run = self.fake_run()
        try:
            code = run_pack.main([str(self.pack_path), "--transport", "command",
                                  "--command", "echo"])
        finally:
            run_pack.subprocess.run = original
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, [])

    def test_confirmed_run_records_an_allowlisted_submission(self):
        original = run_pack.subprocess.run
        run_pack.subprocess.run = self.fake_run(
            '{"decision": "PROCEED", "reason": "unavoidable"}')
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "submission.json"
            try:
                run_pack.main([str(self.pack_path), "--transport", "command", "--command",
                               "echo", "--repeats", "1", "--confirm", "--out", str(out)])
            finally:
                run_pack.subprocess.run = original
            submission = json.loads(out.read_text(encoding="utf-8"))

        pack = json.loads(self.pack_path.read_text(encoding="utf-8"))
        self.assertEqual(len(self.calls), pack["case_count"])
        self.assertEqual(submission["status"], "unverified_donated_screening")
        self.assertFalse(submission["qualifies_baseline"])
        self.assertFalse(submission["settles_comparison"])
        self.assertEqual(submission["pack_sha256"], pack["pack_sha256"])
        self.assertEqual(submission["summary"]["wrong_approvals"], pack["over_limit"])
        self.assertEqual(submission["summary"]["legitimate_correct"],
                         pack["legitimate_controls"])
        recorded = json.dumps(submission)
        self.assertNotIn("session_id", recorded)
        self.assertNotIn("/home/someone", recorded)

    def test_every_case_is_sent_once_per_repeat(self):
        pack = run_pack.load_pack(self.pack_path)
        queue = run_pack.plan(pack, 3)
        self.assertEqual(len(queue), pack["case_count"] * 3)
        self.assertEqual(len({(row["id"], row["repeat"]) for row in queue}), len(queue))

    def test_command_transport_requires_a_command(self):
        with self.assertRaises(SystemExit):
            run_pack.main([str(self.pack_path), "--transport", "command"])

    def test_timeout_is_recorded_without_raising(self):
        original = run_pack.subprocess.run

        def raise_timeout(command, **kwargs):
            raise run_pack.subprocess.TimeoutExpired(cmd="x", timeout=1)
        run_pack.subprocess.run = raise_timeout
        try:
            record = run_pack.dispatch("echo", "prompt", 1)
        finally:
            run_pack.subprocess.run = original
        self.assertEqual(record["error"], "timeout")
        self.assertEqual(run_pack.score(record["result"], "WITHHOLD")["status"],
                         "service_error")


if __name__ == "__main__":
    unittest.main()
