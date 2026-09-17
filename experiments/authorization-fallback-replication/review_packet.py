"""Offline model-masked packet for the two AFR1 targets."""
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]


def build(datasets):
    entries = [(target, req, records[req['index']]['raw'].get('result', ''))
               for target, requests, records in datasets for req in requests if req['index'] in records]
    random.Random(9152026).shuffle(entries)
    packet, mapping = [], []
    for n, (target, req, response) in enumerate(entries):
        ident = f'F{n+1:04}'
        packet.append({'review_id': ident, 'system': req['system'], 'prompt': req['prompt'], 'response': response})
        mapping.append({'review_id': ident, 'target': target, 'index': req['index'],
                        'batch': req['batch'], 'group': req['group'], 'pair_id': req['pair_id'],
                        'response_text_sha256': hashlib.sha256(response.encode()).hexdigest()})
    return packet, mapping


def main():
    datasets = []
    for target in ('claude', 'older'):
        p = ROOT / ('results/authorization-fallback-' + target)
        requests = json.loads((p/'plan.json').read_text(encoding='utf-8'))['requests']
        records = {int(f.stem): json.loads(f.read_text(encoding='utf-8')) for f in (p/'responses').glob('*.json')}
        datasets.append((target, requests, records))
    packet, mapping = build(datasets)
    out = ROOT/'results/authorization-fallback-review'
    out.mkdir(exist_ok=True)
    for name, rows in [('masked-packet.jsonl', packet), ('identity-map.jsonl', mapping)]:
        with (out/name).open('x', encoding='utf-8', newline='\n') as f:
            for row in rows: f.write(json.dumps(row, ensure_ascii=False)+'\n')
    print(f'Exported {len(packet)} masked responses; independent review not performed.')


if __name__ == '__main__': main()
