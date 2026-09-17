"""Corrected accounting/parser, separately registered; original APS1 preserved."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
import time

spec = importlib.util.spec_from_file_location('aps1_frozen', Path(__file__).with_name('run.py'))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
OLD_OUT = base.OUT
base.OUT = base.ROOT / 'results/authorization-pressure-smoke-v2'
original_hashes, original_requests, original_score = base.hashes, base.requests, base.score


def hashes():
    found = original_hashes()
    for p in ('experiments/authorization-pressure-smoke/v2.py',
              'experiments/authorization-pressure-smoke/V2-PROTOCOL.md',
              'experiments/authorization-pressure-smoke/test_v2.py',
              'results/authorization-pressure-smoke/plan.json',
              'results/authorization-pressure-smoke/start.json',
              'results/authorization-pressure-smoke/completion.json',
              'results/authorization-pressure-smoke/responses/000.json'):
        found[p] = hashlib.sha256((base.ROOT / p).read_bytes()).hexdigest()
    return found


def requests():
    return original_requests()[:58]


def score(case, raw):
    raw = raw.strip() if isinstance(raw, str) else raw
    match = re.fullmatch(r'```(?:json)?\s*\n(.*?)\n```', raw, flags=re.S) if isinstance(raw, str) else None
    result = original_score(case, match.group(1) if match else raw)
    result['bare_json_format'] = match is None
    return result


def operational(raw):
    keys = set(raw.get('modelUsage') or {})
    cost = raw.get('total_cost_usd')
    return (raw.get('is_error') is False and raw.get('returncode') == 0
            and 'claude-sonnet-5' in keys
            and keys <= {'claude-sonnet-5', 'claude-haiku-4-5-20251001'}
            and raw.get('num_turns') == 1
            and type(cost) in (int, float) and math.isfinite(cost) and cost >= 0)


base.hashes, base.requests, base.score, base.operational = hashes, requests, score, operational


def prior():
    rows = [base.read(p)['raw'] for p in (OLD_OUT / 'responses').glob('*.json')]
    return len(list((OLD_OUT / 'reservations').glob('*.json'))), sum(r['total_cost_usd'] for r in rows)


def remaining_seconds():
    start = datetime.fromisoformat(base.read(OLD_OUT / 'start.json')['started_at'])
    return max(0, 540 - (datetime.now(timezone.utc) - start).total_seconds())


def register():
    n, spent = prior()
    base.save_new(base.OUT / 'plan.json', {
        'registered_at': base.now(), 'registration': 'shared workspace before APS2 calls',
        'model': 'claude-sonnet-5', 'effort': 'medium', 'cli_version': '2.1.270',
        'allowed_helper': 'claude-haiku-4-5-20251001', 'maximum_calls': 58,
        'combined_maximum_calls': 60, 'combined_maximum_seconds': 540,
        'combined_maximum_reported_usd': 3, 'prior_calls': n, 'prior_reported_usd': spent,
        'maximum_reported_usd': 3 - spent, 'per_call_budget_usd': 0.10,
        'maximum_call_seconds': 60, 'source_sha256': hashes(), 'requests': requests()})
    print('APS2 registered; ' + str(round(remaining_seconds(), 1)) + ' seconds remain in original window.')


def run():
    plan = base.read(base.OUT / 'plan.json')
    if plan['source_sha256'] != hashes() or plan['requests'] != requests():
        raise ValueError('registered sources changed')
    base.save_new(base.OUT / 'start.json', {'started_at': base.now(),
                  'plan_sha256': hashlib.sha256((base.OUT / 'plan.json').read_bytes()).hexdigest()})
    transport = base.module('aps2_transport', 'experiments/guidance-pilot/model_io.py')
    start = time.monotonic()
    spent = 0.0
    stop = 'planned_call_limit'
    try:
        for req in plan['requests']:
            remaining = remaining_seconds()
            if remaining < 5:
                stop = 'combined_wall_clock_limit'
                break
            if spent + 0.10 > plan['maximum_reported_usd']:
                stop = 'combined_usage_limit'
                break
            i = req['index']
            if i + plan['prior_calls'] >= plan['combined_maximum_calls']:
                stop = 'combined_call_limit'
                break
            base.save_new(base.OUT / 'reservations' / f'{i:03}.json', {'reserved_at': base.now(),
                          'index': i, 'case_id': req['case']['id'], 'repeat': req['repeat']})
            raw = transport.call(req['prompt'], system=req['system'], budget='0.10', timeout=min(60, remaining))
            base.save_new(base.OUT / 'responses' / f'{i:03}.json', {'index': i, 'raw': raw})
            report = base.report()
            print(json.dumps({'completed': i + 1, 'id': req['case']['id'], 'repeat': req['repeat'],
                              'verdict': report['observations'][i]['verdict'],
                              'reported_usd': report['known_reported_usd'],
                              'remaining_seconds': round(remaining_seconds(), 1)}), flush=True)
            if not operational(raw):
                stop = 'operational_or_identity_or_usage_error'
                break
            spent += raw['total_cost_usd']
    except KeyboardInterrupt:
        stop = 'interrupted'
    except Exception as exc:
        stop = 'runner_error: ' + type(exc).__name__ + ': ' + str(exc)
    finally:
        base.save_new(base.OUT / 'completion.json', {'completed_at': base.now(), 'stop_reason': stop,
                      'elapsed_seconds': time.monotonic() - start,
                      'combined_elapsed_seconds': 540 - remaining_seconds()})
        result = base.report()
        print(json.dumps({k: v for k, v in result.items() if k != 'observations'}), flush=True)


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'register': register()
    elif command == 'run': run()
    elif command == 'report':
        print(json.dumps({k: v for k, v in base.report().items() if k != 'observations'}, indent=2))
    else: raise SystemExit('Expected register, run, or report')
