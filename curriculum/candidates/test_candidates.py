"""Check the new contracts' important counterexamples, not moral efficacy."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import explore


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.catalog = explore.load()

    def test_every_practice_case_has_an_inspectable_consistent_outcome(self):
        data = explore.prepare()
        self.assertEqual(len(data["cases"]), 12)
        self.assertEqual({r["assessment"]["disposition"] for r in data["cases"]}, {"ALLOW", "BLOCK", "REVIEW"})

    def test_truthful_negative_report_is_allowed_but_unsupported_positive_is_blocked(self):
        rows = {r["id"]: r for r in explore.prepare()["cases"]}
        self.assertEqual(rows["record-honest-failure"]["assessment"]["disposition"], "ALLOW")
        self.assertEqual(rows["record-mismatch"]["assessment"]["disposition"], "BLOCK")

    def test_revocation_does_not_cancel_an_unrelated_authorized_job(self):
        rows = {r["id"]: r for r in explore.prepare()["cases"]}
        self.assertEqual(rows["stop-revoked"]["assessment"]["disposition"], "BLOCK")
        self.assertEqual(rows["stop-other-job"]["assessment"]["disposition"], "ALLOW")

    def test_missing_facts_are_reviewed_and_known_tampering_overrides_uncertainty(self):
        self.assertEqual(explore.assess(self.catalog, "weighed-record", {})["disposition"], "REVIEW")
        self.assertEqual(explore.assess(self.catalog, "weighed-record", {"actor_modified_record": True})["disposition"], "BLOCK")

    def test_prose_and_unknown_fact_names_cannot_grant_authority(self):
        for facts in ({"authorization_valid": "trust me"}, {"stop_requested": False}):
            with self.assertRaises(ValueError):
                explore.assess(self.catalog, "working-stop", facts)

    def test_candidate_metadata_cannot_turn_examples_into_model_evidence(self):
        for key, value in (("model_calls", 12), ("human_reviewers", 1), ("deployment_approved", True),
                           ("behavioral_result", {"wins": 12})):
            with self.subTest(key=key), TemporaryDirectory() as name:
                root = Path(name)
                (root / "curriculum/candidates").mkdir(parents=True)
                catalog = deepcopy(self.catalog)
                catalog[key] = value
                (root / "curriculum/candidates/catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Candidate material cannot claim"):
                    explore.load(root)


if __name__ == "__main__":
    unittest.main()
