"""Integrity and risk-separation checks for the dashboard export."""
from copy import deepcopy
from hashlib import sha256
import json
import shutil
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
        # The guidance fixture preserves the actual frozen 48-call record so
        # corruption tests exercise the same graph of hashes as publication.
        shutil.copytree(dashboard.ROOT / "results/guidance-pilot", self.root / "results/guidance-pilot")
        shutil.copytree(dashboard.ROOT / "experiments/guidance-pilot", self.root / "experiments/guidance-pilot",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(dashboard.ROOT / "results/decision-repair", self.root / "results/decision-repair")
        shutil.copytree(dashboard.ROOT / "experiments/decision-repair", self.root / "experiments/decision-repair",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(dashboard.ROOT / "results/repair-replication", self.root / "results/repair-replication")
        shutil.copytree(dashboard.ROOT / "experiments/repair-replication", self.root / "experiments/repair-replication",
                        ignore=shutil.ignore_patterns("__pycache__"))
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

    def test_guidance_preserves_strict_scores_and_explains_substantive_tie(self):
        data = dashboard.load_guidance_evidence(self.root)
        self.assertEqual(data["calls"], 48)
        self.assertEqual(data["strict"]["E"]["correct_pairs"], 6)
        self.assertEqual(data["strict"]["S"]["correct_pairs"], 7)
        self.assertEqual([data["substantive"][a]["correct"] for a in "PES"], [16, 16, 16])
        self.assertTrue(data["formattingOnlyDifference"])

    def test_changed_guidance_response_is_rejected(self):
        (self.root / "results/guidance-pilot/responses/000.json").write_text('{"result":"improved"}')
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_guidance_evidence(self.root)

    def test_inflated_diagnostic_score_is_rejected(self):
        path = self.root / "results/guidance-pilot/format-diagnosis.json"
        data = json.loads(path.read_text())
        data["conditions"]["S"]["correct"] = 17
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "summary disagrees"):
            dashboard.load_guidance_evidence(self.root)

    def test_changed_guidance_source_is_rejected(self):
        (self.root / "experiments/guidance-pilot/materials.json").write_text('{"easier":true}')
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_guidance_evidence(self.root)

    def test_repair_counts_include_real_errors_and_preserved_usefulness(self):
        data = dashboard.load_repair_evidence(self.root)
        self.assertEqual(data["calls"], 216)
        self.assertEqual([data["conditions"][a]["unsafe_approvals"] for a in "BRE"], [3, 0, 0])
        self.assertEqual([data["conditions"][a]["useful_decisions"] for a in "BRE"], [36, 36, 36])
        self.assertEqual(data["conditions"]["B"]["invalid_or_missing"], 2)
        self.assertEqual(data["p"], 0.125)

    def test_invented_repair_gain_is_rejected(self):
        path = self.root / "results/decision-repair/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["conditions"]["B"]["unsafe_approvals"] = 10
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Repair summary disagrees"):
            dashboard.load_repair_evidence(self.root)

    def test_replication_report_cannot_invent_progress(self):
        path = self.root / "results/repair-replication/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["phases"]["replication"]["claude-sonnet-5"]["conditions"]["B"]["unsafe_approvals"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "report does not reproduce"):
            dashboard.load_replication_evidence(self.root)

    def test_replication_booking_evidence_cannot_be_forged(self):
        path = self.root / "results/repair-replication/ledger.json"
        ledger = json.loads(path.read_text(encoding="utf-8"))
        ledger.append({"request_index": -1, "case_id": "invented-booking"})
        path.write_text(json.dumps(ledger), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Frozen evidence changed"):
            dashboard.load_replication_evidence(self.root)


if __name__ == "__main__":
    unittest.main()
