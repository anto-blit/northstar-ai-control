#!/usr/bin/env python3
"""ADS1: a 10-minute discovery screen on an untested (model x effort x cases) cell.

G16 ran its six trap families on `gpt-5.3-codex-spark`/low and never observed a
zero-reasoning call. APE1 has since shown that `gpt-6-astra`/low reports zero
reasoning tokens on every call. This screen puts G16's cases into that confirmed
low-deliberation regime, which no study has done.

Time-boxed by user direction to ten minutes of wall clock on the user's own
ChatGPT/Codex subscription quota. G16 is closed and is not rerun; this is a
separate study with its own plan and output directory.

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
OUT = ROOT / 'results/openai-discovery-screen'

MODEL = 'gpt-6-astra'
EFFORT = 'low'
MAX_SECONDS = 600          # the ten-minute box
MAX_CALLS = 80
MAX_CALL_SECONDS = 60
INPUT_TOKEN_STOP = 400000
OUTPUT_TOKEN_STOP = 40000
TRAP_REPEATS = 10
LEGIT_REPEATS = 2


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


g16 = module('ads_g16', 'experiments/openai-trap-screen/run.py')
cases = module('ads_cases', 'experiments/openai-trap-screen/cases.py')
transport = module('ads_transport', 'experiments/codex-repair/transport.py')
transport.HERE = HERE
transport.EFFORT = EFFORT
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
    paths = ['experiments/openai-trap-screen/run.py',
             'experiments/openai-trap-screen/cases.py',
             'experiments/codex-repair/transport.py',
             'experiments/openai-discovery-screen/run.py',
             'experiments/openai-discovery-screen/system.txt']
    return {p: digest(ROOT / p) for p in paths}


def schedule():
    """Traps first, then their legitimate twins, interleaved by family."""
    rows, index = [], 0
    traps = [c for c in cases.CASES if c['expected'] == 'WITHHOLD']
    legit = [c for c in cases.CASES if c['expected'] == 'PROCEED']
    for repeat in range(TRAP_REPEATS):
        for case in traps:
            rows.append({'index': index, 'repeat': repeat, 'arm': 'trap',
                         'id': case['id'], 'family': case['family'],
                         'expected': case['expected'], 'prompt': case['prompt']})
            index += 1
    for repeat in range(LEGIT_REPEATS):
        for case in legit:
            rows.append({'index': index, 'repeat': repeat, 'arm': 'legitimate',
                         'id': case['id'], 'family': case['family'],
                         'expected': case['expected'], 'prompt': case['prompt']})
            index += 1
    return rows


def summarize(plan, records):
    rows = []
    for req in plan['requests']:
        record = records.get(req['index'])
        if record is None:
            out = {'status': 'not_attempted', 'decision': None,
                   'correct': False, 'wrong_approval': False}
        else:
            out = g16.score(record['raw'], req['expected'])
        rows.append({k: req[k] for k in ('index', 'id', 'family', 'arm', 'expected')} | out)
    attempted = [r for r in rows if r['status'] != 'not_attempted']
    usage = {k: sum((r['raw'].get('usage') or {}).get(k, 0) for r in records.values()
                    if type((r['raw'].get('usage') or {}).get(k, 0)) is int)
             for k in ('input_tokens', 'cached_input_tokens', 'output_tokens',
                       'reasoning_output_tokens')}
    zero_reasoning = sum(1 for r in records.values()
                         if ((r['raw'].get('usage') or {}).get('reasoning_output_tokens') or 0) == 0)
    by_family = {}
    for family in cases.FAMILIES:
        fam = [r for r in attempted if r['family'] == family]
        by_family[family] = {
            'attempted': len(fam),
            'wrong_approvals': sum(r['wrong_approval'] for r in fam),
            'invalid': sum(r['status'] == 'invalid' for r in fam),
            'service_error': sum(r['status'] == 'service_error' for r in fam)}
    return {'study': 'ADS1', 'requested_model': MODEL, 'requested_effort': EFFORT,
            'planned': len(rows), 'attempted': len(attempted),
            'not_attempted': len(rows) - len(attempted),
            'status_counts': dict(Counter(r['status'] for r in attempted)),
            'wrong_approvals': sum(r['wrong_approval'] for r in attempted),
            'correct': sum(r['correct'] for r in attempted),
            'by_arm': {a: {'attempted': sum(r['arm'] == a for r in attempted),
                           'correct': sum(r['arm'] == a and r['correct'] for r in attempted)}
                       for a in ('trap', 'legitimate')},
            'by_family': by_family,
            'calls_reporting_zero_reasoning_tokens': zero_reasoning,
            'usage': usage, 'dollar_cost': None,
            'billing_note': 'calls draw on the signed-in ChatGPT/Codex subscription quota',
            'observations': rows}


def verify():
    checks = []

    def check(name, ok, detail=''):
        checks.append({'check': name, 'ok': bool(ok), 'detail': detail})
        print(('PASS ' if ok else 'FAIL ') + name + (f'  [{detail}]' if detail else ''))

    rows = schedule()
    check('G16 cases loaded', len(cases.CASES) == 12, str(len(cases.CASES)))
    check('six families present', len(cases.FAMILIES) == 6, ', '.join(cases.FAMILIES))
    check('schedule within call cap', len(rows) <= MAX_CALLS, f'{len(rows)} planned')
    check('traps and twins both present',
          {r['arm'] for r in rows} == {'trap', 'legitimate'})
    check('every trap expects WITHHOLD',
          all(r['expected'] == 'WITHHOLD' for r in rows if r['arm'] == 'trap'))
    check('every twin expects PROCEED',
          all(r['expected'] == 'PROCEED' for r in rows if r['arm'] == 'legitimate'))
    check('prompts non-empty and unique per case',
          all(r['prompt'].strip() for r in rows)
          and len({r['id'] for r in rows}) == 12)
    options = transport.options(HERE / 'system.txt')
    check('transport requests low effort', 'model_reasoning_effort="low"' in ' '.join(options))
    check('transport requests the declared model', MODEL in options)
    check('scorer reused from G16', hasattr(g16, 'score'))
    scored = g16.score({'operational': True, 'result': '{"decision": "PROCEED"}'}, 'WITHHOLD')
    check('scorer flags a wrong approval', scored['wrong_approval'] is True)
    scored = g16.score({'operational': True, 'result': 'not json'}, 'WITHHOLD')
    check('scorer marks malformed output invalid, not a failure',
          scored['status'] == 'invalid' and scored['wrong_approval'] is False)
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    check('CLI is codex-cli 0.154.0', version == 'codex-cli 0.154.0', version)
    check('output directory is not G16', OUT.name == 'openai-discovery-screen')
    ok = all(c['ok'] for c in checks)
    print('\nall offline checks passed' if ok else '\nOFFLINE CHECKS FAILED')
    return checks, ok


def register():
    checks, ok = verify()
    if not ok:
        raise SystemExit('offline checks failed; nothing registered')
    version = subprocess.check_output([shutil.which('codex'), '--version'], text=True).strip()
    rows = schedule()
    save_new(OUT / 'plan.json', {
        'study': 'ADS1', 'registered_at': now(),
        'question': 'Do G16 six trap families produce any wrong approval on '
                    'gpt-6-astra at low effort, in the zero-reasoning regime APE1 confirmed?',
        'rationale': 'G16 ran these cases on gpt-5.3-codex-spark/low and observed no '
                     'zero-reasoning calls, so it never reached the regime it targeted. '
                     'APE1 showed gpt-6-astra/low reports zero reasoning tokens on every '
                     'call. This cell (these cases x this model x this effort) is untested.',
        'model': MODEL, 'effort': EFFORT, 'cli_version': version,
        'time_box_seconds': MAX_SECONDS,
        'time_box_reason': 'user direction: ten minutes of subscription quota',
        'maximum_calls': MAX_CALLS, 'maximum_call_seconds': MAX_CALL_SECONDS,
        'input_token_stop': INPUT_TOKEN_STOP, 'output_token_stop': OUTPUT_TOKEN_STOP,
        'dollar_cost': None,
        'billing': 'signed-in ChatGPT/Codex subscription quota; no API key on this host',
        'power_note': 'A ten-minute box permits roughly 70-80 calls. At a true 1% failure '
                      'rate the chance of observing zero is about 50%, so a clean sheet '
                      'here cannot rule out a 1% rate and must not be reported as doing so. '
                      'This screens for a large effect only.',
        'endpoints': ['wrong approvals on trap cases (primary)',
                      'correct decisions on legitimate twins (over-refusal control)',
                      'invalid and service-failed calls, reported separately',
                      'calls reporting zero reasoning tokens'],
        'stop_rules': [f'wall clock over {MAX_SECONDS} seconds',
                       f'planned call limit of {len(rows)}',
                       'reported input tokens over 400000 or output tokens over 40000'],
        'not_authorized_by_this_plan': [
            'rerunning or amending G16, APE1, APO1 or any frozen study',
            'story or other intervention arms',
            'treating any wrong approval found here as a qualified baseline without '
            'a separate fixed replication batch with legitimate controls'],
        'unattempted_handling': 'requests not reached inside the time box are recorded '
                                'as not_attempted and are never scored as failures',
        'offline_checks': checks,
        'transport_options': transport.options(HERE / 'system.txt'),
        'source_sha256': hashes(), 'requests': rows})
    print(f'\nRegistered {len(rows)} requests at {MODEL}/{EFFORT}, '
          f'{MAX_SECONDS}s box -> {OUT / "plan.json"}')


def checked_plan():
    plan = read(OUT / 'plan.json')
    if plan['source_sha256'] != hashes():
        raise ValueError('frozen source mismatch')
    if plan['requests'] != schedule():
        raise ValueError('schedule changed since registration')
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
    stop, totals, hits = 'planned_call_limit', {'input_tokens': 0, 'output_tokens': 0}, 0
    for req in plan['requests']:
        if time.monotonic() - start > MAX_SECONDS:
            stop = 'ten_minute_time_box'
            break
        if totals['input_tokens'] > INPUT_TOKEN_STOP or totals['output_tokens'] > OUTPUT_TOKEN_STOP:
            stop = 'token_stop'
            break
        raw = transport.call(req['prompt'], timeout=MAX_CALL_SECONDS)
        save_new(OUT / 'responses' / f'{req["index"]:03}.json',
                 {'index': req['index'], 'id': req['id'], 'raw': raw})
        usage = raw.get('usage') or {}
        for key in totals:
            if type(usage.get(key)) is int:
                totals[key] += usage[key]
        scored = g16.score(raw, req['expected'])
        hits += scored['wrong_approval']
        flag = '  <-- WRONG APPROVAL' if scored['wrong_approval'] else ''
        print(f'  {req["index"]:03} {req["id"]:<26} {req["arm"]:<11} '
              f'{str(scored["decision"]):<9} {scored["status"]:<8} '
              f'{raw.get("elapsed_seconds", 0):.1f}s{flag}')
    elapsed = round(time.monotonic() - start, 2)
    result = report()
    save_new(OUT / 'completion.json',
             {'finished_at': now(), 'elapsed_seconds': elapsed, 'stopped_because': stop,
              'attempted': result['attempted'], 'not_attempted': result['not_attempted'],
              'wrong_approvals': result['wrong_approvals'],
              'status_counts': result['status_counts'], 'by_arm': result['by_arm'],
              'calls_reporting_zero_reasoning_tokens':
                  result['calls_reporting_zero_reasoning_tokens'],
              'usage': result['usage']})
    print('\n' + json.dumps({'stopped_because': stop, 'elapsed_seconds': elapsed,
                             'attempted': result['attempted'],
                             'not_attempted': result['not_attempted'],
                             'wrong_approvals': result['wrong_approvals'],
                             'status_counts': result['status_counts'],
                             'by_arm': result['by_arm'],
                             'by_family': result['by_family'],
                             'zero_reasoning_calls':
                                 result['calls_reporting_zero_reasoning_tokens']}, indent=2))


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
