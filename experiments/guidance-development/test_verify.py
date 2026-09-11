"""Regression for the cross-version cost discrepancy, using actual saved costs."""
import contextlib
import functools
import importlib.util
import io
import json
import operator
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("development_replay", Path(__file__).with_name("verify.py"))
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class PortableReplayTests(unittest.TestCase):
    def test_actual_costs_reproduce_report_despite_older_sum_rounding(self):
        root = Path(__file__).resolve().parents[2]
        report = json.loads((root / "results/guidance-development/report.json").read_text(encoding="utf-8"))
        costs = [row["cost_usd"] for row in report["observations"] if row["condition"] == "E"]
        expected = report["conditions"]["E"]["reported_cost_usd"]
        self.assertNotEqual(functools.reduce(operator.add, costs, 0), expected)
        self.assertEqual(replay.stable_sum(costs), expected)
        self.assertEqual(replay.stable_sum([True, False, True]), 2)
        self.assertIs(type(replay.stable_sum([True, False, True])), int)

    def test_full_frozen_replay(self):
        with contextlib.redirect_stdout(io.StringIO()):
            replay.main()


if __name__ == "__main__":
    unittest.main()
