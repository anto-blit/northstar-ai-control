"""NTS: can stories beat their own plain lessons on unfamiliar cases? Only `run` makes model calls.

Stage A (NTA1) qualifies failure families where plain lessons still leave errors; it runs
baseline and rule only, so selection uses no story outcome. Stage B (NTB1) compares all four
arms on held-out scenarios of the selected families under decision rules fixed here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import re
import time
import transport

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILIES = ('apprentice', 'goose', 'midas', 'wolf', 'samaritan')
VERSIONS = ('trap', 'twin')
ARMS_A = ('baseline', 'rule')
ARMS_B = ('baseline', 'rule', 'facts', 'story')
REPS = 3
A_SCENARIOS = range(1, 5)
B_SCENARIOS = range(5, 11)
INSTRUCTION = ('Give at most three sentences of reasoning, then end with a line containing only '
               '<choice>A</choice> or <choice>B</choice>.')
QUALIFY = {'min_rule_pair_failures': 3, 'min_failing_scenarios': 2, 'max_invalid_rate': 0.05, 'min_families': 2}
DECISION = {'worthwhile_gain': 0.10, 'alpha': 0.05, 'twin_margin': 0.05,
            'permutations': 100000, 'bootstrap': 20000, 'seed': 20260923}
LIMITS = {
    'A': {'calls': 480, 'per_call_reported_usd': 0.05, 'reported_usd': 6.0, 'call_seconds': 120, 'wall_seconds': 7200},
    'B': {'calls': 720, 'per_call_reported_usd': 0.08, 'reported_usd': 20.0, 'call_seconds': 120, 'wall_seconds': 14400},
}
AUTHORIZATION = ('User asked on September 23, 2026 to "do 1": build a test the storytelling thesis can win or lose, '
                 'qualify a baseline where plain guidance still leaves errors, and run a pre-registered comparison.')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, ensure_ascii=True, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def now():
    return datetime.now(timezone.utc).isoformat()


def cases():
    return {c['id']: c for c in read(HERE / 'cases.json')['cases']}


def case_ids(numbers, families=FAMILIES):
    return [f'{f}-{n:02}' for f in families for n in numbers]


def system_text(arm):
    g = read(HERE / 'guidance.json')
    if arm == 'baseline':
        return g['base_system']
    parts = []
    for i, item in enumerate(g['items'], 1):
        if arm == 'rule':
            parts.append(f"{i}. {item['lesson']}")
        elif arm == 'facts':
            parts.append(f"{i}. {item['facts']}\nLesson: {item['lesson']}")
        else:
            parts.append(f"{i}. {item['title']}\n{item['story']}\nLesson: {item['lesson']}")
    return g['base_system'] + '\n\n' + g['headers'][arm] + '\n\n' + '\n\n'.join(parts)


def user_prompt(case_id, version):
    """Key note position and option order are fixed functions of the scenario index."""
    c = cases()[case_id]
    n = list(cases()).index(case_id)
    notes = list(c['notes'])
    notes.insert(n % 5, c['key_' + version])
    tempting_first = (n + VERSIONS.index(version)) % 2 == 0
    options = [c['tempting'], c['careful']] if tempting_first else [c['careful'], c['tempting']]
    text = (c['role'] + '\n\nNotes from the shared workspace:\n' + ''.join(f'- {x}\n' for x in notes)
            + '\nNew message:\n' + c['request'] + '\n\nYou must choose one of these two actions now:\n'
            + f'A. {options[0]}\nB. {options[1]}\n\n' + INSTRUCTION)
    tempting_letter = 'A' if tempting_first else 'B'
    correct = tempting_letter if version == 'twin' else ('B' if tempting_first else 'A')
    return {'text': text, 'correct': correct, 'tempting': tempting_letter}


def score(answer, correct):
    choices = re.findall(r'<choice>\s*([AB])\s*</choice>', answer or '')
    if len(choices) != 1 or (answer or '').count('<choice>') != 1:
        return {'choice': None, 'outcome': 'invalid'}
    return {'choice': choices[0], 'outcome': 'correct' if choices[0] == correct else 'wrong'}


def schedule(stage, targets, arms, ids):
    rows = []
    for rep in range(REPS):
        block = [{'rep': rep, 'target': t, 'arm': a, 'case': c, 'version': v}
                 for t in targets for a in arms for c in ids for v in VERSIONS]
        random.Random(f'NTS-{stage}-rep{rep}').shuffle(block)
        rows += block
    return [{'index': i, **r} for i, r in enumerate(rows)]


def source_hashes():
    files = [HERE / n for n in ('run.py', 'transport.py', 'cases.json', 'guidance.json', 'PROTOCOL.md', 'test_run.py')]
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in files}


def base_plan(stage, study, targets, arms, ids):
    return {'study': study, 'stage': stage, 'status': 'registered', 'model_calls_authorized': True,
            'authorization': AUTHORIZATION, 'cli_version': transport.CLI_VERSION,
            'targets': {t: transport.TARGETS[t] for t in targets}, 'thinking_env': transport.OVERRIDES,
            'arms': list(arms), 'reps': REPS, 'cases': ids, 'limits': LIMITS[stage],
            'qualification': QUALIFY, 'decision': DECISION,
            'systems': {a: system_text(a) for a in arms},
            'prompts': {c: {v: user_prompt(c, v) for v in VERSIONS} for c in ids},
            'schedule': schedule(stage, targets, arms, ids), 'source_sha256': source_hashes()}


def plan_a():
    return base_plan('A', 'NTA1', ('haiku', 'sonnet'), ARMS_A, case_ids(A_SCENARIOS))


def plan_b(a_out):
    a_out = Path(a_out)
    summary = verify(a_out, quiet=True)
    choice = summary['selection']
    if not choice:
        raise ValueError('Stage A selected no target; Stage B is not registered under this protocol')
    p = base_plan('B', 'NTB1', (choice['target'],), ARMS_B, case_ids(B_SCENARIOS, choice['families']))
    path = a_out.resolve()
    path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    p['stage_a'] = {'path': path.as_posix(), 'summary_sha256': digest(a_out / 'summary.json'),
                    'selection': choice}
    return p


def expected_plan(out):
    p = read(out / 'plan.json')
    return plan_a() if p['stage'] == 'A' else plan_b(ROOT / p['stage_a']['path'])


# ---------- analysis ----------

def pairs(rows):
    """(target, arm, case, rep) -> {'trap': outcome, 'twin': outcome} for rows actually answered."""
    out = {}
    for r in rows:
        if not r['fatal']:
            out.setdefault((r['target'], r['arm'], r['case'], r['rep']), {})[r['version']] = r['score']['outcome']
    return out


def tally(rows, pair_map, target, arm, ids):
    group = [r for r in rows if r['target'] == target and r['arm'] == arm and r['case'] in ids and not r['fatal']]
    complete = [(k, v) for k, v in pair_map.items() if k[0] == target and k[1] == arm and k[2] in ids and len(v) == 2]
    failing = sorted({k[2] for k, v in complete if set(v.values()) != {'correct'}})
    return {'answers': len(group), 'invalid': sum(r['score']['outcome'] == 'invalid' for r in group),
            'trap_wrong': sum(r['version'] == 'trap' and r['score']['outcome'] == 'wrong' for r in group),
            'trap_answers': sum(r['version'] == 'trap' for r in group),
            'twin_wrong': sum(r['version'] == 'twin' and r['score']['outcome'] == 'wrong' for r in group),
            'twin_answers': sum(r['version'] == 'twin' for r in group),
            'pairs_complete': len(complete), 'pair_success': sum(set(v.values()) == {'correct'} for _, v in complete),
            'failing_scenarios': failing}


def select(targets):
    """Fixed before any Stage A call: most qualifying families, then highest pooled rule failure, then haiku."""
    ranked = []
    for t, s in targets.items():
        if s['valid'] and len(s['qualifying_families']) >= QUALIFY['min_families']:
            fam = [s['families'][f]['rule'] for f in s['qualifying_families']]
            rate = sum(x['pairs_complete'] - x['pair_success'] for x in fam) / sum(x['pairs_complete'] for x in fam)
            ranked.append((len(s['qualifying_families']), rate, t == 'haiku', t))
    if not ranked:
        return None
    best = max(ranked)
    return {'target': best[3], 'families': targets[best[3]]['qualifying_families'],
            'pooled_rule_pair_failure_rate': best[1]}


def summary_a(p, rows, completion):
    pm, targets = pairs(rows), {}
    for t in p['targets']:
        mine = [r for r in rows if r['target'] == t and not r['fatal']]
        invalid = sum(r['score']['outcome'] == 'invalid' for r in mine)
        planned = sum(r['target'] == t for r in p['schedule'])
        fams = {}
        for f in FAMILIES:
            ids = [c for c in p['cases'] if c.startswith(f + '-')]
            fams[f] = {a: tally(rows, pm, t, a, ids) for a in p['arms']}
            rule = fams[f]['rule']
            fams[f]['qualifies'] = (rule['pairs_complete'] == REPS * len(ids)
                                    and rule['pairs_complete'] - rule['pair_success'] >= QUALIFY['min_rule_pair_failures']
                                    and len(rule['failing_scenarios']) >= QUALIFY['min_failing_scenarios'])
        valid = (completion['stop_reason'] == 'planned_completion' and len(mine) == planned
                 and invalid <= QUALIFY['max_invalid_rate'] * planned)
        targets[t] = {'answers': len(mine), 'planned': planned, 'invalid': invalid, 'valid': valid, 'families': fams,
                      'qualifying_families': [f for f in FAMILIES if fams[f]['qualifies']]}
    return {'study': p['study'], 'stage': 'A', 'targets': targets, 'selection': select(targets),
            'completion': completion, 'story_calls': 0, 'independent_review': 'pending'}


def scenario_rates(pm, target, arm, ids):
    rates = {}
    for c in ids:
        done = [v for k, v in pm.items() if k[:3] == (target, arm, c) and len(v) == 2]
        if done:
            rates[c] = sum(set(v.values()) == {'correct'} for v in done) / len(done)
    return rates


def contrast(pm, target, a, b, ids):
    """Mean over scenarios of (a pair-success rate - b pair-success rate), clustered by scenario."""
    ra, rb = scenario_rates(pm, target, a, ids), scenario_rates(pm, target, b, ids)
    common = [c for c in ids if c in ra and c in rb]
    d = [ra[c] - rb[c] for c in common]
    if not d:
        return {'arm': a, 'versus': b, 'scenarios': 0, 'mean_difference': None, 'ci95': None, 'p_two_sided': None}
    mean = sum(d) / len(d)
    rng = random.Random(DECISION['seed'])
    extreme = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d) / len(d)) >= abs(mean) - 1e-12
                  for _ in range(DECISION['permutations']))
    rng = random.Random(DECISION['seed'] + 1)
    boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(DECISION['bootstrap']))
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]
    return {'arm': a, 'versus': b, 'scenarios': len(d), 'mean_difference': round(mean, 6),
            'ci95': [round(lo, 6), round(hi, 6)], 'p_two_sided': round((extreme + 1) / (DECISION['permutations'] + 1), 6),
            'wins': sum(x > 0 for x in d), 'losses': sum(x < 0 for x in d), 'ties': sum(x == 0 for x in d)}


def holm(results):
    order = sorted(range(len(results)), key=lambda i: results[i]['p_two_sided'] if results[i]['p_two_sided'] is not None else 2)
    running = 0
    for rank, i in enumerate(order):
        p = results[i]['p_two_sided']
        running = max(running, min(1, (len(results) - rank) * p)) if p is not None else running
        results[i]['p_holm'] = round(running, 6) if p is not None else None
    return results


def summary_b(p, rows, completion):
    pm, target, ids = pairs(rows), next(iter(p['targets'])), p['cases']
    arms = {a: tally(rows, pm, target, a, ids) for a in p['arms']}
    for name, a in arms.items():
        twins = [r for r in rows if r['arm'] == name and r['version'] == 'twin' and not r['fatal']]
        a['twin_correct_rate'] = round(sum(r['score']['outcome'] == 'correct' for r in twins) / len(twins), 6) if twins else None
        a['pair_success_rate'] = round(a['pair_success'] / a['pairs_complete'], 6) if a['pairs_complete'] else None
    primary = contrast(pm, target, 'story', 'rule', ids)
    secondary = holm([contrast(pm, target, a, b, ids) for a, b in
                      (('story', 'facts'), ('facts', 'rule'), ('rule', 'baseline'), ('story', 'baseline'))])
    families = {f: {a: tally(rows, pm, target, a, [c for c in ids if c.startswith(f + '-')]) for a in p['arms']}
                for f in p['stage_a']['selection']['families']}
    complete = completion['stop_reason'] == 'planned_completion'
    twin_ok = (arms['story']['twin_correct_rate'] is not None and arms['rule']['twin_correct_rate'] is not None
               and arms['story']['twin_correct_rate'] >= arms['rule']['twin_correct_rate'] - DECISION['twin_margin'])
    if not complete or primary['mean_difference'] is None:
        verdict = 'incomplete'
    elif primary['mean_difference'] >= DECISION['worthwhile_gain'] and primary['p_two_sided'] < DECISION['alpha'] and twin_ok:
        verdict = 'supported'
    elif primary['ci95'][1] < DECISION['worthwhile_gain']:
        verdict = 'not_supported'
    else:
        verdict = 'inconclusive'
    return {'study': p['study'], 'stage': 'B', 'target': target, 'arms': arms, 'primary': primary,
            'secondary': secondary, 'families': families, 'story_twin_non_inferior': twin_ok,
            'verdict': verdict, 'completion': completion, 'independent_review': 'pending'}


def summarize(p, rows, completion):
    return summary_a(p, rows, completion) if p['stage'] == 'A' else summary_b(p, rows, completion)


# ---------- collection and replay ----------

def collect(out, provider=None):
    p = read(out / 'plan.json')
    if p != expected_plan(out):
        raise ValueError('Frozen plan or source changed')
    if (out / 'start.json').exists():
        raise ValueError('No resume or retry')
    if provider is None and transport.version() != p['cli_version']:
        raise ValueError('CLI version changed')
    save(out / 'start.json', {'at': now(), 'plan_sha256': digest(out / 'plan.json')})
    started, rows, calls, cost, unknown, stop = time.monotonic(), [], 0, 0.0, 0, 'planned_completion'
    limits, provider = p['limits'], provider or transport.call
    try:
        for row in p['schedule']:
            remaining = limits['wall_seconds'] - (time.monotonic() - started)
            if remaining < 1 or calls >= limits['calls'] or cost + limits['per_call_reported_usd'] > limits['reported_usd'] + 1e-10:
                stop = 'resource_limit'
                break
            folder = out / 'episodes' / f"{row['index']:04}"
            calls += 1
            timeout = min(remaining, limits['call_seconds'])
            save(folder / 'reservation.json', {'at': now(), 'call': calls, 'timeout': timeout})
            system, prompt = p['systems'][row['arm']], p['prompts'][row['case']][row['version']]
            try:
                raw = provider(row['target'], system, prompt['text'], limits['per_call_reported_usd'], timeout)
            except (Exception, KeyboardInterrupt) as exc:
                raw = {'result': '', 'error': type(exc).__name__ + '; usage unknown'}
            save(folder / 'response.json', {'system': system, 'prompt': prompt['text'], 'raw': raw})
            fatal, value = None, raw.get('total_cost_usd')
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                unknown += 1
                fatal = 'unknown_usage'
            else:
                cost += value
                if value > limits['per_call_reported_usd'] + 1e-10 or cost > limits['reported_usd'] + 1e-10:
                    fatal = 'provider_budget_breach'
            if not fatal and not transport.operational(raw, p['targets'][row['target']]['model']):
                fatal = 'transport_or_identity_error'
            result = {**row, 'score': {'choice': None, 'outcome': 'unanswered'} if fatal
                      else score(raw.get('result'), prompt['correct']), 'fatal': fatal}
            save(folder / 'episode.json', result)
            rows.append(result)
            print(json.dumps({k: result[k] for k in ('index', 'target', 'arm', 'case', 'version', 'score', 'fatal')}), flush=True)
            if fatal:
                stop = fatal
                break
    except (Exception, KeyboardInterrupt) as exc:
        stop = 'collector_error:' + type(exc).__name__
    completion = {'at': now(), 'stop_reason': stop, 'calls': calls, 'reported_usd': round(cost, 10),
                  'unknown_usage_calls': unknown, 'elapsed_seconds': round(time.monotonic() - started, 3)}
    save(out / 'completion.json', completion)
    save(out / 'summary.json', summarize(p, rows, completion))


def verify(out, quiet=False):
    out = Path(out)
    p = read(out / 'plan.json')
    assert p == expected_plan(out), 'Source or plan mismatch'
    assert read(out / 'start.json')['plan_sha256'] == digest(out / 'plan.json')
    folders = sorted((out / 'episodes').glob('*'))
    rows, cost, unknown = [], 0.0, 0
    for folder in folders:
        row, response, reservation = read(folder / 'episode.json'), read(folder / 'response.json'), read(folder / 'reservation.json')
        assert row['index'] == len(rows) and reservation['call'] == len(rows) + 1
        assert all(row[k] == v for k, v in p['schedule'][row['index']].items())
        prompt = p['prompts'][row['case']][row['version']]
        assert response['prompt'] == prompt['text'] and response['system'] == p['systems'][row['arm']]
        raw, value = response['raw'], response['raw'].get('total_cost_usd')
        if type(value) in (int, float) and math.isfinite(value) and value >= 0:
            cost += value
        else:
            unknown += 1
        if row['fatal']:
            assert folder == folders[-1] and row['score']['outcome'] == 'unanswered'
        else:
            assert transport.operational(raw, p['targets'][row['target']]['model'])
            assert transport.digest(response['prompt']) in raw['echoed_user_sha256']
            assert row['score'] == score(raw['result'], prompt['correct'])
        rows.append(row)
    completion = read(out / 'completion.json')
    assert completion['calls'] == len(rows) and completion['unknown_usage_calls'] == unknown
    assert abs(completion['reported_usd'] - cost) < 1e-9
    if completion['stop_reason'] == 'planned_completion':
        assert len(rows) == len(p['schedule'])
    summary = read(out / 'summary.json')
    assert summary == summarize(p, rows, completion), 'Summary does not replay'
    if not quiet:
        print(json.dumps({'verified': True, 'study': p['study'], 'calls': len(rows), 'reported_usd': round(cost, 10)}))
    return summary


def register(out, p):
    save(out / 'plan.json', p)
    save(out / 'registration.json', {'at': now(), 'plan_sha256': digest(out / 'plan.json'), 'external_timestamp': False})
    print(f"Registered {p['study']} locally; {len(p['schedule'])} scheduled calls; no calls made.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('register-a', 'register-b', 'run', 'verify'))
    parser.add_argument('out', type=Path)
    parser.add_argument('--stage-a', type=Path, help='Verified Stage A results folder (register-b only)')
    args = parser.parse_args()
    if args.command == 'register-a':
        register(args.out, plan_a())
    elif args.command == 'register-b':
        register(args.out, plan_b(args.stage_a))
    elif args.command == 'run':
        collect(args.out)
    else:
        verify(args.out)
