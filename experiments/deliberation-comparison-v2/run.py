"""Corrected comparison machinery, with an offline-only command line.

No provider adapters are installed here. A future live study needs its own
target, qualified baseline and publication. G17 plans/results are read-only.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import math
import os
from uuid import uuid4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("deliberation_v2_scoring", HERE / "scoring.py")
scoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scoring)
KIND = "offline_harness_validation"
TARGET = {"provider": "synthetic", "model": "fixture-v1", "effort": None}
INPUTS = ("results/deliberation-comparison/stage-B/plan.json",
          "results/deliberation-comparison/stage-A/plan.json",
          "results/deliberation-comparison/stage-A2/plan.json",
          "results/story-confirmation-v3/plan.json")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def source_hashes():
    paths = [ROOT / p for p in INPUTS] + [HERE / n for n in ("run.py", "scoring.py")]
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in paths}


@lru_cache(maxsize=2)
def _frozen_requests(input_hashes):
    """Cache by checked input bytes, not by a mutable caller's plan."""
    old = read(ROOT / INPUTS[0])
    packets = {(r["case"], r["arm"]): r for r in read(ROOT / INPUTS[3])["requests"]}
    rows = []
    for entry in old["requests"]:
        packet = copy.deepcopy(packets[(entry["case"], entry["arm"])])
        packet["index"] = entry["index"]
        if any(packet[key] != value for key, value in entry.items()):
            raise ValueError("saved prompt packet differs from G17 B request")
        packet["system_sha256"] = sha256(packet["system"].encode()).hexdigest()
        rows.append(packet)
    used = {r["case"] for path in INPUTS[1:3] for r in read(ROOT / path)["requests"]}
    if used.intersection(r["case"] for r in rows):
        raise ValueError("comparison reuses qualification cases")
    return rows


def build_plan():
    """Use saved prompt packets directly; no old runner/transport is imported."""
    hashes = source_hashes()
    rows = copy.deepcopy(_frozen_requests(tuple(hashes[p] for p in INPUTS)))
    plan = {"version": 2, "kind": KIND, "live_registered": False,
            "target": dict(TARGET), "primary_scorer": "first_object",
            "scientific_claims_enabled": False, "source_sha256": hashes,
            "requests": rows, "budget_calls": 320,
            "stop_rule": "Stop at the first service error, timeout, interruption, "
                         "unknown usage/cost or transport mismatch. Preserve evidence. "
                         "No retries, added calls or automatic resume.",
            "consumer_policy": "First decision object, either key order. Later "
                               "corrections do not replace that decision. "
                               "Malformed/duplicate-key objects are not rescued."}
    validate_plan(plan)
    return plan


def validate_plan(plan):
    if (plan.get("version") != 2 or plan.get("kind") != KIND
            or plan.get("target") != TARGET or plan.get("live_registered") is not False
            or plan.get("scientific_claims_enabled") is not False
            or plan.get("primary_scorer") != "first_object"):
        raise ValueError("this version is an offline validation, not a live study")
    hashes = source_hashes()
    if plan.get("source_sha256") != hashes:
        raise ValueError("source/input hashes differ; do not reuse this run")
    rows = plan["requests"]
    if rows != _frozen_requests(tuple(hashes[p] for p in INPUTS)):
        raise ValueError("requests differ from frozen prompt packets")
    if len(rows) != plan.get("budget_calls") or len(rows) != 320:
        raise ValueError("expected exactly 320 requests")
    if [r["index"] for r in rows] != list(range(len(rows))):
        raise ValueError("request indices must be unique, contiguous and ordered")
    if Counter((r["arm"], r["expected"]) for r in rows) != Counter(
            {(arm, decision): 40 for arm in scoring.ARMS for decision in scoring.DECISIONS}):
        raise ValueError("unbalanced arm/case inventory")
    identities = set()
    for row in rows:
        identity = (row["case"], row["arm"])
        if identity in identities:
            raise ValueError("duplicate case/arm")
        identities.add(identity)
        if (sha256(row["prompt"].encode()).hexdigest() != row["prompt_sha256"]
                or sha256(row["system"].encode()).hexdigest() != row["system_sha256"]):
            raise ValueError("prompt/system does not match its hash")
    for start in range(0, len(rows), 4):
        block = rows[start:start + 4]
        if (len({(r["case"], r["pair"], r["block"], r["expected"]) for r in block}) != 1
                or {r["arm"] for r in block} != set(scoring.ARMS)):
            raise ValueError("four-arm paired block is incomplete or inconsistent")


def _finite_cost(value):
    return type(value) in (float, int) and math.isfinite(value) and value >= 0


def normalize(raw):
    """Copy only a provider-independent allowlist; unknown usage is never zero."""
    if not isinstance(raw, dict):
        return {"status": "service_error", "text": "", "error": "invalid_transport_record",
                "usage": None, "cost_usd": None, "target": dict(TARGET)}
    result = {key: copy.deepcopy(raw.get(key)) for key in
              ("status", "text", "target", "usage", "cost_usd")}
    if raw.get("status") == "service_error":
        result.update(status="service_error", error="provider_service_error")
    elif (raw.get("status") != "ok" or not isinstance(raw.get("text"), str)
          or raw.get("target") != TARGET):
        result.update(status="service_error", error="transport_contract_mismatch")
    usage = result.get("usage")
    if isinstance(usage, dict):
        result["usage"] = {name: usage.get(name) if type(usage.get(name)) is int
                           and usage[name] >= 0 else None for name in
                           ("input_tokens", "output_tokens", "reasoning_tokens")}
    else:
        result["usage"] = None
    if not _finite_cost(result.get("cost_usd")):
        result["cost_usd"] = None
    return result


def stop_reason(record):
    if record["status"] != "ok":
        return "service_error"
    usage = record.get("usage") or {}
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in
           ("input_tokens", "output_tokens", "reasoning_tokens")):
        return "unknown_usage"
    if record.get("cost_usd") is None:
        return "unknown_cost"
    return None


def report(plan, records):
    validate_plan(plan)
    if set(records) != set(range(len(records))) or len(records) > len(plan["requests"]):
        raise ValueError("records are not a contiguous prefix of registered requests")
    rows = []
    for request in plan["requests"]:
        row = {key: request[key] for key in ("index", "case", "pair", "block", "arm", "expected")}
        raw = records.get(request["index"])
        if raw is None:
            row.update({name: scoring.outcome("missing") for name in scoring.SCORERS})
            row.update(reasoning_tokens=None, cost_usd=None)
        else:
            if raw.get("request_sha256") != digest(request) or raw.get("kind") != KIND:
                raise ValueError("record is not bound to its request and evidence kind")
            if raw.get("status") == "ok":
                row.update(scoring.score(raw["text"], request["arm"], request["expected"]))
            else:
                row.update({name: scoring.outcome("service_error") for name in scoring.SCORERS})
            row["reasoning_tokens"] = (raw.get("usage") or {}).get("reasoning_tokens")
            row["cost_usd"] = raw.get("cost_usd")
        rows.append(row)
    views = {}
    for name in scoring.SCORERS:
        arms = {}
        for arm in scoring.ARMS:
            selected = [r for r in rows if r["arm"] == arm]
            forbidden = [r for r in selected if r["expected"] == "WITHHOLD"]
            legitimate = [r for r in selected if r["expected"] == "PROCEED"]
            useful = scoring.tally(legitimate, name)
            arms[arm] = {"over_limit": scoring.tally(forbidden, name), "legitimate": useful,
                         "all_legitimate_work_preserved": useful["correct"] == useful["planned"]}
        views[name] = {"arms": arms, "comparisons": {
            f"S_vs_{other}": scoring.compare(rows, name, other) for other in "FRD"}}
    measured = [r["reasoning_tokens"] for r in rows[:len(records)]
                if type(r["reasoning_tokens"]) is int and r["reasoning_tokens"] >= 0]
    costs = [r["cost_usd"] for r in rows[:len(records)] if _finite_cost(r["cost_usd"])]
    return {"version": 2, "kind": KIND, "plan_sha256": digest(plan),
            "planned": len(rows), "recorded": len(records), "missing": len(rows) - len(records),
            "complete": len(records) == len(rows), "views": views, "observations": rows,
            "reasoning_usage": {"known_calls": len(measured), "zero_calls": measured.count(0),
                                "unknown_recorded_calls": len(records) - len(measured)},
            "known_cost_usd": math.fsum(costs), "unknown_cost_calls": len(records) - len(costs),
            "provider_calls": 0, "scientific_claims_enabled": False,
            "claim_limit": "Synthetic offline validation only. Counts test the machinery; "
                           "they are not model performance or story-effectiveness evidence."}


def _write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _snapshot(folder, value):
    temp = folder / f"report-{uuid4().hex}.tmp"
    _write_new(temp, value)
    os.replace(temp, folder / "report.json")


def execute(plan, folder, transport):
    """Exercise the fixed sequence with an injected offline fixture transport.

    The transport receives prompt/system/target, never expected labels or arms.
    A new output directory is mandatory, including after an interrupted attempt.
    """
    validate_plan(plan)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "attempts").mkdir()
    (folder / "records").mkdir()
    _write_new(folder / "plan.json", plan)
    records, reason = {}, "completed"
    _snapshot(folder, report(plan, records))
    for request in plan["requests"]:
        index = request["index"]
        _write_new(folder / "attempts" / f"{index:03d}.json",
                   {"index": index, "request_sha256": digest(request), "kind": KIND})
        try:
            raw = normalize(transport(prompt=request["prompt"], system=request["system"],
                                      target=copy.deepcopy(plan["target"])))
        except (Exception, KeyboardInterrupt) as error:
            raw = {"status": "service_error", "text": "", "target": dict(TARGET),
                   "usage": None, "cost_usd": None, "error": type(error).__name__}
        raw.update(kind=KIND, index=index, request_sha256=digest(request))
        _write_new(folder / "records" / f"{index:03d}.json", raw)
        records[index] = raw
        _snapshot(folder, report(plan, records))
        if stop_reason(raw):
            reason = stop_reason(raw)
            break
    _write_new(folder / "completion.json", {"reason": reason, "recorded": len(records),
                "record_sha256": {f"{i:03d}.json": sha256((folder / "records" / f"{i:03d}.json").read_bytes()).hexdigest()
                                  for i in records}})
    return read(folder / "report.json")


def verify(folder):
    folder = Path(folder)
    plan, completion = read(folder / "plan.json"), read(folder / "completion.json")
    paths = sorted((folder / "records").glob("*.json"))
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    if hashes != completion["record_sha256"]:
        raise ValueError("record inventory or bytes changed")
    records = {int(p.stem): read(p) for p in paths}
    if completion["recorded"] != len(records):
        raise ValueError("completion count differs")
    attempts = sorted((folder / "attempts").glob("*.json"))
    if [p.stem for p in attempts] != [p.stem for p in paths]:
        raise ValueError("unresolved or missing attempt; never retry it automatically")
    for path in attempts:
        index = int(path.stem)
        if read(path) != {"index": index, "request_sha256": digest(plan["requests"][index]), "kind": KIND}:
            raise ValueError("attempt does not match registered request")
    for index, raw in records.items():
        if raw.get("index") != index:
            raise ValueError("response index differs")
        if index < len(records) - 1 and stop_reason(raw):
            raise ValueError("calls continued after a stop condition")
    reason = stop_reason(records[len(records) - 1]) if records else None
    expected = reason or ("completed" if len(records) == len(plan["requests"]) else "incomplete")
    if completion["reason"] != expected:
        raise ValueError("completion reason conflicts with the stored sequence")
    fresh = report(plan, records)
    if fresh != read(folder / "report.json"):
        raise ValueError("report differs from stored records")
    return fresh


def recover(folder):
    """Rebuild a crash checkpoint offline. Unanswered reservations stay unresolved."""
    folder = Path(folder)
    if (folder / "completion.json").exists():
        return verify(folder)
    plan = read(folder / "plan.json")
    validate_plan(plan)
    paths = sorted((folder / "records").glob("*.json"))
    records = {int(p.stem): read(p) for p in paths}
    attempts = sorted((folder / "attempts").glob("*.json"))
    if [int(p.stem) for p in attempts] != list(range(len(attempts))):
        raise ValueError("attempts are not a contiguous prefix")
    if len(attempts) not in (len(records), len(records) + 1):
        raise ValueError("unexpected unresolved attempt inventory")
    for path in attempts:
        index = int(path.stem)
        if read(path) != {"index": index, "kind": KIND,
                          "request_sha256": digest(plan["requests"][index])}:
            raise ValueError("attempt differs from plan")
    fresh = report(plan, records)
    _snapshot(folder, fresh)
    recovery = {"kind": KIND, "automatic_resume_allowed": False,
                "unresolved_attempts": [i for i in range(len(attempts)) if i not in records],
                "unknown_usage_may_include_unanswered_attempt": len(attempts) > len(records),
                "record_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}}
    _write_new(folder / f"recovery-{uuid4().hex}.json", recovery)
    return fresh


def fixture_transport(plan):
    """All-correct synthetic replies. Never described as model results."""
    lookup = {r["prompt"]: r for r in plan["requests"]}
    def reply(*, prompt, system, target):
        row = lookup[prompt]
        body = ({"reason": "Synthetic fixture.", "decision": row["expected"]} if row["arm"] == "R"
                else {"decision": row["expected"], "reason": "Synthetic fixture."})
        return {"status": "ok", "text": json.dumps(body), "target": target,
                "usage": {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0}, "cost_usd": 0}
    return reply


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "verify", "recover"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.command == "demo":
        plan = build_plan()
        execute(plan, args.directory, fixture_transport(plan))
    result = recover(args.directory) if args.command == "recover" else verify(args.directory)
    print(json.dumps({key: result[key] for key in
                      ("kind", "planned", "recorded", "missing", "provider_calls", "scientific_claims_enabled")}))
