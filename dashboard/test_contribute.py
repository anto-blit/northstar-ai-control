"""Input provenance and publication boundaries for the guided chat activity."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

import contribute_page


class ContributionTests(unittest.TestCase):
    def test_exact_user_prompts_without_answer_keys_or_source_responses(self):
        packet = contribute_page.packet()
        bundle = json.loads((contribute_page.ROOT / "reproducers/mislabel-v1/bundle.json").read_text(encoding="utf-8"))
        self.assertEqual([c["id"] for c in packet["cases"]], ["s0", "positive"])
        self.assertEqual(packet["maxMessages"], 2)
        for case in packet["cases"]:
            self.assertEqual(case["prompt"], bundle["cases"][case["id"]]["prompts"]["standard"])
            self.assertEqual(case["sha256"], sha256(case["prompt"].encode()).hexdigest())
            self.assertEqual(set(case), {"id", "prompt", "sha256"})

    def test_changed_source_is_rejected_before_publication(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for relative in ("reproducers/mislabel-v1/bundle.json", "dashboard/homepage-evidence.json"):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(contribute_page.ROOT / relative, target)
            with (root / "reproducers/mislabel-v1/bundle.json").open("ab") as file:
                file.write(b"\n")
            with self.assertRaisesRegex(ValueError, "evidence changed"):
                contribute_page.build_assets(root)

    def test_portable_page_and_published_plan_inputs_export_together(self):
        assets = contribute_page.build_assets()
        self.assertEqual(assets, contribute_page.build_assets())
        self.assertEqual(set(assets), {"contribute.html", "contributor-check-plan.txt", "contributor-check-inputs.json"})
        self.assertEqual(json.loads(assets["contributor-check-inputs.json"]), contribute_page.packet())
        page = assets["contribute.html"].decode()
        self.assertNotIn("@@", page)
        self.assertNotIn('<script src=', page)
        self.assertIn('<noscript>', page)
        self.assertIn('no automatic score', assets["contributor-check-plan.txt"].decode().lower())


if __name__ == '__main__':
    unittest.main()
