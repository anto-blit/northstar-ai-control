#!/usr/bin/env python3
"""APE1: the APS2/APO1 task set re-run at the CLI's lowest reasoning effort.

Same 58 frozen requests, same system text, same scorer as APO1. The only
declared change is `model_reasoning_effort`: medium -> low. APO1 is closed and
is not rerun; this is a separately registered study with its own plan and output
directory.

Subcommands:
  verify     offline checks; no model calls
  register   write plan.json before any call
  run        execute the registered plan (makes model calls)
  report     rescore saved responses offline
"""
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
OUT = ROOT / 'results/authorization-pressure-loweffort'
CLAUDE_PLAN = ROOT / 'results/authorization-pressure-smoke-v2/plan.json'

MODEL = 'gpt-6-astra'
EFFORT = 'low'          # the whole point of this study
MAX_CALLS = 58
MAX_SECONDS = 720
MAX_CALL_SECONDS = 60
INPUT_TOKEN_STOP = 400000
OUTPUT_TOKEN_STOP = 40000


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


scoring = module('ape_scoring', 'experiments/authorization-pressure-smoke/v2.py')
transport = module('ape_transport', 'experiments/codex-repair/transport.py')
transport.HERE = HERE
transport.EFFORT = EFFORT          # medium -> low
assert transport.MODEL == MODEL, transport.MODEL


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
    paths = ['experiments/authorization-pressure-smoke/v2.py',
             'experiments/codex-repair/transport.py',
             'results/authorization-pressure-smoke-v2/plan.json',
             'experiments/authorization-pressure-loweffort/run.py',
             'experiments/authorization-pressure-loweffort/system.txt']
    return {p: digest(ROOT / p) for p in paths}


def requests():
    return read(CLAUDE_PLAN)['requests']


def operational(raw):
    usage = raw.get('usage') or {}
    return (raw.get('operational') is True and raw.get('returncode') == 0
            and raw.get('requested_model') == MODEL and raw.get('requested_effort') == EFFORT
            and raw.get('tool_or_unexpected_item') is False
            and isinstance(raw.get('thread_id_sha256'), str) and len(raw['thread_id_sha256']) == 64
            and all(type(usage.get(k)) is int and usage[k] >= 0
                    for k in ('input_tokens', 'output_tokens')))


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
        rows.append({'index': req['index'], 'id': c['id'], 'repeat': req['repeat'],
                     'arm': c['arm'], **out})
        pairs.setdefault((req['repeat'], c['domain'], c['level']), []).append(out['verdict'])
    usage = {k: sum((r['raw'].get('usage') or {}).get(k, 0) for r in records.values()
                    if type((r['raw'].get('usage') or {}).get(k, 0)) is int)
             for k in ('input_tokens', 'cached_input_tokens', 'output_tokens',
                       'reasoning_output_tokens')}
    zero_reasoning = sum(1 for r in records.values()
                         if ((r['raw'].get('usage') or {}).get('reasoning_output_tokens') or 0) == 0)
    return {'study': 'APE1', 'planned': len(rows), 'attempted_records': len(records),
            'requested_model': MODEL, 'requested_effort': EFFORT,
            'resolved_server_snapshot': None, 'dollar_cost': None,
            'counts': dict(Counter(r['verdict'] for r in rows)),
            'by_arm': {a: dict(Counter(r['verdict'] for r in rows if r['arm'] == a))
                       for a in ('trap', 'twin')},
            'joint_decision_pairs': {
                'correct': sum(v == ['CORRECT', 'CORRECT'] for v in pairs.values()),
                'planned': len(pairs),
                'complete': sum('MISSING' not in v and 'SERVICE_ERROR' not in v
                                for v in pairs.values())},
            'usage': usage, 'unique_threads': len(set(threads)),
            'calls_reporting_zero_reasoning_tokens': zero_reasoning,
            'action_review': 'separate qualitative endpoint; independent review outstanding',
            'observations': rows}


def verify():
    checks = []

    def check(name, ok, detail=''):
        checks.append({'check': name, 'ok': bool(ok), 'detail': detail})
        print(('PASS ' if ok else 'FAIL ') + name + (f'  [{detail}]' if detail else ''))

    rows = requests()
    system = (HERE / 'system.txt').read_text(encoding='utf-8')
    check('58 frozen APS2 requests loaded', len(rows) == 58, str(len(rows)))
    check('system text matches every request', all(r['system'] == system for r in rows))
    apo = ROOT / 'experiments/authorization-pressure-openai/system.txt'
    check('system text identical to APO1', apo.read_bytes() == (HERE / 'system.txt').read_bytes())
    options = transport.options(HERE / 'system.txt')
    check('transport requests low effort',
          '"low"' in ' '.join(options) and 'model_reasoning_effort="low"' in ' '.join(options))
    check('transport requests the declared model', MODEL in options)
    check('tools disabled for a decision-only study',
          any('features.shell_tool=false' in o for o in options)
          or any('shell_tool' in o and 'false' in o for o in options))
    check('scorer loaded', hasattr(scoring, 'score'))
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    check('CLI is codex-cli 0.154.0', version == 'codex-cli 0.154.0', version)
    check('output directory is not APO1', OUT.name == 'authorization-pressure-loweffort')
    ok = all(c['ok'] for c in checks)
    print('\nall offline checks passed' if ok else '\nOFFLINE CHECKS FAILED')
    return checks, ok


def register():
    checks, ok = verify()
    if not ok:
        raise SystemExit('offline checks failed; nothing registered')
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    save_new(OUT / 'plan.json', {
        'study': 'APE1', 'registered_at': now(),
        'question': 'Does the declared OpenAI target reproduce the APS2 authorization '
                    'failures when reasoning effort is dropped from medium to low?',
        'rationale': 'All 36 recorded Claude failures in the thinking analysis sit in '
                     'non-thinking calls (257/257 thinking calls correct). G16 targeted a '
                     'low-deliberation regime but observed no zero-reasoning calls. This '
                     'is the only OpenAI failure hypothesis with in-repo evidence behind it.',
        'model': MODEL, 'effort': EFFORT, 'cli_version': version,
        'changed_from_APO1': 'model_reasoning_effort only (medium -> low)',
        'maximum_calls': MAX_CALLS, 'maximum_seconds': MAX_SECONDS,
        'maximum_call_seconds': MAX_CALL_SECONDS,
        'input_token_stop': INPUT_TOKEN_STOP, 'output_token_stop': OUTPUT_TOKEN_STOP,
        'dollar_cost': None,
        'endpoints': ['structured decision per request',
                      'joint decision pairs (trap and twin both correct)',
                      'proposed-action review, preserved for separate adjudication',
                      'calls reporting zero reasoning tokens'],
        'stop_rules': ['planned call limit of 58',
                       'wall clock over 720 seconds',
                       'reported input tokens over 400000 or output tokens over 40000'],
        'not_authorized_by_this_plan': [
            'rerunning or amending APO1, APS2 or any frozen study',
            'story or other intervention arms',
            'treating any failure found here as a qualified baseline without '
            'a separate fixed replication batch'],
        'offline_checks': checks,
        'transport_options': transport.options(HERE / 'system.txt'),
        'source_sha256': hashes(), 'requests': requests()})
    print(f'\nRegistered {MAX_CALLS} requests at {MODEL}/{EFFORT} -> {OUT / "plan.json"}')


def checked_plan():
    plan = read(OUT / 'plan.json')
    if plan['source_sha256'] != hashes() or plan['requests'] != requests():
        raise ValueError('frozen source/request mismatch')
    if plan['transport_options'] != transport.options(HERE / 'system.txt'):
        raise ValueError('transport configuration changed')
    if plan['effort'] != EFFORT or plan['model'] != MODEL:
        raise ValueError('target changed since registration')
    return plan


def report(write=True):
    plan = read(OUT / 'plan.json')
    records = {int(p.stem): read(p) for p in (OUT / 'responses').glob('*.json')}
    result = summarize(plan, records)
    if write:
        (OUT / 'report.json').write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


def run():
    plan = checked_plan()
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    if version != plan['cli_version']:
        raise ValueError('CLI version changed')
    save_new(OUT / 'start.json', {'started_at': now(), 'plan_sha256': digest(OUT / 'plan.json')})
    (OUT / 'responses').mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    stop, totals = 'planned_call_limit', {'input_tokens': 0, 'output_tokens': 0}
    for req in plan['requests']:
        if time.monotonic() - start > MAX_SECONDS:
            stop = 'wall_clock_stop'
            break
        if totals['input_tokens'] > INPUT_TOKEN_STOP or totals['output_tokens'] > OUTPUT_TOKEN_STOP:
            stop = 'token_stop'
            break
        raw = transport.call(req['prompt'], timeout=MAX_CALL_SECONDS)
        save_new(OUT / 'responses' / f'{req["index"]:03}.json',
                 {'index': req['index'], 'id': req['case']['id'], 'raw': raw})
        usage = raw.get('usage') or {}
        for key in totals:
            if type(usage.get(key)) is int:
                totals[key] += usage[key]
        print(f'  {req["index"]:03} {req["case"]["id"]:<28} '
              f'op={raw.get("operational")} {raw.get("elapsed_seconds", 0):.1f}s')
    elapsed = round(time.monotonic() - start, 2)
    result = report()
    save_new(OUT / 'completion.json',
             {'finished_at': now(), 'elapsed_seconds': elapsed, 'stopped_because': stop,
              'counts': result['counts'], 'joint_decision_pairs': result['joint_decision_pairs'],
              'usage': result['usage'],
              'calls_reporting_zero_reasoning_tokens': result['calls_reporting_zero_reasoning_tokens']})
    print('\n' + json.dumps({'stopped_because': stop, 'elapsed_seconds': elapsed,
                             'counts': result['counts'],
                             'by_arm': result['by_arm'],
                             'joint_decision_pairs': result['joint_decision_pairs'],
                             'zero_reasoning_calls': result['calls_reporting_zero_reasoning_tokens']},
                            indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('verify', 'register', 'run', 'report'))
    command = parser.parse_args().command
    if command == 'verify':
        raise SystemExit(0 if verify()[1] else 1)
    if command == 'register':
        register()
    elif command == 'run':
        run()
    else:
        print(json.dumps(report(), indent=2)[:2000])
