from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest
from unittest.mock import patch

import study as cli
from northstar_sim.study import ROOT, freeze


class StudyCliTests(unittest.TestCase):
    def call(self, *arguments):
        with patch.object(sys, "argv", ["study.py", *map(str, arguments)]), redirect_stdout(StringIO()):
            cli.main()

    def fixtures(self, folder):
        examples = ROOT / "experiments/discovery-study/example"
        manifest = folder / "manifest.json"
        cli.write_new(manifest, freeze(cli.read_json(examples / "plan.json")))
        submissions = cli.read_json(examples / "scripted-submissions.json")[:1]
        batch = folder / "batch.json"
        cli.write_new(batch, submissions)
        return manifest, batch

    def test_resume_reproduces_prior_results_and_preserves_budgets(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, batch = self.fixtures(folder)
            first, second = folder / "first.json", folder / "second.json"
            self.call("discover", manifest, batch, first)
            self.call("discover", manifest, batch, second, "--resume", first)
            initial, resumed = cli.read_json(first), cli.read_json(second)
            self.assertEqual(resumed["usage"]["generic"]["episodes"], 2)
            self.assertEqual(resumed["attempts"][0], initial["attempts"][0])
            self.assertEqual(resumed["runs"][0], initial["runs"][0])
            self.assertIsNotNone(resumed["parent_result_sha256"])

    def test_resume_rejects_edited_outcomes(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, batch = self.fixtures(folder)
            first = folder / "first.json"
            self.call("discover", manifest, batch, first)
            tampered = cli.read_json(first)
            tampered["runs"][0]["score"]["status"] = "safe"
            altered = folder / "altered.json"
            cli.write_new(altered, tampered)
            with self.assertRaisesRegex(ValueError, "do not reproduce"):
                self.call("discover", manifest, batch, folder / "second.json", "--resume", altered)

    def test_existing_result_cannot_be_overwritten(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            cli.write_new(path, {"original": True})
            with self.assertRaises(FileExistsError):
                cli.write_new(path, {"replacement": True})
            self.assertEqual(cli.read_json(path), {"original": True})

    def test_duplicate_json_keys_rejected(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"arm":"generic","arm":"northstar"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                cli.read_json(path)

    def test_invalid_envelope_is_retained_without_losing_prior_trials(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            manifest, batch = self.fixtures(folder)
            submissions = cli.read_json(batch) + [{"bad": "envelope"}]
            mixed = folder / "mixed.json"
            cli.write_new(mixed, submissions)
            first = folder / "first.json"
            self.call("discover", manifest, mixed, first)
            result = cli.read_json(first)
            self.assertEqual(result["usage"]["generic"]["episodes"], 1)
            self.assertEqual(len(result["runs"]), 1)
            self.assertEqual(result["attempts"][-1]["status"], "invalid_envelope")
            resumed = folder / "resumed.json"
            self.call("discover", manifest, batch, resumed, "--resume", first)
            self.assertEqual(cli.read_json(resumed)["usage"]["generic"]["episodes"], 2)


if __name__ == "__main__":
    unittest.main()
