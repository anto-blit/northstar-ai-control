#!/usr/bin/env python3
"""Post-hoc analysis of frozen Claude evidence: does extended thinking predict failure?

Reads only saved G10/G11 responses and reports. Makes no model calls and writes
no experiment evidence. `analyze.py verify` re-derives the published numbers and
exits non-zero if the frozen evidence no longer supports them.
"""
from hashlib import sha256
from math import comb
from pathlib import Path
import collections
import json
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
STUDIES = (
    ("G10", "approval-repeatability"),
    ("G11", "story-micro"),
)
# Published claims, recomputed on every run. Changing frozen evidence breaks these.
EXPECTED = {
    "pooled_calls": 300,
    "thinking_zero": 43,
    "thinking_nonzero": 257,
    "nonzero_failures": 0,
    "zero_wrong_approvals": 18,
    "zero_invalid": 18,
    "zero_correct": 7,
    "zero_correct_arms": ["S"],
}


def thinking_tokens(response):
    details = response.get("usage", {}).get("output_tokens_details") or {}
    return details.get("thinking_tokens", 0)


def load(study):
    """Join a frozen report's scored observations to their saved responses."""
    base = ROOT / "results" / study
    report = json.loads((base / "report.json").read_text(encoding="utf-8"))
    rows = []
    for observation in report["observations"]:
        path = base / "responses" / f"{observation['index']:03d}.json"
        response = json.loads(path.read_text(encoding="utf-8"))
        usage = response.get("usage", {})
        rows.append(dict(
            observation,
            study=study,
            think=thinking_tokens(response),
            service_tier=usage.get("service_tier"),
            speed=usage.get("speed"),
            started_at=response.get("started_at"),
            elapsed_seconds=response.get("elapsed_seconds"),
            output_tokens=usage.get("output_tokens"),
        ))
    return rows


def failed(row):
    return bool(row.get("unsafe_approval")) or row["status"] != "valid"


def fisher_two_sided(a, b, c, d):
    """Exact two-sided p-value for a 2x2 table, by summing equal-or-rarer tables."""
    total = a + b + c + d
    if min(a + b, c + d, a + c, b + d) == 0:
        return 1.0

    def probability(x):
        return comb(a + b, x) * comb(c + d, a + c - x) / comb(total, a + c)

    low, high = max(0, a + c - (c + d)), min(a + b, a + c)
    observed = probability(a)
    return sum(probability(x) for x in range(low, high + 1)
               if probability(x) <= observed + 1e-12)


def tally(rows):
    return dict(
        n=len(rows),
        correct=sum(1 for r in rows if r["correct"]),
        wrong_approval=sum(1 for r in rows if r.get("unsafe_approval")),
        invalid=sum(1 for r in rows if r["status"] != "valid"),
    )


def longest_zero_run(rows):
    """Consecutive zero-thinking calls in wall-clock order; clustering would imply a window."""
    longest = run = 0
    for row in sorted(rows, key=lambda r: r["started_at"] or ""):
        run = run + 1 if row["think"] == 0 else 0
        longest = max(longest, run)
    return longest


def evidence_hash():
    digest = sha256()
    for _, study in STUDIES:
        base = ROOT / "results" / study
        for path in sorted(base.glob("responses/*.json")) + [base / "report.json"]:
            digest.update(path.read_bytes())
    return digest.hexdigest()


def analyse():
    rows = [row for _, study in STUDIES for row in load(study)]
    zero = [r for r in rows if r["think"] == 0]
    nonzero = [r for r in rows if r["think"] > 0]

    result = {
        "pooled_calls": len(rows),
        "by_study": {},
        "pooled": {"thinking_zero": tally(zero), "thinking_nonzero": tally(nonzero)},
        "failures_with_thinking": sum(1 for r in nonzero if failed(r)),
        "successes_without_thinking": sum(1 for r in zero if r["correct"]),
        "successes_without_thinking_arms": sorted(
            {r["arm"] for r in zero if r["correct"] and "arm" in r}),
    }
    for label, study in STUDIES:
        srows = [r for r in rows if r["study"] == study]
        result["by_study"][label] = {
            "study": study,
            "calls": len(srows),
            "thinking_zero": tally([r for r in srows if r["think"] == 0]),
            "thinking_nonzero": tally([r for r in srows if r["think"] > 0]),
        }

    # Is "no extended thinking" a property of the prompt? G10 repeats fixed prompts.
    per_case = collections.defaultdict(lambda: [0, 0])
    for row in rows:
        if row["study"] != "approval-repeatability":
            continue
        per_case[row["case"]][0] += 1
        per_case[row["case"]][1] += row["think"] == 0
    result["g10_zero_thinking_rate_by_prompt"] = {
        str(case): {"calls": n, "zero_thinking": z, "rate": round(z / n, 4)}
        for case, (n, z) in sorted(per_case.items())}

    # G11 arms, restricted to the subgroup where any variation exists at all.
    g11 = [r for r in rows if r["study"] == "story-micro" and r["expected"] == "WITHHOLD"]
    result["g11_arms_over_limit"] = {
        arm: {
            "zero_thinking": tally([r for r in g11 if r["arm"] == arm and r["think"] == 0]),
            "with_thinking": tally([r for r in g11 if r["arm"] == arm and r["think"] > 0]),
        }
        for arm in ("D", "F", "S")}

    story = [r for r in g11 if r["arm"] == "S" and r["think"] == 0]
    other = [r for r in g11 if r["arm"] in ("D", "F") and r["think"] == 0]
    story_ok = sum(1 for r in story if r["correct"])
    other_ok = sum(1 for r in other if r["correct"])
    result["g11_zero_thinking_story_vs_rest"] = {
        "story_correct": story_ok, "story_n": len(story),
        "other_correct": other_ok, "other_n": len(other),
        "fisher_two_sided_p": round(fisher_two_sided(
            story_ok, len(story) - story_ok, other_ok, len(other) - other_ok), 8),
        "caveat": "Post-treatment conditioning on a non-randomised variable; "
                  "hypothesis-generating only.",
    }

    # Mechanical-artifact checks: a service window or truncation would show here.
    result["artifact_checks"] = {
        "service_tiers_zero": sorted({r["service_tier"] for r in zero}),
        "service_tiers_nonzero": sorted({r["service_tier"] for r in nonzero}),
        "speed_zero": sorted({r["speed"] for r in zero}),
        "speed_nonzero": sorted({r["speed"] for r in nonzero}),
        "mean_elapsed_seconds_zero": round(statistics.mean(r["elapsed_seconds"] for r in zero), 3),
        "mean_elapsed_seconds_nonzero": round(statistics.mean(r["elapsed_seconds"] for r in nonzero), 3),
        "longest_consecutive_zero_run": longest_zero_run(rows),
        "distinct_thinking_values": sorted({r["think"] for r in rows}),
    }
    result["evidence_sha256"] = evidence_hash()
    return result


def check(result):
    pooled = result["pooled"]
    actual = {
        "pooled_calls": result["pooled_calls"],
        "thinking_zero": pooled["thinking_zero"]["n"],
        "thinking_nonzero": pooled["thinking_nonzero"]["n"],
        "nonzero_failures": result["failures_with_thinking"],
        "zero_wrong_approvals": pooled["thinking_zero"]["wrong_approval"],
        "zero_invalid": pooled["thinking_zero"]["invalid"],
        "zero_correct": pooled["thinking_zero"]["correct"],
        "zero_correct_arms": result["successes_without_thinking_arms"],
    }
    return [f"{key}: published {value!r}, recomputed {actual[key]!r}"
            for key, value in EXPECTED.items() if actual[key] != value]


def main():
    result = analyse()
    problems = check(result)
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        for problem in problems:
            print("MISMATCH", problem)
        print("Frozen evidence still supports the published analysis."
              if not problems else "Published analysis does NOT match frozen evidence.")
        raise SystemExit(1 if problems else 0)
    print(json.dumps(result, indent=2))
    if problems:
        raise SystemExit("Published analysis does not match frozen evidence; see above.")


if __name__ == "__main__":
    main()
