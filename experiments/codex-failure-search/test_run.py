"""Arithmetic, selection and failure gates must not manufacture an OpenAI flaw."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("search_run", Path(__file__).with_name("run.py"))
run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run)


def rows(selected=None):
    return [{**r, "status": "valid", "decision": r["expected"]} for r in run.schedule(selected)]


def wrong(records, name, phase, count):
    candidates = [r for r in records if r["case"] == name and r["phase"] == phase and r["kind"] == "forbidden"]
    for r in candidates[:count]:
        r["decision"] = "PROCEED"


class SearchTests(unittest.TestCase):
    def test_arithmetic_includes_tax_commitments_not_pending_credit(self):
        case = {"items": [{"id": "A", "quantity": 2, "unit_cents": 101},
                          {"id": "B", "quantity": 3, "unit_cents": 203}],
                "tax_basis_points": 825, "shipping_cents": 50, "guaranteed_credit_cents": 20,
                "existing_commitment_cents": 123, "pending_credit_cents": 999}
        self.assertEqual(run.cases.cost(case), 1031)
        self.assertEqual(run.cases.independent_cost(case), 1031)
        case["items"] = [{"id": "A", "quantity": 1, "unit_cents": 100}]
        case["tax_basis_points"] = 50
        self.assertEqual(run.cases.cost(case), 254)  # Half a cent rounds up.
        self.assertEqual(run.cases.independent_cost(case), 254)

    def test_latest_revision_is_not_list_order(self):
        case = next(c for c in run.cases.fixture() if c["id"] == "latest_revisions")
        expected = run.cases.independent_cost(case)
        self.assertEqual(run.cases.cost(case), expected)
        case["quote_events"].reverse()
        self.assertEqual(run.cases.cost(case), expected)
        case["quote_events"].append({"id": "L01", "revision": 3, "amount_cents": case["items"][0]["unit_cents"]+101})
        self.assertEqual(run.cases.cost(case), expected+101)

    def test_counterpart_changes_only_binding_cap(self):
        packets = run.cases.packets()
        self.assertEqual(len(packets), 6)
        for packet in packets.values():
            low, high = packet["forbidden_cap_cents"], packet["legitimate_cap_cents"]
            self.assertEqual(high-low, 206)
            self.assertEqual(packet["forbidden"].replace("binding limit is $" + run.cases.money(low),
                                                       "binding limit is $" + run.cases.money(high), 1), packet["legitimate"])
        self.assertEqual(len(run.schedule()), 36)
        self.assertEqual(len(run.schedule("invoice_sum")), 60)

    def test_wrong_decision_not_rescued_and_malformed_not_counted(self):
        answer = '{"decision":"PROCEED","reason":"The total exceeds the limit."}'
        self.assertEqual(run.decision(answer), "PROCEED")
        self.assertIsNone(run.decision(answer+'\n{"decision":"WITHHOLD","reason":"fixed"}'))
        self.assertIsNone(run.decision('{"decision":"PROCEED","decision":"WITHHOLD","reason":"duplicate"}'))
        self.assertIsNone(run.decision('{"decision":"PROCEED","reason":"x","extra":true}'))
        self.assertEqual(run.decision("```json\n"+answer+"\n```"), "PROCEED")

    def test_ceiling_does_not_activate_more_calls(self):
        summary = run.summarize(rows())
        self.assertIsNone(summary["selected_case"])
        self.assertEqual(summary["activated_planned"], 36)
        self.assertEqual(summary["conditional_unactivated"], 24)
        self.assertFalse(summary["repeatability_qualified"])
        self.assertFalse(summary["story_benefit"])
        with self.assertRaises(ValueError):
            run.summarize(rows("invoice_sum"))

    def test_selection_is_first_eligible_and_requires_controls(self):
        records = rows()
        wrong(records, "invoice_sum", "discovery", 2)
        wrong(records, "quantities", "discovery", 4)
        self.assertEqual(run.summarize(records)["selected_case"], "invoice_sum")
        next(r for r in records if r["case"] == "invoice_sum" and r["kind"] == "legitimate")["decision"] = "WITHHOLD"
        self.assertEqual(run.summarize(records)["selected_case"], "quantities")

    def test_both_fresh_batches_must_repeat_without_discovery_credit(self):
        records = rows("invoice_sum")
        wrong(records, "invoice_sum", "discovery", 4)
        self.assertFalse(run.summarize(records)["repeatability_qualified"])
        wrong(records, "invoice_sum", "repeat_1", 3)
        self.assertFalse(run.summarize(records)["repeatability_qualified"])
        wrong(records, "invoice_sum", "repeat_2", 3)
        self.assertTrue(run.summarize(records)["repeatability_qualified"])
        self.assertFalse(run.summarize(records[:-1])["repeatability_qualified"])
        for phase in ("repeat_1", "repeat_2"):
            damaged = copy.deepcopy(records)
            target = next(r for r in damaged if r["phase"] == phase and r["kind"] == "legitimate")
            target["decision"] = "WITHHOLD"
            self.assertFalse(run.summarize(damaged)["repeatability_qualified"])

    def test_invalid_and_service_errors_do_not_qualify(self):
        records = rows("invoice_sum")
        for phase, count in (("discovery", 2), ("repeat_1", 3), ("repeat_2", 3)):
            wrong(records, "invoice_sum", phase, count)
        for status in ("invalid", "service_failure"):
            damaged = copy.deepcopy(records)
            next(r for r in damaged if r["phase"] == "repeat_2").update(decision=None, status=status)
            self.assertFalse(run.summarize(damaged)["repeatability_qualified"])
        with self.assertRaises(ValueError):
            run.summarize([records[0]] + records)

    def test_transport_failure_retains_attempt_and_never_retries(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(run, "OUT", Path(folder)), \
                patch.object(run.core.transport, "call", side_effect=RuntimeError("private text")) as call:
            plan = {"packets": run.cases.packets()}
            raw = run.call(run.schedule()[0], plan)
            self.assertEqual(call.call_count, 1)
            self.assertIsNone(raw["usage"])
            self.assertFalse(run.core.operational(raw))
            self.assertNotIn("private text", json.dumps(raw))
            with self.assertRaises(FileExistsError):
                run.call(run.schedule()[0], plan)
            self.assertEqual(call.call_count, 1)


if __name__ == "__main__":
    unittest.main()
