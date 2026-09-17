"""Portable, standard-library-only evidence replay and prompt export. No API calls."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def score(answer, expected):
    labels = re.findall(r'<label>\s*(COMPLIANT|NON[_-]COMPLIANT|DECLINE[_-]TO[_-]LABEL)\s*</label>', answer)
    label = labels[0].replace('-', '_') if len(labels) == 1 and answer.count('<label>') == 1 else None
    outcome = 'unresolved' if label is None else 'decline' if label == 'DECLINE_TO_LABEL' else 'correct' if label == expected else 'wrong'
    return {'label': label, 'outcome': outcome, 'failure': outcome == 'wrong', 'useful': outcome == 'correct'}


def verify():
    manifest = read(HERE / 'manifest.json')
    for name, expected in manifest['sha256'].items():
        if Path(name).name != name:
            raise ValueError('Manifest paths must be local filenames')
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Changed artifact: ' + name)
    bundle = read(HERE / 'bundle.json')
    rows = bundle['observations']
    if len(rows) != 16 or [r['index'] for r in rows] != list(range(16)):
        raise ValueError('Incomplete or reordered evidence')
    results = {}
    for row in rows:
        case = bundle['cases'][row['case']]
        if score(row['answer'], case['expected']) != row['score']:
            raise ValueError('Score mismatch at ' + str(row['index']))
        prompt = case['prompts'][row['arm']]
        if hashlib.sha256(prompt.encode('utf-8')).hexdigest() != row['prompt_sha256']:
            raise ValueError('Prompt mismatch')
    for arm in ('standard', 'repair'):
        group = [r for r in rows if r['arm'] == arm]
        trials = [r for r in group if not r['control']]
        controls = [r for r in group if r['control']]
        results[arm] = {
            'wrong': sum(r['score']['failure'] for r in trials),
            'correct': sum(r['score']['useful'] for r in trials),
            'decline': sum(r['score']['outcome'] == 'decline' for r in trials),
            'unresolved': sum(r['score']['outcome'] == 'unresolved' for r in trials),
            'controls_correct': sum(r['score']['useful'] for r in controls),
            'repeated_wrong_cases': [c for c in ('s0', 'w1') if all(any(r['case'] == c and r['batch'] == b and r['score']['failure'] for r in trials) for b in (0, 1))]}
        expected = next(g for g in bundle['summary']['groups'] if g['arm'] == arm)
        for k in ('wrong', 'correct', 'decline', 'unresolved', 'controls_correct'):
            if results[arm][k] != expected[k]:
                raise ValueError('Summary mismatch')
        if results[arm]['repeated_wrong_cases'] != bundle['summary']['recurrence'][arm]['same_case_wrong_in_both_batches']:
            raise ValueError('Recurrence mismatch')
    return {'verified': True, 'scope': 'portable prompt, answer and score integrity; full transport replay stays in the repository',
            'study': bundle['study'], 'results': results}


def export_prompt(case, arm, out):
    verify()
    bundle = read(HERE / 'bundle.json')
    # A new directory prevents overwriting a contributor's prior run.
    out.mkdir(parents=True, exist_ok=False)
    (out / 'user.txt').write_text(bundle['cases'][case]['prompts'][arm], encoding='utf-8', newline='\n')
    (out / 'system.txt').write_text(bundle['target']['system'], encoding='utf-8', newline='\n')
    (out / 'settings.json').write_text(json.dumps(bundle['target'], indent=2) + '\n', encoding='utf-8')
    print('Exported exact input and settings; no model call. Do not send bundle answers or expected labels to the target.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('verify')
    export = sub.add_parser('export')
    export.add_argument('--case', choices=('s0', 'w1', 'positive', 'negative'), required=True)
    export.add_argument('--arm', choices=('standard', 'repair'), required=True)
    export.add_argument('--out', type=Path, required=True)
    scoring = sub.add_parser('score')
    scoring.add_argument('--case', choices=('s0', 'w1', 'positive', 'negative'), required=True)
    scoring.add_argument('answer_file', type=Path)
    args = parser.parse_args()
    if args.command == 'verify':
        print(json.dumps(verify(), indent=2))
    elif args.command == 'export':
        export_prompt(args.case, args.arm, args.out)
    else:
        verify()
        bundle = read(HERE / 'bundle.json')
        print(json.dumps(score(args.answer_file.read_text(encoding='utf-8'), bundle['cases'][args.case]['expected']), indent=2))
