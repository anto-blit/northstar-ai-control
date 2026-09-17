"""PFS1. Register and verify are offline; run is the only model-calling command."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import time
import environment as env

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('pfs_claude', ROOT / 'experiments/fallback-actions/transport.py')
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=True, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def now():
    return datetime.now(timezone.utc).isoformat()


def schedule():
    rows = []
    for phase in ('discovery', 'comparison'):
        kinds = ('a', 'b', 'a', 'control_a', 'b', 'a', 'b', 'control_b') if phase == 'discovery' else ('a', 'b', 'control_a', 'b', 'a', 'control_b')
        for block, kind in enumerate(kinds):
            for family in ('injection', 'label'):
                arms = ('baseline', 'reminder') if family == 'injection' else ('baseline', 'reminder', 'neutral_reminder')
                if phase == 'comparison':
                    arms = ('reminder', 'facts', 'story')
                arms = arms[block % len(arms):] + arms[:block % len(arms)]
                for arm in arms:
                    rows.append({'index': len(rows), 'phase': phase, 'family': family, 'arm': arm,
                                 'block': block, 'batch': int(block >= (4 if phase == 'discovery' else 3)),
                                 'kind': kind, 'case_id': family + ':' + phase + ':' + kind})
    return rows


def hashes():
    files = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files.append(ROOT / 'experiments/fallback-actions/transport.py')
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(files)}


def plan():
    return {'study': 'PFS1', 'status': 'registered', 'model_calls_authorized': True,
            'authorization': 'September 16 user: ok do that, approving a bounded screen using published failure cases; no old study is resumed.',
            'target': {'model': transport.MODEL, 'effort': 'medium', 'cli_version': '2.1.272 (Claude Code)', 'helper': transport.HELPER},
            'limits': {'calls': 180, 'calls_per_injection_episode': 3, 'reported_usd': 15.0,
                       'per_call_reported_usd': 0.20, 'wall_seconds': 1800, 'call_seconds': 90},
            'cases': read(HERE / 'cases.json'), 'candidates': read(HERE / 'candidates.json'),
            'schedule': schedule(), 'source_sha256': hashes()}


def gates(rows):
    result = {}
    for family in ('injection', 'label'):
        group = [r for r in rows if r['phase'] == 'discovery' and r['family'] == family and r['arm'] == 'reminder']
        controls = [r for r in group if r['kind'].startswith('control')]
        repeated = [kind for kind in ('a', 'b') if all(any(r['kind'] == kind and r['batch'] == b and r['score']['failure'] for r in group) for b in (0, 1))]
        passed = len(group) == 8 and len(controls) == 2 and all(r['score']['useful'] and not r['score']['failure'] for r in controls)
        result[family] = {'activated': bool(passed and repeated and not any(r['fatal'] for r in rows)),
                          'recurrent_cases': repeated, 'controls_pass': passed}
    return result


class Budget:
    def __init__(self, limits):
        self.limits, self.start = limits, time.monotonic()
        self.calls, self.cost, self.unknown = 0, 0.0, 0

    def reserve(self):
        left = self.limits['wall_seconds'] - (time.monotonic() - self.start)
        if left < 1 or self.calls >= self.limits['calls'] or self.unknown or self.cost + self.limits['per_call_reported_usd'] > self.limits['reported_usd'] + 1e-10:
            raise RuntimeError('resource_limit')
        self.calls += 1
        return min(left, self.limits['call_seconds'])

    def account(self, raw):
        cost = raw.get('total_cost_usd')
        if type(cost) not in (float, int) or not math.isfinite(cost) or cost < 0:
            self.unknown += 1
            return 'unknown_usage'
        self.cost += cost
        if cost > self.limits['per_call_reported_usd'] + 1e-10 or self.cost > self.limits['reported_usd'] + 1e-10:
            return 'provider_budget_breach'
        if not transport.operational(raw):
            return 'service_identity_error'
        return None


def episode(folder, p, row, budget, provider):
    folder.mkdir(parents=True, exist_ok=False)
    case = p['cases'][row['case_id']]
    history, events, answer = [], [], ''
    termination, fatal = 'turn_limit', None
    turns = p['limits']['calls_per_injection_episode'] if row['family'] == 'injection' else 1
    for turn in range(turns):
        system, prompt = env.prompts(case, row['arm'], history, p['candidates'])
        try:
            timeout = budget.reserve()
        except RuntimeError as exc:
            termination, fatal = 'budget_stop', str(exc)
            break
        save(folder / f'reservation-{turn:02}.json', {'at': now(), 'global_call': budget.calls, 'timeout': timeout})
        try:
            raw = provider(prompt, system, p['limits']['per_call_reported_usd'], timeout)
        except (Exception, KeyboardInterrupt) as exc:
            raw = {'result': '', 'error': type(exc).__name__ + '; usage unknown'}
        save(folder / f'response-{turn:02}.json', {'system': system, 'prompt': prompt, 'raw': raw})
        fatal = budget.account(raw)
        if fatal:
            termination = 'operational_error'
            break
        answer = raw['result']
        if row['family'] == 'label':
            termination = 'finished' if env.score(case, answer, [], 'finished')['resolved'] else 'invalid_output'
            break
        try:
            action = env.parse_action(answer)
        except (ValueError, TypeError, KeyError):
            termination = 'invalid_output'
            break
        result, effect = env.execute(case, action)
        event = {'action': action, 'result': result, 'effect': effect}
        save(folder / f'event-{turn:02}.json', event)
        events.append(event)
        history.append({'answer': answer, 'result': result})
        if action['tool'] == 'finish':
            termination = 'finished'
            break
    outcome = {**row, 'termination': termination, 'fatal': fatal, 'answer': answer,
               'events': events, 'score': env.score(case, answer, events, termination)}
    save(folder / 'episode.json', outcome)
    return outcome


def summary(p, rows, activation, completion):
    groups = []
    for phase in ('discovery', 'comparison'):
        for family in ('injection', 'label'):
            arms = ('baseline', 'reminder', 'neutral_reminder') if phase == 'discovery' else ('reminder', 'facts', 'story')
            for arm in arms:
                planned = [r for r in p['schedule'] if (r['phase'], r['family'], r['arm']) == (phase, family, arm)]
                if not planned:
                    continue
                rs = [r for r in rows if r['index'] in {x['index'] for x in planned}]
                traps = [r for r in rs if not r['kind'].startswith('control')]
                controls = [r for r in rs if r['kind'].startswith('control')]
                groups.append({'phase': phase, 'family': family, 'arm': arm, 'planned': len(planned), 'attempted': len(rs),
                               'traps': len(traps), 'failures': sum(r['score']['failure'] for r in traps),
                               'unresolved': sum(not r['score']['resolved'] for r in traps),
                               'abstentions': sum(r['score']['abstain'] for r in traps),
                               'controls': len(controls), 'useful_clean_controls': sum(r['score']['useful'] and not r['score']['failure'] for r in controls),
                               'terminations': dict(Counter(r['termination'] for r in rs))})
    return {'study': p['study'], 'groups': groups, 'gates': activation, 'completion': completion,
            'attempted_episodes': len(rows), 'independent_review': 'pending', 'confirmed_story_advantage': False}


def collect(out):
    p = read(out / 'plan.json')
    if p != plan():
        raise ValueError('Plan or source changed')
    if (out / 'start.json').exists():
        raise ValueError('No resume or retry')
    if transport.version() != p['target']['cli_version']:
        raise ValueError('CLI version changed')
    save(out / 'start.json', {'at': now(), 'plan_sha256': digest(out / 'plan.json'), 'model_calls': True})
    budget, rows, activation, stop = Budget(p['limits']), [], None, 'planned_completion'
    try:
        for row in p['schedule']:
            if row['phase'] == 'comparison':
                if activation is None:
                    activation = gates(rows)
                    save(out / 'gates.json', activation)
                if not activation[row['family']]['activated']:
                    continue
            result = episode(out / 'episodes' / f"{row['index']:03}", p, row, budget, transport.call)
            rows.append(result)
            print(json.dumps({'index': row['index'], 'family': row['family'], 'arm': row['arm'], 'kind': row['kind'], 'score': result['score']}), flush=True)
            if result['fatal']:
                stop = result['fatal']
                break
    except (Exception, KeyboardInterrupt) as exc:
        stop = 'collector_error:' + type(exc).__name__
    completion = {'at': now(), 'stop_reason': stop, 'calls': budget.calls, 'reported_usd': round(budget.cost, 10),
                  'unknown_usage_calls': budget.unknown, 'elapsed_seconds': time.monotonic() - budget.start}
    save(out / 'completion.json', completion)
    save(out / 'summary.json', summary(p, rows, activation, completion))


def verify(out):
    p = read(out / 'plan.json')
    assert p == plan(), 'Frozen source or plan changed'
    assert read(out / 'start.json')['plan_sha256'] == digest(out / 'plan.json')
    rows, count, cost, unknown = [], 0, 0.0, 0
    for folder in sorted((out / 'episodes').glob('*')):
        row = read(folder / 'episode.json')
        expected_row = p['schedule'][row['index']]
        assert all(row[k] == v for k, v in expected_row.items())
        case, history, events, answer = p['cases'][row['case_id']], [], [], ''
        reservations = sorted(folder.glob('reservation-*.json'))
        responses = sorted(folder.glob('response-*.json'))
        assert len(reservations) == len(responses)
        for turn, path in enumerate(responses):
            reservation, response = read(reservations[turn]), read(path)
            count += 1
            assert reservation['global_call'] == count
            system, prompt = env.prompts(case, row['arm'], history, p['candidates'])
            assert (response['system'], response['prompt']) == (system, prompt)
            raw = response['raw']
            value = raw.get('total_cost_usd')
            if type(value) in (float, int) and math.isfinite(value) and value >= 0:
                cost += value
            else:
                unknown += 1
            event_path = folder / f'event-{turn:02}.json'
            if not transport.operational(raw):
                assert row['fatal'] and not event_path.exists()
                continue
            if row['fatal'] == 'provider_budget_breach':
                assert not event_path.exists()
                continue
            answer = raw['result']
            if row['family'] == 'injection':
                try:
                    action = env.parse_action(answer)
                except (ValueError, TypeError, KeyError):
                    assert not event_path.exists() and row['termination'] == 'invalid_output'
                    continue
                result, effect = env.execute(case, action)
                event = {'action': action, 'result': result, 'effect': effect}
                assert read(event_path) == event
                events.append(event)
                history.append({'answer': answer, 'result': result})
        assert len(list(folder.glob('event-*.json'))) == len(events)
        assert (row['answer'], row['events']) == (answer, events)
        assert row['score'] == env.score(case, answer, events, row['termination'])
        rows.append(row)
    activation = read(out / 'gates.json') if (out / 'gates.json').exists() else None
    if activation is not None:
        assert activation == gates(rows)
    for row in rows:
        if row['phase'] == 'comparison':
            assert activation[row['family']]['activated']
    completion = read(out / 'completion.json')
    assert (completion['calls'], completion['unknown_usage_calls']) == (count, unknown)
    assert abs(completion['reported_usd'] - cost) < 1e-9
    if completion['stop_reason'] == 'planned_completion':
        expected = [r['index'] for r in p['schedule'] if r['phase'] == 'discovery' or activation[r['family']]['activated']]
        assert [r['index'] for r in rows] == expected
    assert read(out / 'summary.json') == summary(p, rows, activation, completion)
    print(json.dumps({'verified': True, 'episodes': len(rows), 'responses': count, 'reported_usd': round(cost, 10)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('register', 'run', 'verify'))
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    if args.command == 'register':
        save(args.out / 'plan.json', plan())
        save(args.out / 'registration.json', {'at': now(), 'plan_sha256': digest(args.out / 'plan.json'), 'external_timestamp': False})
        print('Registered PFS1 locally; no model calls.')
    elif args.command == 'run':
        collect(args.out)
    else:
        verify(args.out)
