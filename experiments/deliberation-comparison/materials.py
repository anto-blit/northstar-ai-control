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
# A2 re-runs the qualification on fresh cases under a revised control rule and
# the tolerant scorer. More controls than A, because the rule it must satisfy is
# now a rate rather than a single all-correct check.
STAGE_A2_PAIRS = 32
STAGE_A2_CONTROLS = 12

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


def stage_a2_requests():
    """Arm D only, on fresh cases: the cases stage A used are excluded.

    A2 exists because stage A's control rule conflated a legitimate case being
    wrongly withheld with a legitimate answer being malformed. The revised rule
    is in PROTOCOL.md; the cases here are disjoint from stage A's so the revised
    rule is never applied to the answers that prompted the revision.
    """
    used = {row["case"] for row in stage_a_requests()}
    rows = [row for row in all_requests() if row["arm"] == "D" and row["case"] not in used]
    over = [r for r in rows if r["expected"] == "WITHHOLD"][:STAGE_A2_PAIRS]
    legit = [r for r in rows if r["expected"] == "PROCEED"][:STAGE_A2_CONTROLS]
    selected = over + legit
    for index, row in enumerate(selected):
        row["stage"] = "A2"
        row["index"] = index
    return selected


def stage_b_requests(over_limit_blocks, legitimate_blocks):
    """All four arms on blocks used by neither A nor A2, balanced by case type.

    Earlier stages' cases are excluded so the comparison is not scored on the
    same instances that qualified its baseline. Stages A and A2 consumed the
    earliest over-limit cases in the frozen order, so the counts are requested
    explicitly rather than taken as a prefix, which would leave the comparison
    with almost no over-limit attempts.
    """
    used = ({row["case"] for row in stage_a_requests()}
            | {row["case"] for row in stage_a2_requests()})
    rows = [row for row in all_requests() if row["case"] not in used]
    wanted, seen = {"WITHHOLD": over_limit_blocks, "PROCEED": legitimate_blocks}, {}
    for row in rows:
        if row["block"] in seen:
            continue
        if wanted.get(row["expected"], 0) > 0:
            wanted[row["expected"]] -= 1
            seen[row["block"]] = row["expected"]
    if any(count > 0 for count in wanted.values()):
        raise ValueError(f"not enough unused blocks remain: {wanted}")
    selected = [row for row in rows if row["block"] in seen]
    for index, row in enumerate(selected):
        row["stage"] = "B"
        row["index"] = index
    return selected


REQUESTS = {"A": stage_a_requests, "A2": stage_a2_requests}


if __name__ == "__main__":
    a, a2 = stage_a_requests(), stage_a2_requests()
    print(json.dumps({
        "stage_a_calls": len(a),
        "stage_a2_calls": len(a2),
        "stage_a2_over_limit": sum(r["expected"] == "WITHHOLD" for r in a2),
        "stage_a2_legitimate": sum(r["expected"] == "PROCEED" for r in a2),
        "arms_present_a2": sorted({r["arm"] for r in a2}),
        "cases_shared_between_a_and_a2": sorted(
            {r["case"] for r in a} & {r["case"] for r in a2}),
        "inherited_hashes": inherited_hashes(),
    }, indent=2))
