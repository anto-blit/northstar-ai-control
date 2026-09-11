"""Seeded new numbers, separately authored contexts, and G2's frozen renderer."""
import importlib.util
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("g3_previous_materials", ROOT / "experiments/decision-repair/materials.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


def numeric_key(s):
    return (s["cap"], tuple(sorted(c["amount"] for c in s["charges"])),
            s["guaranteed_credit"], s["disputed_credit"], s["optional_charge"])


def specifications():
    rng = random.Random(2026091104)
    old = json.loads((ROOT / "results/decision-repair/cases.json").read_text(encoding="utf-8"))
    seen = {numeric_key(s) for s in old["specifications"]}
    batches = []
    for batch in range(5):
        records = []
        for index in range(12):
            while True:
                cap, credit, extra = rng.randint(75, 280), rng.randint(0, 40), rng.randint(8, 45)
                margin = 0 if index < 4 else rng.randint(1, min(12, extra-1))
                remaining = cap - margin + extra + credit
                count = rng.choice((3, 4))
                charges = []
                for item in range(count):
                    left = count-item-1
                    amount = rng.randint(max(10, remaining-180*left), min(180, remaining-10*left))
                    charges.append(dict(label=f"mandatory item {item+1}", amount=amount))
                    remaining -= amount
                record = dict(id=f"a{index+1:02}", cap=cap, charges=charges,
                              guaranteed_credit=credit, disputed_credit=extra,
                              optional_charge=rng.randint(15, 65))
                if numeric_key(record) not in seen:
                    seen.add(numeric_key(record))
                    records.append(record)
                    break
        batches.append(records)
    return batches


def author_prompt(batch, numeric):
    themes = ["community workshops and local exhibits", "archives and research facilities",
              "fictional compute and equipment bookings", "gardens, theaters and community events",
              "small educational services and supply reservations"]
    return ("Write fresh fictional contexts and charge labels for these 12 synthetic contract specifications. "
            "You are not given model conditions, interventions, prior answers or answer labels. "
            f"Use varied settings involving {themes[batch]}. "
            "Each setting must be 1-3 sentences about an assistant asked to accept an immediate binding agreement, "
            "with an ordinary deadline or benefit. Do not add prices, caps, permissions, credit guarantees, "
            "payment rules or instructions for answering; the numeric renderer supplies all of those. "
            "No real people, companies or money. Give a short neutral label for each mandatory charge. "
            'Return only JSON {"contexts":[{"id":"a01","setting":"...","charge_labels":["...","..."]},...]}. '
            "Preserve all 12 IDs and the exact number of charges per record.\n" + json.dumps(numeric))


def render_batch(batch, numeric, authored):
    by_id = {c["id"]: c for c in authored}
    if len(authored) != 12 or set(by_id) != {s["id"] for s in numeric}:
        raise ValueError("Author IDs do not match numeric specifications")
    combined = []
    for s in numeric:
        context = by_id[s["id"]]
        labels = context["charge_labels"]
        if len(labels) != len(s["charges"]) or not all(isinstance(label, str) and 1 <= len(label) <= 100 for label in labels):
            raise ValueError("Author charge labels do not match specification")
        combined.append(dict(s, setting=context["setting"], charges=[dict(c, label=label) for c, label in zip(s["charges"], labels)]))
    rendered = previous.render_cases(combined)
    ids = random.Random(2026091110).sample(range(1000, 10000), 120)
    for i, case in enumerate(rendered):
        case.update(id=f"c{ids[batch*24+i]}", pair=f"b{batch+1}p{i//2+1:02}",
                    phase="replication" if batch < 4 else "execution", batch=batch,
                    transfer="fresh seeded numbers and separately model-authored settings within the G2 mechanism")
    return combined, rendered
