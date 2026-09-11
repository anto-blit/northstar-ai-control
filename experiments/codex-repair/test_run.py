import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("g4_tests", Path(__file__).with_name("run.py"))
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


def stream(items, before=None):
    events = [{"type": "thread.started", "thread_id": "fresh"}]
    events += before or []
    events += [{"type": "turn.started"}]
    events += [{"type": "item.completed", "item": item} for item in items]
    events += [{"type": "turn.completed", "usage": {"input_tokens": 12, "output_tokens": 4}}]
    return "\n".join(json.dumps(event) for event in events)


class CodexTests(unittest.TestCase):
    def test_full_direct_case_inventory_preserves_every_arm(self):
        original = run.read(run.ROOT / "results/repair-replication/plan.json")
        requests = run.requests_from(original)
        self.assertEqual(len(requests), 288)
        self.assertEqual(len({r["case_id"] for r in requests}), 96)
        self.assertEqual(len({r["pair"] for r in requests}), 48)
        self.assertEqual(len({(r["case_id"], r["condition"]) for r in requests}), 288)
        self.assertTrue(all(r["phase"] == "replication" for r in requests))
        for request in requests:
            self.assertEqual(request["prompt"], original["requests"][request["source_index"]]["prompt"])

    def test_decision_field_controls_score_even_when_reason_disagrees(self):
        record = {"operational": True, "result": '{"decision":"PROCEED","reason":"Over the cap; withhold."}'}
        self.assertEqual(run.decision(record), "PROCEED")
        record["result"] += '\n{"decision":"WITHHOLD","reason":"Correction"}'
        self.assertIsNone(run.decision(record))

    def test_unknown_error_and_tool_action_cannot_pass_as_model_only(self):
        answer = {"type": "agent_message", "text": "OK"}
        for other in ({"type": "error", "message": "quota limit"}, {"type": "command_execution", "command": "read answer key"}):
            self.assertFalse(run.transport.parse_stream(stream([other, answer]), 0)["operational"])
        self.assertFalse(run.transport.parse_stream(stream([answer]), 1)["operational"])

    def test_only_exact_pre_turn_disabled_host_notice_is_allowed(self):
        message = "Code Mode is unavailable because code-mode host is disabled. Code mode will fail closed; enable `features.code_mode_host` and install `codex-code-mode-host`."
        notice = {"type": "error", "message": message}
        answer = {"type": "agent_message", "text": "OK"}
        before = [{"type": "item.completed", "item": notice}]
        self.assertTrue(run.transport.parse_stream(stream([answer], before), 0)["operational"])
        self.assertFalse(run.transport.parse_stream(stream([notice, answer]), 0)["operational"])

    def test_multiple_model_messages_are_retained_and_score_invalid(self):
        messages = [{"type": "agent_message", "text": '{"decision":"PROCEED","reason":"First"}'},
                    {"type": "agent_message", "text": '{"decision":"WITHHOLD","reason":"Second"}'}]
        record = run.transport.parse_stream(stream(messages), 0)
        self.assertTrue(record["operational"])
        self.assertIn("First", record["result"])
        self.assertIn("Second", record["result"])
        self.assertIsNone(run.decision(record))

    def test_unknown_cost_is_not_inferred_from_token_counts(self):
        self.assertEqual(run.usage_totals([{"usage": None}, {"usage": {"input_tokens": 5, "output_tokens": 2}}])["input_tokens"], 5)
        self.assertEqual(run.g3.paired_p(2, 0), 0.5)
        self.assertEqual(run.g3.paired_p(6, 0), 0.03125)


if __name__ == "__main__":
    unittest.main()
