"""G17 materials: G12-B's audited cases and frozen arms, at a suppressed-deliberation target.

Nothing here is new content. The case generator, the four arm texts and the two
output contracts are imported unchanged from the frozen G12-B sources, so the
only deliberate difference between G17 and G12-B is the target configuration:
`--effort low` instead of `medium`.

G12-B's cases carry sixteen blind label reviews that agreed on all 256 case
labels and calculations. Reusing them inherits that audit; regenerating
equivalent cases would not.
"""
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
ARMS = "DFSR"
ARM_NAMES = {"D": "original prompt", "F": "matched factual guidance",
             "S": "story guidance", "R": "justification-first repair"}

# Stage A qualifies the baseline; stage B is registered separately once A reports.
STAGE_A_PAIRS = 32          # 32 over-limit + 8 legitimate controls, arm D only
STAGE_A_CONTROLS = 8

# Sources inherited unchanged. Their hashes are recorded in the plan; if any of
# them changes, this study must be re-versioned rather than re-run.
INHERITED = (
    "experiments/story-confirmation-v3/materials.py",   # case generator + arm assembly
    "experiments/approval-story-screen/run.py",         # RULE / FACT / STORY texts
    "experiments/decision-repair/run.py",               # ORIGINAL / REPAIRED contracts
    "results/repair-continuation/attempts/068-01.json",  # commitments prefix + system text
)


def _module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def g12b():
    return _module("g17_inherited_materials", "experiments/story-confirmation-v3/materials.py")


def inherited_hashes():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in INHERITED}


def all_requests():
    """Every G12-B request row, unchanged, in its frozen deterministic order."""
    return g12b().requests()


def stage_a_requests():
    """Arm D only: the baseline the gate requires before any intervention arm runs.

    Blocks are taken in G12-B's frozen shuffled order, so the cases are neither
    hand-picked nor reordered to favour a result.
    """
    rows = [row for row in all_requests() if row["arm"] == "D"]
    over = [r for r in rows if r["expected"] == "WITHHOLD"][:STAGE_A_PAIRS]
    legit = [r for r in rows if r["expected"] == "PROCEED"][:STAGE_A_CONTROLS]
    selected = over + legit
    for index, row in enumerate(selected):
        row["stage"] = "A"
        row["index"] = index
    return selected


def stage_b_requests(pairs):
    """All four arms on the first `pairs` blocks not used by stage A.

    Stage A's cases are excluded so the comparison is not scored on the same
    instances that qualified its baseline.
    """
    used = {row["case"] for row in stage_a_requests()}
    rows = [row for row in all_requests() if row["case"] not in used]
    blocks, seen = [], set()
    for row in rows:
        if row["block"] not in seen and len(seen) < pairs:
            seen.add(row["block"])
        blocks.append(row)
    selected = [row for row in blocks if row["block"] in seen]
    for index, row in enumerate(selected):
        row["stage"] = "B"
        row["index"] = index
    return selected


if __name__ == "__main__":
    a = stage_a_requests()
    print(json.dumps({
        "stage_a_calls": len(a),
        "over_limit": sum(r["expected"] == "WITHHOLD" for r in a),
        "legitimate": sum(r["expected"] == "PROCEED" for r in a),
        "arms_present": sorted({r["arm"] for r in a}),
        "distinct_cases": len({r["case"] for r in a}),
        "inherited_hashes": inherited_hashes(),
    }, indent=2))
