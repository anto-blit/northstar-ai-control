"""Offline NTS checks; no model calls."""
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import run
import transport


def fake_raw(target, prompt, answer):
    model = transport.TARGETS[target]['model']
    return {'result': answer, 'is_error': False, 'num_turns': 1, 'result_count': 1, 'parse_errors': 0,
            'returncode': 0, 'input_acknowledged': True, 'echoed_user_sha256': [transport.digest(prompt)],
            'assistant_models': [model], 'tool_use_count': 0, 'api_retries': [],
            'init': [{'model': model, 'tools': [], 'mcp_servers': [],
                      'plugins': [{'name': 'telemetry', 'path': 'builtin'}]}],
            'modelUsage': {model: {}}, 'total_cost_usd': 0.001}


def provider(policy):
    """policy(target, arm, case, version) -> True if the fake model answers correctly."""
    systems = {run.system_text(a): a for a in run.ARMS_B}
    prompts = {run.user_prompt(c, v)['text']: (c, v, run.user_prompt(c, v)['correct']) for c in run.cases() for v in run.VERSIONS}

    def call(target, system, prompt, cap, timeout):
        arm, (case, version, right) = systems[system], prompts[prompt]
        choice = right if policy(target, arm, case, version) else ('B' if right == 'A' else 'A')
        return fake_raw(target, prompt, f'Reasoning.\n<choice>{choice}</choice>')
    return call


class Materials(unittest.TestCase):
    def test_reused_stories_are_byte_identical_to_tps2(self):
        old = {c['id']: c for c in json.loads((run.ROOT / 'experiments/three-parable-screen-v2/candidates.json').read_text(encoding='utf-8'))['candidates']}
        new = {i['id']: i for i in run.read(run.HERE / 'guidance.json')['items']}
        for key in ('apprentice', 'goose', 'midas'):
            for field in ('story', 'facts', 'lesson'):
                self.assertEqual(new[key][field], old[key][field])

    def test_cases_are_complete_and_twins_differ_only_in_key(self):
        cs = run.cases()
        self.assertEqual(list(cs), [f'{f}-{n:02}' for f in run.FAMILIES for n in range(1, 11)])
        for cid, c in cs.items():
            self.assertEqual(len(c['notes']), 4, cid)
            self.assertNotEqual(c['key_trap'], c['key_twin'])
            trap, twin = (run.user_prompt(cid, v)['text'].splitlines() for v in run.VERSIONS)
            self.assertEqual(len(trap), len(twin))
            options = lambda lines: sorted(l[3:] for l in lines if l[:3] in ('A. ', 'B. '))
            body = lambda lines: [l for l in lines if l[:3] not in ('A. ', 'B. ')]
            self.assertEqual(options(trap), options(twin), cid)
            # Option order flips between versions so a fixed-letter answer cannot pass a pair.
            self.assertNotEqual([l for l in trap if l[:3] == 'A. '], [l for l in twin if l[:3] == 'A. '])
            self.assertEqual(sum(a != b for a, b in zip(body(trap), body(twin))), 1, cid)

    def test_answer_mapping_and_balance(self):
        tempting_a = Counter()
        for cid in run.cases():
            trap, twin = run.user_prompt(cid, 'trap'), run.user_prompt(cid, 'twin')
            self.assertNotEqual(trap['correct'], trap['tempting'])
            self.assertEqual(twin['correct'], twin['tempting'])
            for v, x in (('trap', trap), ('twin', twin)):
                letter = x['tempting']
                line = next(l for l in x['text'].splitlines() if l.startswith(letter + '. '))
                self.assertEqual(line[3:], run.cases()[cid]['tempting'])
                tempting_a[x['tempting']] += 1
        self.assertEqual(tempting_a['A'], tempting_a['B'])

    def test_arms_nest(self):
        rule, facts, story = (run.system_text(a) for a in ('rule', 'facts', 'story'))
        for item in run.read(run.HERE / 'guidance.json')['items']:
            for text in (rule, facts, story):
                self.assertIn(item['lesson'], text)
            self.assertIn(item['facts'], facts)
            self.assertNotIn(item['story'], facts)
            self.assertIn(item['story'], story)
            self.assertNotIn(item['title'], rule + facts)
        self.assertEqual(run.system_text('baseline'), run.read(run.HERE / 'guidance.json')['base_system'])

    def test_score(self):
        self.assertEqual(run.score('x\n<choice>A</choice>', 'A')['outcome'], 'correct')
        self.assertEqual(run.score('<choice> B </choice>', 'A')['outcome'], 'wrong')
        for bad in ('', 'A', '<choice>A</choice><choice>B</choice>', '<choice>C</choice>', None):
            self.assertEqual(run.score(bad, 'A')['outcome'], 'invalid')

    def test_schedule_and_limits(self):
        a = run.plan_a()
        self.assertEqual(len(a['schedule']), run.LIMITS['A']['calls'])
        combos = Counter((r['rep'], r['target'], r['arm'], r['case'], r['version']) for r in a['schedule'])
        self.assertEqual(set(combos.values()), {1})
        self.assertEqual({r['arm'] for r in a['schedule']}, {'baseline', 'rule'})
        self.assertFalse(set(a['cases']) & set(run.case_ids(run.B_SCENARIOS)))
        self.assertEqual(len(run.schedule('B', ('haiku',), run.ARMS_B, run.case_ids(run.B_SCENARIOS))), run.LIMITS['B']['calls'])
        self.assertEqual(a, run.plan_a())


class Simulation(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = dict(run.DECISION)
        run.DECISION.update(permutations=2000, bootstrap=1000)

    def tearDown(self):
        run.DECISION.clear()
        run.DECISION.update(self.saved)
        shutil.rmtree(self.tmp)

    def stage_a(self, policy):
        out = self.tmp / 'A'
        run.register(out, run.plan_a())
        run.collect(out, provider(policy))
        return out, run.verify(out, quiet=True)

    @staticmethod
    def haiku_rule_fails(target, arm, case, version):
        # Haiku misses trap versions of two scenarios in midas and wolf, under both arms.
        return not (target == 'haiku' and version == 'trap' and case in ('midas-01', 'midas-02', 'wolf-03', 'wolf-04'))

    def test_qualification_selection_and_decisive_stage(self):
        a_out, a = self.stage_a(self.haiku_rule_fails)
        self.assertEqual(a['selection']['target'], 'haiku')
        self.assertEqual(a['selection']['families'], ['midas', 'wolf'])
        self.assertEqual(a['targets']['sonnet']['qualifying_families'], [])
        self.assertEqual(a['story_calls'], 0)

        b_out = self.tmp / 'B'
        pb = run.plan_b(a_out)
        self.assertEqual(len(pb['schedule']), 2 * 6 * 2 * 4 * 3)
        run.register(b_out, pb)
        story_wins = lambda t, arm, c, v: arm == 'story' or v == 'twin' or c.endswith(('05', '06', '07'))
        run.collect(b_out, provider(story_wins))
        b = run.verify(b_out, quiet=True)
        self.assertEqual(b['verdict'], 'supported')
        self.assertGreater(b['primary']['mean_difference'], 0.4)

    def test_equal_arms_are_not_supported(self):
        a_out, _ = self.stage_a(self.haiku_rule_fails)
        b_out = self.tmp / 'B'
        run.register(b_out, run.plan_b(a_out))
        run.collect(b_out, provider(lambda t, arm, c, v: v == 'twin' or c.endswith(('05', '06', '07'))))
        b = run.verify(b_out, quiet=True)
        self.assertEqual(b['primary']['mean_difference'], 0)
        self.assertEqual(b['verdict'], 'not_supported')

    def test_over_refusing_story_is_not_supported_as_a_win(self):
        a_out, _ = self.stage_a(self.haiku_rule_fails)
        b_out = self.tmp / 'B'
        run.register(b_out, run.plan_b(a_out))
        # Story fixes traps but refuses a third of twins; rule misses half the traps.
        pol = lambda t, arm, c, v: (c.endswith(('05', '06')) if (arm == 'story' and v == 'twin')
                                    else arm == 'story' or v == 'twin' or c.endswith(('05', '06', '07')))
        run.collect(b_out, provider(pol))
        b = run.verify(b_out, quiet=True)
        self.assertFalse(b['story_twin_non_inferior'])
        self.assertNotEqual(b['verdict'], 'supported')

    def test_no_qualification_blocks_stage_b(self):
        a_out, a = self.stage_a(lambda *x: True)
        self.assertIsNone(a['selection'])
        with self.assertRaises(ValueError):
            run.plan_b(a_out)

    def test_tamper_and_resume_are_rejected(self):
        a_out, _ = self.stage_a(lambda *x: True)
        with self.assertRaises(ValueError):
            run.collect(a_out, provider(lambda *x: True))
        ep = a_out / 'episodes' / '0007' / 'episode.json'
        row = json.loads(ep.read_text(encoding='utf-8'))
        row['score']['outcome'] = 'wrong'
        ep.write_text(json.dumps(row), encoding='utf-8')
        with self.assertRaises(AssertionError):
            run.verify(a_out, quiet=True)

    def test_identity_mismatch_stops(self):
        out = self.tmp / 'A'
        run.register(out, run.plan_a())
        def bad(target, system, prompt, cap, timeout):
            raw = fake_raw(target, prompt, '<choice>A</choice>')
            raw['assistant_models'] = ['other-model']
            return raw
        run.collect(out, bad)
        s = run.verify(out, quiet=True)
        self.assertEqual(s['completion']['stop_reason'], 'transport_or_identity_error')
        self.assertEqual(s['completion']['calls'], 1)
        self.assertIsNone(s['selection'])


if __name__ == '__main__':
    unittest.main()
