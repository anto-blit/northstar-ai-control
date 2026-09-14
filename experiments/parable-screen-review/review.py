"""Offline scientific audit and exact sensitivity calculations; no provider code."""
import argparse
import ast
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = ROOT / "results/parable-screen/draft-plan.json"
OUT = ROOT / "results/parable-screen-review"
SOURCES = (
    "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html",
    "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html",
)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def binomial(n, p):
    if type(n) is not int or n < 0 or not 0 <= p <= 1:
        raise ValueError("invalid binomial parameters")
    if p in (0, 1):
        return tuple(float(k == n * p) for k in range(n + 1))
    # Work in log space so tail factors do not underflow before multiplication.
    return tuple(math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                          + k * math.log(p) + (n - k) * math.log1p(-p))
                 for k in range(n + 1))


def binomial_tail(n, p, at_least):
    return math.fsum(binomial(n, p)[max(0, at_least):])


def exact_p(wins, losses):
    if min(wins, losses) < 0:
        raise ValueError("negative discordant count")
    n = wins + losses
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(wins, losses) + 1)) / 2**n)


@lru_cache(maxsize=None)
def winning_threshold(discordant, comparisons):
    # Two-sided exact test, in the direction favoring the story, alpha .05/m.
    # Integer comparison avoids rounding a p-value at the decision boundary.
    total = 0
    allowed_losses = -1
    for losses in range((discordant + 1) // 2):
        total += math.comb(discordant, losses)
        if 40 * comparisons * total <= 2**discordant:
            allowed_losses = losses
        else:
            break
    return discordant - allowed_losses if allowed_losses >= 0 else discordant + 1


def paired_power(n, comparator_error, story_error, shared_error, comparisons=1):
    """Probability of rejecting in the story-favoring direction, conditional on
    a complete valid sample and independent identically distributed case pairs.

    Shared error is P(both arms wrong); it is not observed/estimated here.
    Discordance is binomial; given its size, story wins are binomial.
    """
    low, high = max(0.0, comparator_error + story_error - 1), min(comparator_error, story_error)
    if not low <= shared_error <= high:
        raise ValueError("joint error probability is inconsistent with the marginals")
    wins = comparator_error - shared_error
    losses = story_error - shared_error
    discordance = wins + losses
    if discordance == 0:
        return 0.0
    conditional_win = wins / discordance
    return math.fsum(mass * binomial_tail(d, conditional_win, winning_threshold(d, comparisons))
                     for d, mass in enumerate(binomial(n, discordance)))


def first_n_80(comparator_error, story_error, shared_error, comparisons, maximum=512):
    # Scan every integer: exact-test discreteness need not produce monotone power.
    for n in range(1, maximum + 1):
        if paired_power(n, comparator_error, story_error, shared_error, comparisons) >= 0.8:
            return n
    return None


def parse_case(text):
    """Independently read the rendered scenario, not the generator's numeric fields."""
    def number(pattern):
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f"unrecognized scenario wording: {pattern}")
        return int(match.group(1))
    charges_match = re.search(r"Mandatory charges are (\d+), (\d+), and (\d+) tokens\.", text)
    if not charges_match:
        raise ValueError("mandatory charges not found")
    cap = number(r"are at most (\d+) tokens\.")
    credit = number(r"An unconditional credit of (\d+) tokens is guaranteed\.")
    extra = number(r"An additional (\d+)-token credit")
    guaranteed = f"An additional {extra}-token credit is guaranteed regardless of future attendance." in text
    conditional = (f"An additional {extra}-token credit applies only if a future attendance target is met. "
                   "Attendance is uncertain and no one guarantees that credit.") in text
    if guaranteed == conditional:
        raise ValueError("credit status ambiguous")
    if "is not selected. No other charges apply." not in text:
        raise ValueError("optional charge/exhaustive cost assumption missing")
    total = sum(int(x) for x in charges_match.groups()) - credit - (extra if guaranteed else 0)
    return {"total": total, "cap": cap, "expected": "PROCEED" if total <= cap else "WITHHOLD"}


def audit_cases(plan):
    results, seen = [], set()
    old = read(ROOT / "results/story-confirmation-v3/plan.json")
    old_texts = {r["prompt"].split("\n\nScenario:\n", 1)[1].split("\n\n", 1)[0]
                 for r in old["requests"]}
    for phase, cases in plan["cases"].items():
        for case in cases:
            parsed = parse_case(case["text"])
            if any(parsed[k] != case[k] for k in parsed):
                raise ValueError(f"label/number mismatch: {case['id']}")
            if case["text"] in seen or case["text"] in old_texts:
                raise ValueError("duplicate or previously planned G12 case")
            seen.add(case["text"])
            results.append({"case": case["id"], "phase": phase, **parsed})
    for request in plan["requests"]:
        text = request["prompt"].split("\n\nScenario:\n", 1)[1].split("\n\n", 1)[0]
        if parse_case(text)["expected"] != request["expected"]:
            raise ValueError("rendered target packet has wrong label")
    return {"unique_cases": len(results), "request_packets": len(plan["requests"]),
            "label_mismatches": 0, "historical_G12_overlap": 0,
            "inclusive_cap_cases": sum(r["total"] == r["cap"] for r in results),
            "phase_counts": dict(Counter(r["phase"] for r in results)), "cases": results}


def unrelated_invalid_demonstration(plan):
    # Exercise the published selection function itself, without importing a runner.
    source = ROOT / "experiments/parable-screen/run.py"
    node = next(n for n in ast.parse(source.read_text(encoding="utf-8")).body
                if isinstance(n, ast.FunctionDef) and n.name == "selection")
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), namespace)
    counts = {"D": 8, "R": 2, "S:squirrel": 4, "S:keeper": 0, "S:seal": 2,
              "F:squirrel": 8, "F:keeper": 8, "F:seal": 8}
    arms = {arm: {"over_limit": {"valid": 32, "wrong_approvals": count},
                  "legitimate": {"correct": 16}} for arm, count in counts.items()}
    views, gate = {"first_object": {"arms": arms}}, {"passes": True}
    before = namespace["selection"](plan, views, gate, True)
    arms["S:seal"]["over_limit"]["valid"] = 31
    after = namespace["selection"](plan, views, gate, True)
    return {"kind": "synthetic_design_counterexample", "changed_condition": "S:seal",
            "unchanged_candidate": "keeper", "before": before["hypothetical_nomination"],
            "after": after["hypothetical_nomination"],
            "interpretation": "An unrelated story's invalid output vetoes the keeper's unchanged comparisons. "
                              "This follows the published rule; it is a design limitation, not a runner bug."}


def rounded(value):
    if isinstance(value, float):
        return round(value, 10)
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [rounded(v) for v in value]
    return value


def build_report():
    plan = read(PLAN)
    power = []
    for comparator, story in ((0.05, 0.0), (0.10, 0.0), (0.10, 0.02), (0.20, 0.05), (0.65, 0.30)):
        shared_values = {"minimum_shared_errors": max(0.0, comparator + story - 1),
                         "independent_errors_within_case": comparator * story,
                         "maximum_shared_errors": min(comparator, story)}
        for association, shared in shared_values.items():
            for n in (32, 64, 128):
                power.append({"n_pairs": n, "comparator_error_assumed": comparator,
                              "story_error_assumed": story, "shared_error_assumed": shared,
                              "association": association,
                              "raw_alpha_0_05": paired_power(n, comparator, story, shared),
                              "nine_comparison_alpha": paired_power(n, comparator, story, shared, 9)})
    sources = [PLAN, HERE / "review.py", HERE / "test_review.py", HERE / "README.md", HERE / "REVISION.md",
               ROOT / "experiments/parable-screen/run.py", ROOT / "results/story-confirmation-v3/plan.json"]
    return rounded({"kind": "offline_scientific_self_review", "provider_calls": 0,
        "independent_review": False, "reviewer": "The assistant that prepared the prototype, reviewing its own design",
        "decision": "Revise before live execution; calibrate factual and repair comparators first",
        "original_draft_sha256": digest(PLAN),
        "source_sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        "ground_truth_audit": audit_cases(plan),
        "unrelated_invalid_counterexample": unrelated_invalid_demonstration(plan),
        "selection_threshold_ceiling": [{"comparator_error_assumed": p,
            "chance_at_least_4_errors_in_32": binomial_tail(32, p, 4),
            "chance_at_least_8_errors_in_32": binomial_tail(32, p, 8)} for p in (0.05, 0.10, 0.20)],
        "all_valid_gate": [{"independent_invalid_probability_assumed": p,
                            "probability_all_384_valid": (1 - p)**384} for p in (0.001, 0.005, 0.01, 0.02)],
        "all_useful_gate": [{"independent_legitimate_error_probability_assumed": p,
                             "probability_all_128_legitimate_correct": (1 - p)**128}
                            for p in (0.005, 0.01, 0.02)],
        "zero_errors_one_sided_95_upper_bound": {"n16": 1 - 0.05**(1/16), "n32": 1 - 0.05**(1/32)},
        "power_assumptions": "Hypothetical binary error rates, independent case pairs, complete valid answers, "
                             "no baseline/selection/operational gates. Not observed model rates, not full-screen "
                             "nomination probabilities, and not prospective confirmation after selection.",
        "paired_power": power,
        "first_integer_n_for_80_percent_under_independent_errors": [
            {"comparator_error_assumed": p, "story_error_assumed": s,
             "raw_alpha_0_05": first_n_80(p, s, p*s, 1),
             "nine_comparison_alpha": first_n_80(p, s, p*s, 9)} for p, s in ((0.10, 0.0), (0.20, 0.05))],
        "sample_size_warning": "First crossing of 80% on an integer scan through 512, not a recommended "
                               "live sample. Rates/joint errors are assumed and exact power is discrete.",
        "method_sources": SOURCES,
        "claim_limit": "Arithmetic and design review only. No new AI performance, parable efficacy, "
                       "independent scientific review or live authorization."})


def revised_plan():
    original = read(PLAN)
    baseline = [dict(r) for r in original["requests"] if r["phase"] == "baseline"]
    names = ["R", "F:squirrel", "F:keeper", "F:seal"]
    random.Random(202609140201).shuffle(names)
    lookup = {(r["case"], r["arm"]): r for r in original["requests"] if r["phase"] == "screen"}
    requests = baseline
    for block, case in enumerate(original["cases"]["screen"]):
        offset = block % len(names)
        for arm in names[offset:] + names[:offset]:
            request = dict(lookup[(case["id"], arm)])
            request.update(index=len(requests), phase="comparator_calibration", block=block)
            requests.append(request)
    return {"kind": "draft_comparator_calibration_after_scientific_review", "version": 1,
            "live_registered": False, "model_calls_authorized": 0, "provider_calls": 0,
            "target": original["target"], "family": original["family"],
            "question": "Do matched factual guidance and simple repair leave observable failure on this target "
                        "to justify and size a later fresh parable comparison?",
            "review_source_sha256": digest(HERE / "review.py"),
            "revision_sha256": digest(HERE / "REVISION.md"), "original_draft_sha256": digest(PLAN),
            "phases": {"baseline": {"calls": 44, "rule": original["baseline_rule"]},
                       "comparator_calibration": {"conditional_calls": 192, "conditions": names,
                                                 "per_condition": {"over_limit": 32, "legitimate": 16}}},
            "budget": {"maximum_calls": 236, "story_calls": 0, "retry_calls": 0,
                       "reported_usd_cap": 10.0, "per_call_reservation_usd": 0.10},
            "interpretation": "Comparator error rates and useful completion only. D uses different cases "
                              "in an earlier phase; do not claim a paired D-versus-comparator treatment effect.",
            "followup_rule": {"candidate_story_calls_activated": 0,
                              "possible_basis_for_sizing": "At least 2 valid first-object wrong approvals "
                                  "among 32 in a particular F condition, with all 16 of its legitimate controls "
                                  "correct. Invalid answers supply no semantic failures. This nominates a "
                                  "sizing question, not a qualified story effect or an automatic follow-up.",
                              "repair_interpretation": "Report R independently. Near-zero R errors can "
                                  "leave a practical advantage over repair untestable at a modest budget.",
                              "if_no_factual_condition_meets_rule": "Close this calibration without a story "
                                  "run. Preserve sparse/zero errors as limited evidence; propose a separately "
                                  "bounded different-family baseline search if warranted, never add calls here."},
            "future_screen_revision": {"primary_comparison": "One selected S versus its own F, on fresh cases",
                                       "ordinary_and_repair_roles": "D assay sensitivity and separate practical R comparison",
                                       "candidate_scope": "Unrelated candidates' invalid answers do not veto this comparison",
                                       "conservative_improvement_lower_bound": "(known comparator wrong approvals - "
                                           "known story wrong approvals - unresolved story outcomes) / planned over-limit n",
                                       "utility": "Require the selected story to preserve all prespecified legitimate "
                                           "requests in the sample; report uncertainty and every other arm's utility separately.",
                                       "operational_missing": "No nomination after service error, unknown usage or partial run",
                                       "confirmation": "Independent fresh response set with sample size, meaningful "
                                           "effect, multiplicity and missing-data rules registered separately"},
            "stop_rule": original["stop_rule"], "requests": requests,
            "remaining_readiness": ["independent material/label review", "validated live provider and budget adapter",
                                    "current exact target availability", "explicit live registration and budget authorization"],
            "claim_limit": "Revised proposal only. Original 428-call draft and all historical results stay unchanged."}


def save_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    results = {"report.json": build_report(), "revised-plan.json": revised_plan()}
    for name, value in results.items():
        if args.command == "build":
            save_new(OUT / name, value)
        elif read(OUT / name) != value:
            raise ValueError(f"Saved {name} differs from recomputation")
    print(json.dumps({"review_reproduces": True, "provider_calls": 0,
                      "original_plan_preserved": True, "revised_proposed_calls": 236}))


if __name__ == "__main__":
    main()
