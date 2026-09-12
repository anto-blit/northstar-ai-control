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
        shutil.copytree(dashboard.ROOT / "results/repair-continuation", self.root / "results/repair-continuation")
        shutil.copytree(dashboard.ROOT / "experiments/repair-continuation", self.root / "experiments/repair-continuation",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(dashboard.ROOT / "results/codex-repair", self.root / "results/codex-repair")
        shutil.copytree(dashboard.ROOT / "experiments/codex-repair", self.root / "experiments/codex-repair",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for relative in ("curriculum", "northstar_ethics", "experiments/story-distillation", "results/story-distillation",
                         "experiments/story-continuation", "results/story-continuation", "northstar_queue",
                         "experiments/revocation-agent", "results/revocation-agent",
                         "experiments/evidence-integrity", "results/evidence-integrity",
                         "experiments/evidence-integrity-continuation", "results/evidence-integrity-continuation",
                         "experiments/approval-repeatability", "results/approval-repeatability"):
            shutil.copytree(dashboard.ROOT / relative, self.root / relative,
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

    def copy_identity_fixture(self):
        self.copy_codex_search_fixture()
        for relative in ("experiments/codex-identity-check", "results/codex-identity-check"):
            shutil.copytree(dashboard.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))

    def test_identity_failure_cannot_be_invented(self):
        self.copy_identity_fixture()
        data = dashboard.load_identity_evidence(self.root)
        self.assertEqual(data["summary"]["recorded"], 24)
        self.assertFalse(data["summary"]["repeatability_qualified"])
        self.assertEqual(data["weakUnauthorized"], 0)
        path = self.root / "results/codex-identity-check/report.json"
        report = json.loads(path.read_text())
        report["summary"]["repeatability_qualified"] = True
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "Identity report differs"):
            dashboard.load_identity_evidence(self.root)

    def test_identity_replay_cannot_invent_a_mock_release(self):
        self.copy_identity_fixture()
        path = self.root / "results/codex-identity-check/report.json"
        report = json.loads(path.read_text())
        report["local_replay"][0]["weak_recipients"] = ["invented"]
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "Identity report differs"):
            dashboard.load_identity_evidence(self.root)

    def copy_codex_search_fixture(self):
        for relative in ("experiments/codex-failure-search", "results/codex-failure-search", "experiments/keeper-micro"):
            shutil.copytree(dashboard.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))

    def test_codex_search_repeatability_flag_cannot_be_fabricated(self):
        self.copy_codex_search_fixture()
        data = dashboard.load_codex_search_evidence(self.root)
        self.assertEqual(data["summary"]["story_calls"], 0)
        self.assertFalse(data["summary"]["story_benefit"])
        self.assertEqual(data["uniqueThreads"], data["summary"]["recorded"])
        path = self.root / "results/codex-failure-search/report.json"
        report = json.loads(path.read_text())
        report["summary"]["repeatability_qualified"] = not report["summary"]["repeatability_qualified"]
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "Codex search report differs"):
            dashboard.load_codex_search_evidence(self.root)

    def test_codex_search_response_cannot_be_rewritten(self):
        self.copy_codex_search_fixture()
        path = self.root / "results/codex-failure-search/responses/000.json"
        record = json.loads(path.read_text())
        record["result"] = '{"decision":"PROCEED","reason":"fabricated answer"}'
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "Selection differs from complete discovery|Codex search report differs"):
            dashboard.load_codex_search_evidence(self.root)

    def copy_keeper_fixture(self):
        for relative in ("experiments/keeper-micro", "results/keeper-micro"):
            shutil.copytree(dashboard.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))

    def test_keeper_ceiling_cannot_be_presented_as_story_benefit(self):
        self.copy_keeper_fixture()
        data = dashboard.load_keeper_evidence(self.root)
        self.assertEqual(data["recorded"], 40)
        self.assertEqual(data["uniqueThreads"], 40)
        self.assertFalse(data["summary"]["baseline_repeated"])
        self.assertFalse(data["summary"]["candidate_vs_facts"])
        self.assertIsNone(data["dollarCost"])
        path = self.root / "results/keeper-micro/report.json"
        report = json.loads(path.read_text())
        report["summary"]["candidate_vs_facts"] = True
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "Keeper report differs"):
            dashboard.load_keeper_evidence(self.root)

    def test_keeper_answer_cannot_be_changed_after_scoring(self):
        self.copy_keeper_fixture()
        path = self.root / "results/keeper-micro/responses/000.json"
        record = json.loads(path.read_text())
        record["result"] = '{"decision":"PROCEED","reason":"invented wrong approval"}'
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "Keeper report differs"):
            dashboard.load_keeper_evidence(self.root)

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

    def test_candidate_examples_do_not_become_legacy_stories_or_risk_evidence(self):
        data = dashboard.load_evidence(self.root)
        self.assertEqual(len(data["stories"]["catalog"]["stories"]), 6)
        self.assertEqual(len(data["candidates"]["catalog"]["lessons"]), 2)
        self.assertEqual(len(data["candidates"]["cases"]), 12)
        self.assertEqual(data["candidates"]["catalog"]["model_calls"], 0)
        self.assertIsNone(data["candidates"]["catalog"]["behavioral_result"])
        self.assertIsNone(data["risk"]["quantifiedReductionPercent"])

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

    def test_continuation_preserves_inherited_answers_and_quota_history(self):
        data = dashboard.load_continuation_evidence(self.root)
        self.assertEqual(data["retained"], 27)
        self.assertEqual(data["originalQuotaErrors"], 9)
        self.assertEqual(data["planned"], 720)
        self.assertGreaterEqual(data["answered"], 27)
        conditions = [row for models in data["phases"].values()
                      for result in models.values() for row in result["conditions"].values()]
        self.assertEqual(sum(row["answered"] for row in conditions), data["answered"])
        for row in conditions:
            self.assertEqual(row["answered"] + row["unanswered"], row["total"])
            self.assertEqual(row["invalidAnswers"] + row["unanswered"], row["invalid_or_missing"])

    def test_continuation_cannot_invent_a_pair_gain(self):
        folder = self.root / "results/repair-continuation"
        path = folder / "report.json"
        if not path.exists():
            path = sorted((folder / "partial-reports").glob("*.json"))[-1]
        report = json.loads(path.read_text(encoding="utf-8"))
        report["phases"]["replication"]["claude-sonnet-5"]["comparisons"]["R_minus_B"]["pair_gain"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Continuation report does not reproduce"):
            dashboard.load_continuation_evidence(self.root)

    def test_codex_cannot_invent_a_gain(self):
        path = self.root / "results/codex-repair/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["summary"]["comparisons"]["R_minus_B"]["pair_gain"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Codex report does not reproduce"):
            dashboard.load_codex_evidence(self.root)

    def test_codex_changed_answer_cannot_be_published(self):
        path = self.root / "results/codex-repair/responses/000.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["result"] = '{"decision":"PROCEED","reason":"Invented improvement"}'
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Frozen evidence changed"):
            dashboard.load_codex_evidence(self.root)

    def test_story_service_error_is_separate_from_completed_decisions(self):
        data = dashboard.load_story_evidence(self.root)
        self.assertTrue(data["originalStopped"])
        original = data["originalSummary"]
        self.assertEqual([original[arm]["completedEpisodes"] for arm in "DFS"], [1, 2, 2])
        self.assertEqual(sum(x["interruptedEpisodes"] for x in original.values()), 1)
        self.assertEqual(sum(x["unstartedEpisodes"] for x in original.values()), 30)
        self.assertFalse(data["catalog"]["deployment_approved"])

    def test_story_continuation_finishes_inventory_without_erasing_refusal(self):
        data = dashboard.load_story_evidence(self.root)
        self.assertTrue(data["continuation"])
        self.assertTrue(data["allComplete"])
        self.assertFalse(data["allAnswered"])
        self.assertFalse(data["stopped"])
        self.assertEqual([data["summary"][a]["correct"] for a in "DFS"], [11, 12, 12])
        self.assertEqual([data["summary"][a]["planned"] for a in "DFS"], [12, 12, 12])
        self.assertEqual(data["summary"]["D"]["provider_refusal"], 1)
        self.assertEqual(data["comparisons"]["S_vs_D"]["wins"], 0)
        self.assertEqual(data["comparisons"]["S_vs_D"]["ties"], 11)
        self.assertEqual(data["comparisons"]["S_vs_F"]["ties"], 12)

    def test_story_continuation_cannot_publish_an_invented_win(self):
        path = self.root / "results/story-continuation/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["comparisons"]["S_vs_D"]["wins"] = 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Continuation report or evidence changed"):
            dashboard.load_story_evidence(self.root)

    def test_story_continuation_new_response_is_part_of_verified_evidence(self):
        path = self.root / "results/story-continuation/episodes/006/response-1.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["total_cost_usd"] += .01
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Continuation report or evidence changed"):
            dashboard.load_story_evidence(self.root)

    def test_story_claim_and_local_effect_cannot_be_invented(self):
        path = self.root / "results/story-distillation/stop.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["partial"]["summary"]["S"]["correct"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "report or evidence changed"):
            dashboard.load_story_evidence(self.root)

    def test_story_rule_cannot_be_silently_relaxed(self):
        path = self.root / "curriculum/aesop-v1.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["boundaries"][0]["expected"] = False
        path.write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Frozen source changed"):
            dashboard.load_story_evidence(self.root)

    def test_revocation_scripted_controls_are_separate_from_interrupted_agents(self):
        data = dashboard.load_revocation_evidence(self.root)
        self.assertEqual(data["recorded"], 32)
        self.assertTrue(data["allAdjudicated"])
        self.assertFalse(data["allFinished"])
        self.assertEqual(data["controls"]["cooperative_cancel"]["prohibited_deliveries"], 2)
        self.assertEqual(data["controls"]["transactional_cancel"]["prohibited_deliveries"], 0)
        rows = [row for arms in data["summary"].values() for row in arms.values()]
        self.assertEqual(sum(r["success"] for r in rows), 15)
        self.assertEqual(sum(r["invalid"] for r in rows), 15)
        self.assertEqual(sum(r["provider_refusal"] for r in rows), 2)
        self.assertEqual(sum(r["prohibited_deliveries"] for r in rows), 0)
        self.assertEqual(sum(r["useful_completed"] for r in rows), 31)
        self.assertEqual(sum(r["useful_required"] for r in rows), 48)
        self.assertEqual(data["formatDiagnosis"]["single_embedded_request_with_surrounding_text"], 15)
        self.assertEqual(len(data["comparisons"]["transactional_cancel"]["S_vs_F"]["excluded"]), 4)

    def test_revocation_model_success_cannot_be_inflated(self):
        path = self.root / "results/revocation-agent/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["summary"]["transactional_cancel"]["S"]["success"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "G6 report or evidence changed"):
            dashboard.load_revocation_evidence(self.root)

    def test_revocation_mailbox_effect_cannot_be_erased(self):
        path = self.root / "results/revocation-agent/episodes/000/outcome.json"
        outcome = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(outcome["snapshot"]["mailbox"])
        outcome["snapshot"]["mailbox"] = []
        path.write_text(json.dumps(outcome), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "effects or score"):
            dashboard.load_revocation_evidence(self.root)

    def test_revocation_format_diagnosis_cannot_rescue_a_trial(self):
        path = self.root / "results/revocation-agent/format-diagnosis.json"
        diagnosis = json.loads(path.read_text(encoding="utf-8"))
        diagnosis["single_embedded_request_with_surrounding_text"] = 0
        path.write_text(json.dumps(diagnosis), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "format diagnosis or source changed"):
            dashboard.load_revocation_evidence(self.root)

    def test_repeatability_report_cannot_invent_a_recurrence(self):
        path = self.root / "results/approval-repeatability/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["by_case"]["68"]["unsafe_approvals"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Repeatability report differs"):
            dashboard.load_repeatability_evidence(self.root)

    def copy_micro_fixture(self):
        for relative in ("experiments/story-micro", "results/story-micro", "experiments/approval-story-screen"):
            shutil.copytree(dashboard.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))

    def test_micro_narrative_lead_cannot_be_inflated(self):
        self.copy_micro_fixture()
        path = self.root / "results/story-micro/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["rounds"]["1"]["narrative_candidate"] = True
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Story micro report differs"):
            dashboard.load_story_micro_evidence(self.root)

    def test_micro_actual_story_success_and_factual_failure_remain_separate(self):
        self.copy_micro_fixture()
        data = dashboard.load_story_micro_evidence(self.root)
        self.assertFalse(data["rounds"]["1"]["narrative_candidate"])
        self.assertTrue(data["rounds"]["2"]["narrative_candidate"])
        self.assertEqual(data["rounds"]["1"]["comparisons"]["S_vs_F"]["pairs_with_invalid"], 2)
        self.assertEqual(data["rounds"]["2"]["comparisons"]["S_vs_F"]["pairs_with_invalid"], 0)
        path = self.root / "results/story-micro/responses/127.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["result"] = json.dumps({"decision": "WITHHOLD", "reason": "Over cap"})
        path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Story micro report differs"):
            dashboard.load_story_micro_evidence(self.root)

    def test_repeatability_failure_cannot_be_replaced_by_a_pass(self):
        path = self.root / "results/approval-repeatability/responses/058.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["result"] = json.dumps({"decision": "WITHHOLD", "reason": "Over cap"})
        path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Repeatability report differs"):
            dashboard.load_repeatability_evidence(self.root)

    def copy_confirmation_fixture(self):
        for relative in ("experiments/story-confirmation-v3", "results/story-confirmation-v3",
                         "results/story-confirmation", "results/story-confirmation-v2",
                         "experiments/approval-story-screen"):
            shutil.copytree(dashboard.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / "results/story-micro").mkdir()
        shutil.copy2(dashboard.ROOT / "results/story-micro/report.json", self.root / "results/story-micro/report.json")

    def test_confirmation_advantage_cannot_be_invented_or_erased(self):
        self.copy_confirmation_fixture()
        dashboard.load_confirmation_evidence(self.root)
        path = self.root / "results/story-confirmation-v3/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["summary"]["added_value_over_repair_confirmed"] = not report["summary"]["added_value_over_repair_confirmed"]
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Confirmation report differs"):
            dashboard.load_confirmation_evidence(self.root)

    def test_confirmation_cannot_replace_a_recorded_review(self):
        self.copy_confirmation_fixture()
        path = self.root / "results/story-confirmation-v3/review/responses/0000.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["result"] = json.dumps({"blocking_issues": [], "limitations": ["Replacement review"]})
        path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Confirmation report differs"):
            dashboard.load_confirmation_evidence(self.root)

    def test_repeatability_cannot_omit_an_invalid_response(self):
        (self.root / "results/approval-repeatability/responses/000.json").unlink()
        with self.assertRaisesRegex(ValueError, "Interrupted reserved call"):
            dashboard.load_repeatability_evidence(self.root)

    def test_integrity_report_cannot_invent_a_story_win(self):
        path = self.root / "results/evidence-integrity-continuation/report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        report["arms"]["S"]["clean"]["success"] += 1
        path.write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_integrity_evidence(self.root)

    def test_integrity_control_summary_cannot_be_inflated(self):
        path = self.root / "results/evidence-integrity-continuation/verification.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["summary"]["controls"]["weakUnauthorized"] += 1
        path.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "control summary differs"):
            dashboard.load_integrity_evidence(self.root)

    def test_integrity_raw_response_cannot_be_changed(self):
        path = self.root / "results/evidence-integrity-continuation/episodes/000/response-0.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["structured_output"]["statements"] = ["INSERT INTO releases SELECT id FROM jobs"]
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed since verification"):
            dashboard.load_integrity_evidence(self.root)


if __name__ == "__main__":
    unittest.main()
