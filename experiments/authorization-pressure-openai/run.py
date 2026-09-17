"""One-shot OpenAI replication of APS2; no study results enter model context."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'results/authorization-pressure-openai'
CLAUDE_PLAN = ROOT / 'results/authorization-pressure-smoke-v2/plan.json'


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


scoring = module('apo_scoring', 'experiments/authorization-pressure-smoke/v2.py')
transport = module('apo_transport', 'experiments/codex-repair/transport.py')
transport.HERE = HERE


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def hashes():
    paths = ['experiments/authorization-pressure-smoke/run.py',
             'experiments/authorization-pressure-smoke/v2.py',
             'experiments/codex-repair/transport.py',
             'results/authorization-pressure-smoke-v2/plan.json',
             'protocol/authorization-pressure-process.md']
    paths += ['experiments/authorization-pressure-openai/' + p for p in
              ('run.py', 'system.txt', 'PROTOCOL.md', 'README.md', 'test_run.py', 'review_packet.py')]
    return {p: digest(ROOT / p) for p in paths}


def requests():
    return read(CLAUDE_PLAN)['requests']


def operational(raw):
    usage = raw.get('usage') or {}
    return (raw.get('operational') is True and raw.get('returncode') == 0
            and raw.get('requested_model') == 'gpt-6-astra' and raw.get('requested_effort') == 'medium'
            and raw.get('tool_or_unexpected_item') is False
            and isinstance(raw.get('thread_id_sha256'), str) and len(raw['thread_id_sha256']) == 64
            and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens')))


def summarize(plan, records):
    rows, pairs, threads = [], {}, []
    for req in plan['requests']:
        record = records.get(req['index'])
        if record is None:
            out = {'verdict': 'MISSING'}
        elif not operational(record['raw']):
            out = {'verdict': 'SERVICE_ERROR'}
        else:
            raw = record['raw']
            if raw['thread_id_sha256'] in threads:
                out = {'verdict': 'SERVICE_ERROR', 'note': 'duplicate thread'}
            else:
                out = scoring.score(req['case'], raw.get('result', ''))
            threads.append(raw['thread_id_sha256'])
        c = req['case']
        rows.append({'index': req['index'], 'id': c['id'], 'repeat': req['repeat'], 'arm': c['arm'], **out})
        pairs.setdefault((req['repeat'], c['domain'], c['level']), []).append(out['verdict'])
    usage = {k: sum((r['raw'].get('usage') or {}).get(k, 0) for r in records.values()
                    if type((r['raw'].get('usage') or {}).get(k, 0)) is int)
             for k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')}
    return {'planned': len(rows), 'attempted_records': len(records), 'requested_model': 'gpt-6-astra',
            'requested_effort': 'medium', 'resolved_server_snapshot': None, 'dollar_cost': None,
            'counts': dict(Counter(r['verdict'] for r in rows)),
            'by_arm': {a: dict(Counter(r['verdict'] for r in rows if r['arm'] == a)) for a in ('trap', 'twin')},
            'joint_decision_pairs': {'correct': sum(v == ['CORRECT', 'CORRECT'] for v in pairs.values()),
                                     'planned': len(pairs),
                                     'complete': sum('MISSING' not in v and 'SERVICE_ERROR' not in v for v in pairs.values())},
            'usage': usage, 'unique_threads': len(set(threads)),
            'action_review': 'separate qualitative endpoint; independent review outstanding', 'observations': rows}


def report(write=True):
    plan = read(OUT / 'plan.json')
    records = {int(p.stem): read(p) for p in (OUT / 'responses').glob('*.json')}
    result = summarize(plan, records)
    if write:
        (OUT / 'report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


def register():
    rows = requests()
    system = (HERE / 'system.txt').read_text(encoding='utf-8')
    assert len(rows) == 58 and all(r['system'] == system for r in rows)
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    assert version == 'codex-cli 0.154.0'
    save_new(OUT / 'plan.json', {'registered_at': now(), 'registration': 'shared workspace before calls',
             'model': 'gpt-6-astra', 'effort': 'medium', 'cli_version': version,
             'maximum_calls': 58, 'maximum_seconds': 540, 'maximum_call_seconds': 60,
             'input_token_stop': 400000, 'output_token_stop': 40000, 'dollar_cost': None,
             'transport_options': transport.options(HERE / 'system.txt'),
             'source_sha256': hashes(), 'requests': rows})
    print('Registered 58 isolated OpenAI requests and 29 pairs; no model calls.')


def checked_plan():
    plan = read(OUT / 'plan.json')
    if plan['source_sha256'] != hashes() or plan['requests'] != requests():
        raise ValueError('frozen source/request mismatch')
    if plan['transport_options'] != transport.options(HERE / 'system.txt'):
        raise ValueError('transport configuration changed')
    return plan


def run():
    plan = checked_plan()
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    if version != plan['cli_version']:
        raise ValueError('CLI version changed')
    save_new(OUT / 'start.json', {'started_at': now(), 'plan_sha256': digest(OUT / 'plan.json')})
    start = time.monotonic()
    stop = 'planned_call_limit'
    threads = set()
    try:
        for req in plan['requests']:
            remaining = plan['maximum_seconds'] - (time.monotonic() - start)
            if remaining < 5:
                stop = 'wall_clock_limit'
                break
            i = req['index']
            save_new(OUT / 'reservations' / f'{i:03}.json', {'reserved_at': now(), 'index': i,
                     'prompt_sha256': hashlib.sha256(req['prompt'].encode()).hexdigest()})
            try:
                raw = transport.call(req['prompt'], timeout=min(plan['maximum_call_seconds'], remaining))
            except Exception as exc:
                raw = {'operational': False, 'result': '', 'usage': None,
                       'error': type(exc).__name__ + ': transport failed; usage unknown'}
            save_new(OUT / 'responses' / f'{i:03}.json', {'index': i, 'raw': raw})
            result = report()
            print(json.dumps({'completed': i + 1, 'id': req['case']['id'], 'repeat': req['repeat'],
                              'verdict': result['observations'][i]['verdict'], 'usage': result['usage'],
                              'elapsed_seconds': round(time.monotonic() - start, 1)}), flush=True)
            if not operational(raw):
                stop = 'operational_stop'
                break
            if raw['thread_id_sha256'] in threads:
                stop = 'duplicate_thread'
                break
            threads.add(raw['thread_id_sha256'])
            if (result['usage']['input_tokens'] >= plan['input_token_stop']
                    or result['usage']['output_tokens'] >= plan['output_token_stop']):
                stop = 'token_stop'
                break
    except KeyboardInterrupt:
        stop = 'interrupted'
    except Exception as exc:
        stop = 'runner_error: ' + type(exc).__name__ + ': ' + str(exc)
    finally:
        save_new(OUT / 'completion.json', {'completed_at': now(), 'stop_reason': stop,
                                         'elapsed_seconds': time.monotonic() - start})
        result = report()
        print(json.dumps({k: v for k, v in result.items() if k != 'observations'}), flush=True)


def verify():
    plan = checked_plan()
    expected = report(write=False)
    assert expected == read(OUT / 'report.json')
    files = sorted((OUT / 'responses').glob('*.json'))
    assert len(files) == len(list((OUT / 'reservations').glob('*.json')))
    for i, path in enumerate(files):
        assert path.stem == f'{i:03}'
        rec = read(path)
        assert rec['index'] == i
        raw = rec['raw']
        if operational(raw):
            req = plan['requests'][i]
            assert raw['prompt'] == req['prompt']
            assert raw['system_sha256'] == digest(HERE / 'system.txt')
            assert raw['prompt_sha256'] == hashlib.sha256(req['prompt'].encode()).hexdigest()
    print(json.dumps({k: v for k, v in expected.items() if k != 'observations'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('register', 'run', 'report', 'verify'))
    command = parser.parse_args().command
    if command == 'register': register()
    elif command == 'run': run()
    elif command == 'verify': verify()
    else: print(json.dumps(report(), indent=2))
