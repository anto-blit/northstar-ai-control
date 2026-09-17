import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


run = load('apo_run', HERE / 'run.py')
packet = load('apo_packet', HERE / 'review_packet.py')


class OfflineChecks(unittest.TestCase):
    def test_same_prompts_system_and_schedule(self):
        requests = run.requests()
        self.assertEqual(len(requests), 58)
        self.assertTrue(all(r['system'] == (HERE / 'system.txt').read_text(encoding='utf-8') for r in requests))
        self.assertEqual(requests, run.read(run.CLAUDE_PLAN)['requests'])

    def test_empty_and_operational_failure_do_not_pass(self):
        p = {'requests': run.requests()}
        self.assertEqual(run.summarize(p, {})['counts'], {'MISSING': 58})
        r = run.summarize(p, {0: {'raw': {'operational': False}}})
        self.assertEqual(r['counts'], {'SERVICE_ERROR': 1, 'MISSING': 57})
        self.assertEqual(r['joint_decision_pairs']['correct'], 0)

    def test_complete_scoring_and_distinct_threads(self):
        records = {}
        for r in run.requests():
            c = r['case']
            answer = {'reasoning': 'Apply D1.', 'authority': {'status': c['correct_authority'], 'cites': c['authorizing_docs']},
                      'decision': c['correct_decision'], 'action': 'Follow the permission rule.'}
            records[r['index']] = {'raw': {'operational': True, 'returncode': 0,
                'requested_model': 'gpt-6-astra', 'requested_effort': 'medium', 'tool_or_unexpected_item': False,
                'thread_id_sha256': f'{r["index"]:064x}', 'usage': {'input_tokens': 100, 'output_tokens': 50},
                'result': json.dumps(answer)}}
        out = run.summarize({'requests': run.requests()}, records)
        self.assertEqual(out['counts'], {'CORRECT': 58})
        self.assertEqual(out['unique_threads'], 58)
        records[1]['raw']['thread_id_sha256'] = records[0]['raw']['thread_id_sha256']
        self.assertEqual(run.summarize({'requests': run.requests()}, records)['counts']['SERVICE_ERROR'], 1)

    def test_isolation_options_and_instruction_file(self):
        args = run.transport.options(HERE / 'system.txt')
        self.assertIn('--ephemeral', args)
        self.assertIn('--ignore-user-config', args)
        self.assertIn('project_doc_max_bytes=0', args)
        for setting in ('features.memories=false', 'features.shell_tool=false', 'features.multi_agent=false', 'mcp_servers={}'):
            self.assertIn(setting, args)
        self.assertEqual(run.transport.HERE, HERE)

    def test_transport_only_receives_prompt_not_labels(self):
        with patch.object(run.transport.subprocess, 'run') as mocked:
            mocked.return_value.stdout = ''
            mocked.return_value.stderr = ''
            mocked.return_value.returncode = 1
            req = run.requests()[0]
            run.transport.call(req['prompt'], timeout=1)
            kwargs = mocked.call_args.kwargs
            self.assertEqual(kwargs['input'], req['prompt'])
            self.assertFalse(Path(kwargs['cwd']).is_relative_to(run.ROOT))
            self.assertNotIn('correct_decision', kwargs['input'])
            self.assertNotIn('candidate-016', kwargs['input'])

    def test_masked_packet_separates_identity(self):
        req = run.requests()[0]
        rows, mapping = packet.build([('provider-secret', [req], {0: {'raw': {'result': 'answer'}}})])
        self.assertEqual(set(rows[0]), {'review_id', 'system', 'prompt', 'response'})
        self.assertNotIn('provider-secret', json.dumps(rows))
        self.assertEqual(mapping[0]['dataset'], 'provider-secret')
        self.assertEqual(rows[0]['review_id'], mapping[0]['review_id'])


if __name__ == '__main__': unittest.main()
