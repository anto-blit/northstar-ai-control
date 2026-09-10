"""Integrity and risk-separation checks for the dashboard export."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import build_dashboard as dashboard


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "results").mkdir()
        (self.root / "proof.py").write_bytes(b"verified source\n")
        artifacts = {"recoverability.json": {"schema_version": 2},
                     "monitor-sweep.json": {"schema_version": 2}}
        hashes = {}
        for name, value in artifacts.items():
            raw = json.dumps(value).encode()
            (self.root / "results" / name).write_bytes(raw)
            hashes[name] = sha256(raw).hexdigest()
        self.report = {"failures": 0, "errors": 0, "tests_run": 90,
                       "started_at": "2026-09-10T04:25:18+00:00", "python": "3.14",
                       "source_sha256": {"proof.py": sha256(b"verified source\n").hexdigest()},
                       "artifact_sha256": hashes}
        self.save_report()
        queue = self.root / "results/queue-integration"
        (queue / "internal").mkdir(parents=True)
        internal = {"technical_errors": [], "summary": {}, "source_sha256": self.report["source_sha256"]}
        (queue / "internal/report.json").write_text(json.dumps(internal))
        (self.root / "review.md").write_text("Separate AI review fixture")
        (self.root / "review.json").write_text(json.dumps({"review_runs": [{"candidate": "first", "failures": 1}, {"candidate": "repair", "failures": 0}], "artifact_sha256": {"review.md": sha256((self.root / "review.md").read_bytes()).hexdigest()}}))
        self.queue_report = {
            "schema_version": 1, "source_sha256": self.report["source_sha256"],
            "artifact_sha256": {"internal/report.json": sha256((queue / "internal/report.json").read_bytes()).hexdigest()},
            "tests": {"internal": {"tests_run": 10, "failures": 0, "errors": 0},
                      "claude_authored": {"tests_run": 1, "failures": 0, "errors": 0}},
            "review_provenance": "review.json", "review_provenance_sha256": sha256((self.root / "review.json").read_bytes()).hexdigest(),
            "summary": {}, "recorded_at": self.report["started_at"],
            "review_type": "Separate AI review", "independent_human_review": False,
        }
        self.save_queue_report()

    def save_queue_report(self):
        (self.root / "results/queue-integration/verification.json").write_text(json.dumps(self.queue_report))

    def save_report(self):
        (self.root / "results/verification.json").write_text(json.dumps(self.report), encoding="utf-8")

    def test_uses_recorded_counts_and_marks_probability_as_unknown(self):
        data = dashboard.load_evidence(self.root)
        self.assertEqual(data["verification"]["tests"], 90)
        self.assertEqual(data["risk"]["assumedBaselinePercent"], 10)
        self.assertIsNone(data["risk"]["currentEstimatePercent"])
        self.assertIsNone(data["risk"]["quantifiedReductionPercent"])
        self.assertIsNone(data["risk"]["potentialGlobalReductionPercent"])
        self.assertEqual(data["risk"]["claimAttribution"], "Geoffrey Hinton")
        self.assertEqual(data["risk"]["claimRangePercent"], [10, 20])
        self.assertIn("wbur.org/onpoint/", data["risk"]["claimSource"])
        self.assertIn("not a rolling horizon", data["risk"]["claimTimeHorizon"])
        self.assertEqual(data["risk"]["demonstratedProtectionScope"], "Synthetic brokers and local HTTP/SQLite queue integration only")
        self.assertFalse(data["queue"]["independentHumanReview"])
        self.assertEqual(data["queue"]["reviewRounds"], 2)

    def test_more_passing_tests_do_not_subtract_from_extinction_risk(self):
        before = deepcopy(dashboard.load_evidence(self.root)["risk"])
        self.report["tests_run"] = 10000
        self.save_report()
        self.assertEqual(dashboard.load_evidence(self.root)["risk"], before)

    def test_stale_source_is_rejected(self):
        (self.root / "proof.py").write_bytes(b"unverified edit")
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_evidence(self.root)

    def test_stale_result_is_rejected(self):
        (self.root / "results/monitor-sweep.json").write_text('{"schema_version":2,"edited":true}')
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_evidence(self.root)

    def test_failed_verification_cannot_be_presented_as_passing(self):
        self.report["failures"] = 1
        self.save_report()
        with self.assertRaisesRegex(ValueError, "failed verification"):
            dashboard.load_evidence(self.root)

    def test_missing_provenance_is_rejected(self):
        self.report["source_sha256"] = {}
        self.save_report()
        with self.assertRaisesRegex(ValueError, "provenance"):
            dashboard.load_evidence(self.root)

    def test_provenance_paths_cannot_escape_repository(self):
        self.report["source_sha256"] = {"../outside.py": "0" * 64}
        self.save_report()
        with self.assertRaisesRegex(ValueError, "inside the repository"):
            dashboard.load_evidence(self.root)

    def test_export_is_deterministic_and_contains_no_fetch_dependency(self):
        first = dashboard.render(self.root)
        self.assertEqual(first, dashboard.render(self.root))
        self.assertIn('id="northstar-data" type="application/json"', first)
        self.assertNotIn("@@DATA@@", first)
        self.assertNotIn("fetch(", first)

    def test_changed_queue_report_cannot_be_published(self):
        (self.root / "results/queue-integration/internal/report.json").write_text('{"edited":true}')
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_evidence(self.root)

    def test_failed_queue_checks_cannot_be_published_as_passing(self):
        self.queue_report["tests"]["internal"]["failures"] = 1
        self.save_queue_report()
        with self.assertRaisesRegex(ValueError, "failed queue"):
            dashboard.load_evidence(self.root)

    def test_changed_reviewer_provenance_cannot_be_published(self):
        (self.root / "review.json").write_text('{"type":"unverified endorsement"}')
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_evidence(self.root)


if __name__ == "__main__":
    unittest.main()
