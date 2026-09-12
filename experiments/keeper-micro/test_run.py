"""Guard against attributing a ceiling, parser error or interrupted run to a story."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("keeper_run", Path(__file__).with_name("run.py"))
run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run)


def correct_rows():
    return [{**{k: r[k] for k in ("index", "block", "case", "arm", "expected")},
             "status": "valid", "decision": r["expected"]} for r in run.requests()]


def change(rows, arm, block, decision="PROCEED", status="valid"):
    row = next(r for r in rows if r["arm"] == arm and r["block"] == block)
    row.update(decision=decision, status=status)


def raw_answer(text):
    return {"result": text, "operational": True, "returncode": 0, "errors": [],
            "tool_or_unexpected_item": False, "event_types": ["thread.started", "turn.started", "turn.completed"],
            "completed_item_types": ["agent_message"], "thread_id_sha256": "a" * 64,
            "usage": {"input_tokens": 100, "output_tokens": 20}}


class KeeperTests(unittest.TestCase):
    def test_exact_known_prompts_and_balanced_controls(self):
        rows = run.requests()
        self.assertEqual([r["index"] for r in rows], list(range(40)))
        for arm in run.ARMS:
            group = [r for r in rows if r["arm"] == arm]
            self.assertEqual(sum(r["case"] == 68 for r in group), 8)
            self.assertEqual(sum(r["case"] == 407 for r in group), 2)
        for r in rows:
            old = run.read(run.ROOT / f"results/repair-continuation/attempts/{r['case']:03}-01.json")
            self.assertEqual(r["system"], old["system"])
            if r["arm"] == "D":
                self.assertEqual(r["prompt"], old["prompt"])
            if r["arm"] in "FS":
                guidance = "\n\nGuidance:\n" + run.RULE + "\n" + (run.FACT if r["arm"] == "F" else run.STORY)
                self.assertEqual(r["prompt"].replace(guidance, "", 1), old["prompt"])
        self.assertNotEqual(rows[0]["prompt"], next(r["prompt"] for r in rows if r["arm"] == "R"))

    def test_actionable_error_not_rescued_by_reason(self):
        request = run.requests()[0]
        old = run.read(run.ROOT / "results/repair-continuation/attempts/068-01.json")
        scored = run.score(request, raw_answer(old["result"]))
        self.assertEqual(scored["decision"], "PROCEED")
        self.assertEqual(scored["status"], "valid")
        conflict = old["result"] + '\n{"decision":"WITHHOLD","reason":"correction"}'
        self.assertEqual(run.score(request, raw_answer(conflict))["status"], "invalid")

    def test_ceiling_and_single_error_do_not_earn_lead(self):
        rows = correct_rows()
        for count in (0, 1):
            if count:
                change(rows, "D", 0)
            report = run.summarize(rows)
            self.assertFalse(report["baseline_repeated"])
            self.assertFalse(report["candidate_vs_facts"])
            self.assertFalse(report["candidate_beyond_repair"])
            self.assertFalse(report["confirmation"])

    def test_story_must_beat_facts_and_preserve_useful_work(self):
        rows = correct_rows()
        change(rows, "D", 0)
        change(rows, "D", 1)
        self.assertTrue(run.summarize(rows)["baseline_repeated"])
        self.assertFalse(run.summarize(rows)["candidate_vs_facts"])
        change(rows, "F", 0)
        self.assertTrue(run.summarize(rows)["candidate_vs_facts"])
        self.assertFalse(run.summarize(rows)["candidate_beyond_repair"])
        change(rows, "R", 1)
        self.assertTrue(run.summarize(rows)["candidate_beyond_repair"])
        for arm in "SF":
            damaged = copy.deepcopy(rows)
            change(damaged, arm, 4, "WITHHOLD")
            self.assertFalse(run.summarize(damaged)["candidate_vs_facts"])
        change(rows, "S", 2, None, "invalid")
        self.assertFalse(run.summarize(rows)["candidate_vs_facts"])

    def test_invalid_comparator_is_not_semantic_win(self):
        rows = correct_rows()
        change(rows, "D", 0)
        change(rows, "D", 1)
        change(rows, "F", 0, None, "invalid")
        summary = run.summarize(rows)
        self.assertFalse(summary["candidate_vs_facts"])
        self.assertEqual(summary["comparisons"]["S_vs_F"], {"wins": 0, "losses": 0, "ties": 7, "excluded": 1})

    def test_missing_failed_and_duplicate_records_fail_closed(self):
        rows = correct_rows()
        change(rows, "D", 0)
        change(rows, "D", 1)
        change(rows, "F", 0)
        self.assertFalse(run.summarize(rows[:-1])["candidate_vs_facts"])
        change(rows, "R", 2, None, "service_failure")
        self.assertFalse(run.summarize(rows)["candidate_vs_facts"])
        with self.assertRaises(ValueError):
            run.summarize(rows + [rows[0]])

    def test_usage_and_no_tools_are_required(self):
        raw = raw_answer('{"decision":"WITHHOLD","reason":"over limit"}')
        self.assertTrue(run.operational(raw))
        for change_to in ({"usage": None}, {"usage": {"input_tokens": True, "output_tokens": 20}},
                          {"completed_item_types": ["agent_message", "command_execution"]},
                          {"event_types": ["thread.started", "turn.completed", "turn.completed"]}):
            self.assertFalse(run.operational({**raw, **change_to}))

    def test_transport_exception_is_preserved_without_retry(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(run, "OUT", Path(folder)), \
                patch.object(run.transport, "call", side_effect=RuntimeError("secret must not appear")) as call:
            raw = run.call(run.requests()[0])
            self.assertEqual(call.call_count, 1)
            self.assertIsNone(raw["usage"])
            self.assertFalse(run.operational(raw))
            self.assertNotIn("secret", json.dumps(raw))
            self.assertTrue((Path(folder) / "responses/000.json").exists())
            with self.assertRaises(FileExistsError):
                run.call(run.requests()[0])
            self.assertEqual(call.call_count, 1)


if __name__ == "__main__":
    unittest.main()
