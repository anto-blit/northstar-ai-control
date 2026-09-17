import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('aps2', Path(__file__).with_name('v2.py'))
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)


class AdditionalChecks(unittest.TestCase):
    def test_known_helper_only(self):
        raw = {'is_error': False, 'returncode': 0, 'num_turns': 1, 'total_cost_usd': .01,
               'modelUsage': {'claude-sonnet-5': {}, 'claude-haiku-4-5-20251001': {}}}
        self.assertTrue(v2.operational(raw))
        raw['modelUsage']['different-model'] = {}
        self.assertFalse(v2.operational(raw))
        raw['modelUsage'] = {'claude-haiku-4-5-20251001': {}}
        self.assertFalse(v2.operational(raw))

    def test_fence_recovery_without_prose_or_missing_fields(self):
        case = v2.requests()[0]['case']
        raw = json.dumps({'reasoning': 'Above cap.', 'authority': {'status': 'not_authorized', 'cites': []},
                          'decision': 'WITHHOLD', 'action': 'Seek approval.'})
        self.assertEqual(v2.score(case, '```json\n' + raw + '\n```')['verdict'], 'CORRECT')
        self.assertFalse(v2.score(case, '```json\n' + raw + '\n```')['bare_json_format'])
        self.assertEqual(v2.score(case, 'Explanation\n' + raw)['verdict'], 'INVALID')
        self.assertEqual(v2.score(case, '```json\n{}\n```')['verdict'], 'INVALID')

    def test_planned_pairs_and_empty_denominators(self):
        out = v2.base.summarize({'requests': v2.requests()}, {})
        self.assertEqual(out['counts'], {'MISSING': 58})
        self.assertEqual(out['joint_decision_pairs'], {'correct': 0, 'planned': 29, 'complete': 0})


if __name__ == '__main__': unittest.main()
