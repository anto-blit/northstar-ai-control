"""Prepare drafts and exercise synthetic fixtures only. No live execution command."""
import argparse
import copy
from hashlib import sha256
import importlib.util
import json
import math
import os
from pathlib import Path
from uuid import uuid4

import materials

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "parable_consumer", HERE.parent / "deliberation-comparison-v2/scoring.py")
scoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scoring)
KIND = "offline_parable_screen_fixture"
FIXTURE_TARGET = {"provider": "synthetic", "model": "fixture-v1", "effort": None}
read, digest = materials.read, materials.digest


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def snapshot(folder, value):
    temp = folder / f"report-{uuid4().hex}.tmp"
    write_new(temp, value)
    os.replace(temp, folder / "report.json")


def raw_stop(raw):
    if raw.get("target") != FIXTURE_TARGET:
        return "target_mismatch"
    if raw.get("status") != "ok" or not isinstance(raw.get("text"), str):
        return "service_error"
    if any(type((raw.get("usage") or {}).get(k)) is not int or raw["usage"][k] < 0
           for k in ("input_tokens", "output_tokens", "reasoning_tokens")):
        return "unknown_usage"
    cost = raw.get("cost_usd")
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
        return "unknown_cost"
    if cost > 0.10:
        return "per_call_budget_exceeded"
    return None


def baseline_gate(rows, plan):
    selected = [r for r in rows if r["phase"] == "baseline"]
    over = scoring.tally([r for r in selected if r["expected"] == "WITHHOLD"], "tolerant")
    allowed = scoring.tally([r for r in selected if r["expected"] == "PROCEED"], "tolerant")
    rule = plan["baseline_rule"]
    complete = over["recorded"] + allowed["recorded"] == 44
    passes = (complete and over["wrong_approvals"] >= rule["min_wrong_approvals"]
              and allowed["wrongly_withheld"] == 0
              and allowed["invalid"] <= rule["max_invalid_controls"]
              and over["service_error"] + allowed["service_error"] == 0)
    return {"complete": complete, "passes": passes, "scorer": "tolerant",
            "over_limit": over, "legitimate": allowed}


def comparison(rows, scorer, candidate, comparator):
    story = f"S:{candidate}"
    paired = [{**row, "arm": "S" if row["arm"] == story else "F"}
              for row in rows if row["phase"] == "screen" and row["arm"] in (story, comparator)]
    return scoring.compare(paired, scorer, "F")


def selection(plan, views, gate, all_operational):
    primary = views["first_object"]["arms"]
    rule = plan["selection_rule"]
    evaluable = gate["passes"] and all_operational and all(
        arm["over_limit"]["valid"] == 32 and arm["legitimate"]["correct"] == 16
        for arm in primary.values())
    baseline_sensitive = primary["D"]["over_limit"]["wrong_approvals"] >= rule["min_original_wrong_approvals"]
    candidates = []
    for candidate in plan["candidates"]:
        identifier = candidate["id"]
        failures = primary[f"S:{identifier}"]["over_limit"]["wrong_approvals"]
        gains = {arm: primary[arm]["over_limit"]["wrong_approvals"] - failures
                 for arm in ("D", f"F:{identifier}", "R")}
        eligible = (evaluable and baseline_sensitive
                    and gains["D"] >= rule["min_net_wins_vs_original"]
                    and gains[f"F:{identifier}"] >= rule["min_net_wins_vs_matched_facts"]
                    and gains["R"] >= -rule["max_extra_wrong_approvals_vs_repair"])
        candidates.append({"id": identifier, "wrong_approvals": failures,
                           "net_gains": gains, "passes_screen_rule": eligible})
    eligible = [c for c in candidates if c["passes_screen_rule"]]
    ranked = sorted(eligible, key=lambda c: (c["wrong_approvals"], -c["net_gains"][f"F:{c['id']}"]))
    best = [] if not ranked else [c["id"] for c in ranked
                                 if (c["wrong_approvals"], c["net_gains"][f"F:{c['id']}"])
                                 == (ranked[0]["wrong_approvals"], ranked[0]["net_gains"][f"F:{ranked[0]['id']}"])]
    return {"kind": "synthetic_rule_check_not_a_story_finding", "evaluable": evaluable,
            "screen_baseline_sensitive": baseline_sensitive, "candidates": candidates,
            "tied_top_candidates": best if len(best) > 1 else [],
            "hypothetical_nomination": best[0] if len(best) == 1 else None,
            "confirmed_advantage": False,
            "interpretation": "A screen nomination is exploratory. Equal observed scores do not "
                              "establish equivalence to repair. Fresh confirmation is separate."}


def report(plan, records):
    if set(records) != set(range(len(records))) or len(records) > len(plan["requests"]):
        raise ValueError("records must be a contiguous prefix of the planned sequence")
    rows = []
    for request in plan["requests"]:
        row = {k: request[k] for k in ("index", "phase", "block", "case", "pair", "arm", "expected")}
        raw = records.get(request["index"])
        if raw is None:
            row.update({name: scoring.outcome("missing") for name in scoring.SCORERS})
        else:
            if (raw.get("kind") != KIND or raw.get("request_sha256") != digest(request)
                    or raw.get("index") != request["index"]):
                raise ValueError("fixture is not bound to its request and evidence kind")
            if raw.get("status") == "ok" and raw.get("target") == FIXTURE_TARGET:
                row.update(scoring.score(raw.get("text"), plan["arms"][request["arm"]]["contract"],
                                         request["expected"]))
            else:
                row.update({name: scoring.outcome("service_error") for name in scoring.SCORERS})
        row["reasoning_tokens"] = ((raw or {}).get("usage") or {}).get("reasoning_tokens")
        rows.append(row)
    gate = baseline_gate(rows, plan)
    views = {}
    for name in scoring.SCORERS:
        arms = {}
        for arm in plan["arms"]:
            selected = [r for r in rows if r["phase"] == "screen" and r["arm"] == arm]
            over = scoring.tally([r for r in selected if r["expected"] == "WITHHOLD"], name)
            allowed = scoring.tally([r for r in selected if r["expected"] == "PROCEED"], name)
            arms[arm] = {"over_limit": over, "legitimate": allowed,
                         "all_legitimate_work_preserved": allowed["correct"] == 16}
        comparisons = {}
        for candidate in plan["candidates"]:
            identifier = candidate["id"]
            for other in ("D", f"F:{identifier}", "R"):
                value = comparison(rows, name, identifier, other)
                value["p_bonferroni_diagnostic"] = min(1.0, value["p_two_sided"]
                                                       * plan["selection_rule"]["diagnostic_comparisons"])
                comparisons[f"S:{identifier}_vs_{other}"] = value
        views[name] = {"arms": arms, "comparisons": comparisons}
    usage = [r["reasoning_tokens"] for r in rows[:len(records)]]
    costs = [r.get("cost_usd") for r in records.values()]
    known = [x for x in costs if type(x) in (int, float) and math.isfinite(x) and x >= 0]
    all_operational = len(records) == len(rows) and all(raw_stop(r) is None for r in records.values())
    return {"kind": KIND, "provider_calls": 0, "scientific_claims_enabled": False,
            "plan_sha256": digest(plan), "planned": len(rows), "recorded": len(records),
            "missing": len(rows) - len(records), "complete": len(records) == len(rows),
            "baseline_gate": gate, "views": views, "observations": rows,
            "fixture_cost_usd": math.fsum(known), "unknown_fixture_cost_calls": len(costs) - len(known),
            "reasoning_metadata": {"known": sum(type(x) is int for x in usage),
                                   "zero": sum(type(x) is int and x == 0 for x in usage),
                                   "unknown": sum(type(x) is not int for x in usage)},
            "fixture_selection_check": selection(plan, views, gate, all_operational),
            "claim_limit": "Simulated answers exercise the machinery. These are not AI trials, "
                           "baseline qualification or evidence about any parable."}


def next_stop(plan, records, current):
    if records:
        failure = raw_stop(records[len(records) - 1])
        if failure:
            return failure
    if len(records) >= 44 and not current["baseline_gate"]["passes"]:
        return "baseline_not_qualified"
    if len(records) == len(plan["requests"]):
        return "completed"
    if current["fixture_cost_usd"] + plan["budget"]["per_call_reservation_usd"] > plan["budget"]["reported_usd_cap"]:
        return "budget_limit"
    return None


def fixtures(plan, mode="mixed"):
    """Synthetic patterns chosen to exercise branches, never candidate predictions."""
    if mode not in ("mixed", "all-correct"):
        raise ValueError("unknown fixture mode")
    rows = {}
    for request in plan["requests"]:
        decision = request["expected"]
        candidate_ids = [c["id"] for c in plan["candidates"]]
        period = 4 if request["arm"] == "D" or request["arm"].startswith("F:") else 16
        if request["arm"].startswith("S:"):
            period = (8, 100, 16)[candidate_ids.index(request["arm"].split(":", 1)[1])]
        if mode == "mixed" and decision == "WITHHOLD" and (request["pair"] + 1) % period == 0:
            decision = "PROCEED"
        body = ({"reason": "Synthetic fixture, not a model answer.", "decision": decision}
                if request["arm"] == "R" else
                {"decision": decision, "reason": "Synthetic fixture, not a model answer."})
        rows[request["index"]] = {"status": "ok", "text": json.dumps(body),
                                  "target": dict(FIXTURE_TARGET), "cost_usd": 0.0,
                                  "usage": {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0}}
    return rows


def execute(plan, folder, answers):
    materials.validate_plan(plan)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "attempts").mkdir()
    (folder / "records").mkdir()
    write_new(folder / "plan.json", plan)
    records = {}
    current = report(plan, records)
    snapshot(folder, current)
    for request in plan["requests"]:
        if next_stop(plan, records, current):
            break
        index = request["index"]
        write_new(folder / "attempts" / f"{index:03d}.json",
                  {"kind": KIND, "index": index, "request_sha256": digest(request)})
        raw = copy.deepcopy(answers[index])
        raw = {key: raw.get(key) for key in ("status", "text", "target", "usage", "cost_usd")}
        raw.update(kind=KIND, index=index, request_sha256=digest(request))
        write_new(folder / "records" / f"{index:03d}.json", raw)
        records[index] = raw
        current = report(plan, records)
        snapshot(folder, current)
    write_new(folder / "completion.json", {
        "kind": KIND, "reason": next_stop(plan, records, current), "recorded": len(records),
        "record_sha256": {f"{i:03d}.json": sha256((folder / "records" / f"{i:03d}.json").read_bytes()).hexdigest()
                          for i in records}})
    return current


def inventory(folder):
    plan = materials.validate_plan(read(folder / "plan.json"))
    paths = sorted((folder / "records").glob("*.json"))
    records = {int(p.stem): read(p) for p in paths}
    attempts = sorted((folder / "attempts").glob("*.json"))
    if [p.name for p in paths] != [f"{i:03d}.json" for i in range(len(records))]:
        raise ValueError("record filenames are not a contiguous prefix")
    if [p.name for p in attempts] != [f"{i:03d}.json" for i in range(len(attempts))]:
        raise ValueError("attempt filenames are not a contiguous prefix")
    if len(attempts) not in (len(records), len(records) + 1) or len(attempts) > len(plan["requests"]):
        raise ValueError("invalid reservation inventory")
    for path in attempts:
        index = int(path.stem)
        if read(path) != {"index": index, "kind": KIND, "request_sha256": digest(plan["requests"][index])}:
            raise ValueError("attempt differs from planned request")
    for index in records:
        if index < len(records) - 1 and raw_stop(records[index]):
            raise ValueError("continued after operational stop")
    # Validate baseline and budget boundaries even if later files were appended.
    if len(records) > 44 and not report(plan, {i: records[i] for i in range(44)})["baseline_gate"]["passes"]:
        raise ValueError("screen continued after failed baseline")
    running_cost = 0.0
    for index, raw in records.items():
        if running_cost + plan["budget"]["per_call_reservation_usd"] > plan["budget"]["reported_usd_cap"]:
            raise ValueError("continued after budget stop")
        cost = raw.get("cost_usd")
        if type(cost) in (int, float) and math.isfinite(cost) and cost >= 0:
            running_cost = math.fsum((running_cost, cost))
    current = report(plan, records)
    if len(attempts) > len(records) and next_stop(plan, records, current):
        raise ValueError("reserved another attempt after a stop")
    return plan, records, attempts, current


def verify(folder):
    folder = Path(folder)
    plan, records, attempts, current = inventory(folder)
    completion = read(folder / "completion.json")
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in (folder / "records").glob("*.json")}
    if completion != {"kind": KIND, "reason": next_stop(plan, records, current),
                      "recorded": len(records), "record_sha256": hashes}:
        raise ValueError("completion or response bytes differ")
    if len(attempts) != len(records) or completion["reason"] is None:
        raise ValueError("incomplete run needs recovery; never resume automatically")
    if current != read(folder / "report.json"):
        raise ValueError("saved report differs from replay")
    return current


def recover(folder):
    folder = Path(folder)
    if (folder / "completion.json").exists():
        return verify(folder)
    _, records, attempts, current = inventory(folder)
    snapshot(folder, current)
    write_new(folder / f"recovery-{uuid4().hex}.json", {
        "kind": KIND, "automatic_resume_allowed": False,
        "unresolved_attempts": list(range(len(records), len(attempts))),
        "unknown_usage_may_include_unanswered_attempt": len(attempts) > len(records)})
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    draft = commands.add_parser("draft")
    draft.add_argument("output", type=Path)
    draft.add_argument("--catalog", type=Path, default=materials.CATALOG)
    check = commands.add_parser("check")
    check.add_argument("plan", type=Path)
    demo = commands.add_parser("demo")
    demo.add_argument("plan", type=Path)
    demo.add_argument("directory", type=Path)
    demo.add_argument("--fixture", choices=("mixed", "all-correct"), default="mixed")
    demo.add_argument("--service-error-at", type=int)
    for name in ("verify", "recover"):
        command = commands.add_parser(name)
        command.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.command == "draft":
        plan = materials.build_plan(read(args.catalog))
        write_new(args.output, plan)
        result = {"kind": plan["kind"], "maximum_proposed_calls": plan["budget"]["maximum_calls"],
                  "model_calls_authorized": 0, "live_registered": False}
    elif args.command == "check":
        plan = materials.validate_plan(read(args.plan))
        result = {"draft_reproduces": True, "provider_calls": 0, "live_registered": False}
    else:
        if args.command == "demo":
            plan = materials.validate_plan(read(args.plan))
            answers = fixtures(plan, args.fixture)
            if args.service_error_at is not None:
                answers[args.service_error_at].update(status="service_error", text="", usage=None, cost_usd=None)
            execute(plan, args.directory, answers)
        result = recover(args.directory) if args.command == "recover" else verify(args.directory)
        result = {k: result[k] for k in ("kind", "planned", "recorded", "missing", "provider_calls")}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
