"""Offline model-masked review packet; identity mapping stays in a separate file."""
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/authorization-pressure-openai'


def build(datasets):
    entries = []
    for name, requests, records in datasets:
        for req in requests:
            rec = records.get(req['index'])
            if rec is None:
                continue
            text = rec['raw'].get('result', '')
            entries.append((name, req, text))
    random.Random(9142026).shuffle(entries)
    packet, mapping = [], []
    for i, (name, req, text) in enumerate(entries):
        opaque = f'R{i + 1:04}'
        packet.append({'review_id': opaque, 'system': req['system'], 'prompt': req['prompt'], 'response': text})
        mapping.append({'review_id': opaque, 'dataset': name, 'index': req['index'],
                        'id': req['case']['id'], 'repeat': req['repeat'],
                        'response_text_sha256': hashlib.sha256(text.encode()).hexdigest()})
    return packet, mapping


def main():
    datasets = []
    for name in ('authorization-pressure-smoke-v2', 'authorization-pressure-openai'):
        p = ROOT / 'results' / name
        requests = json.loads((p / 'plan.json').read_text(encoding='utf-8'))['requests']
        records = {int(f.stem): json.loads(f.read_text(encoding='utf-8')) for f in (p / 'responses').glob('*.json')}
        datasets.append((name, requests, records))
    packet, mapping = build(datasets)
    for name, rows in (('masked-review-packet.jsonl', packet), ('review-identity-map.jsonl', mapping)):
        with (OUT / name).open('x', encoding='utf-8', newline='\n') as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'Exported {len(packet)} masked rows; mapping is separate. No model calls or independent labels.')


if __name__ == '__main__': main()
