"""G5-C: preserve G5 and attempt only its thirty entirely unstarted episodes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REL = Path("results/story-continuation")
SOURCES = ["experiments/story-continuation/" + name for name in ("run.py", "PROTOCOL.md", "test_run.py")]
RETAINED = list(range(6))
ELIGIBLE = list(range(6, 36))


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def original(root=ROOT):
    spec = importlib.util.spec_from_file_location("g5c_original", root / "experiments/story-distillation/run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    module.HERE = root / "experiments/story-distillation"
    # Resolve catalog inputs against this checkout, including temporary fixtures.
    module.load_catalog = lambda path=None: read(Path(path) if path is not None else root / "curriculum/aesop-v1.json")
    return module


def provider_refusal(record):
    message = record.get("result")
    return bool(record.get("is_error") is True and type(record.get("returncode")) is int
                and record["returncode"] != 0 and isinstance(message, str)
                and message.startswith("API Error:") and "can't help with this" in message
                and "https://www.anthropic.com/legal/aup" in message and "Details:" in message)


def known_cost(record):
    value = record.get("total_cost_usd")
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def should_stop(records, new_cost, limit=5.0):
    g5 = original()
    return new_cost >= limit or any(not known_cost(r) or
        (not g5.operational(r) and not provider_refusal(r)) for r in records)


def episode_status(g5, case, records):
    if not records:
        return "unstarted"
    if any(not g5.operational(r) for r in records):
        return "provider_refusal" if all(g5.operational(r) or provider_refusal(r) for r in records) else "service_failure"
    first = g5.parse_response(records[0], {"inspect", "finish_from_note", "cancel"})
    if first is None:
        return "invalid"
    if first == "inspect" and len(records) == 1:
        return "partial"
    return "invalid" if g5.score_episode(case, records)["invalid"] else "valid_decision"


def register(root=ROOT):
    g5 = original(root)
    report = g5.verify(root)
    plan = g5.checked_plan(root)
    if [r["index"] for r in report["observations"]] != RETAINED or len(plan["episodes"]) != 36:
        raise ValueError("Expected exactly six original attempted episodes")
    paths = g5.SOURCES + sorted(p.relative_to(root).as_posix() for p in
                               (root / "results/story-distillation").rglob("*.json"))
    frozen = {path: sha(root / path) for path in paths}
    value = dict(schema_version=1, study="G5-C development continuation",
                 created_at=datetime.now(timezone.utc).isoformat(), retained_indices=RETAINED,
                 eligible_indices=ELIGIBLE, original_sha256=frozen,
                 source_sha256={p: sha(root / p) for p in SOURCES},
                 maximum_new_calls=60, per_call_budget_usd="0.08", maximum_new_known_cost_usd=5.0,
                 original_known_cost_usd=report["known_cost_usd"], original_observations_known=6,
                 interpretation="Operational amendment after five successes and one refusal; no independent replication.")
    dump(root / REL / "plan.json", value)
    return value


def checked_plan(root=ROOT):
    plan = read(root / REL / "plan.json")
    if plan["retained_indices"] != RETAINED or plan["eligible_indices"] != ELIGIBLE:
        raise ValueError("Continuation inventory changed")
    if set(plan["source_sha256"]) != set(SOURCES):
        raise ValueError("Continuation source inventory changed")
    g5 = original(root)
    expected = set(g5.SOURCES) | {p.relative_to(root).as_posix() for p in
                               (root / "results/story-distillation").rglob("*.json")}
    if set(plan["original_sha256"]) != expected:
        raise ValueError("Original evidence inventory changed")
    for path, expected_hash in {**plan["source_sha256"], **plan["original_sha256"]}.items():
        if sha(root / path) != expected_hash:
            raise ValueError("Frozen continuation input changed: " + path)
    report = g5.verify(root)
    if [r["index"] for r in report["observations"]] != RETAINED:
        raise ValueError("Original attempts changed")
    return plan


def run_episode(row, g5, out, call_fn=None):
    if row["index"] not in ELIGIBLE:
        raise ValueError("Cannot retry a retained original episode")
    folder = out / "episodes" / f"{row['index']:03}"
    folder.mkdir(parents=True, exist_ok=False)  # Attempt reservation: even a crash cannot silently retry.
    case = next(c for c in g5.cases() if c["id"] == row["case"])
    records = []
    for stage in (0, 1):
        prompt = g5.prompt(case, row["arm"], stage)
        try:
            record = (call_fn or g5.call)(prompt)
        except Exception as error:
            # Do not publish arbitrary exception messages, which can contain account data.
            record = dict(result="", is_error=True, returncode=None, error=type(error).__name__,
                          prompt=prompt, prompt_sha256=sha256(prompt.encode()).hexdigest(),
                          requested_model=g5.MODEL, system_sha256=sha256(g5.SYSTEM.encode()).hexdigest())
        dump(folder / f"response-{stage}.json", record)
        records.append(record)
        if not g5.operational(record) or (stage == 0 and g5.parse_response(record, {"inspect", "finish_from_note", "cancel"}) != "inspect"):
            break
    dump(folder / "ledger.json", {"case": case["id"], "arm": row["arm"],
                                  "effects": g5.score_episode(case, records)["effects"]})
    return records


def summarize(observations):
    statuses = ("valid_decision", "invalid", "provider_refusal", "service_failure", "partial", "unstarted")
    summary = {}
    for arm in "DFS":
        rows = [r for r in observations if r["arm"] == arm]
        summary[arm] = dict(planned=len(rows), **{s: sum(r["status"] == s for r in rows) for s in statuses},
                            correct=sum(r["correct"] for r in rows), useful=sum(r["useful"] for r in rows),
                            unsafe_proposals=sum(r["unsafe_proposal"] for r in rows),
                            premature_proposals=sum(r["premature_proposal"] for r in rows),
                            calls=sum(r["calls"] for r in rows), model_answers=sum(r["operational_answers"] for r in rows),
                            local_effects=sum(len(r["effects"]) for r in rows))
    comparisons = {}
    for other in "FD":
        wins = losses = ties = 0
        excluded = []
        for case_id in dict.fromkeys(r["case"] for r in observations):
            pair = {r["arm"]: r for r in observations if r["case"] == case_id}
            if any(pair[a]["status"] != "valid_decision" for a in ("S", other)):
                excluded.append({"case": case_id, "statuses": {a: pair[a]["status"] for a in ("S", other)}})
                continue
            delta = int(pair["S"]["correct"]) - int(pair[other]["correct"])
            wins += delta > 0
            losses += delta < 0
            ties += delta == 0
        comparisons["S_vs_" + other] = dict(wins=wins, losses=losses, ties=ties, paired=wins+losses+ties, excluded=excluded)
    return summary, comparisons


def make_report(root=ROOT):
    plan = checked_plan(root)
    g5 = original(root)
    observations, hashes = [], {}
    costs = {"retained": 0.0, "new": 0.0}
    unknown = 0
    episode_root = root / REL / "episodes"
    if episode_root.exists() and any(p.name not in {f"{i:03}" for i in ELIGIBLE} or not p.is_dir() for p in episode_root.iterdir()):
        raise ValueError("Unexpected continuation episode")
    for row in g5.checked_plan(root)["episodes"]:
        retained = row["index"] in RETAINED
        folder = (root / "results/story-distillation" if retained else root / REL) / "episodes" / f"{row['index']:03}"
        paths = sorted(folder.glob("response-*.json"))
        if folder.exists() and not paths:
            raise ValueError("Incomplete episode attempt")
        if folder.exists() and {p.name for p in folder.iterdir()} != {p.name for p in paths} | {"ledger.json"}:
            raise ValueError("Incomplete or unexpected episode artifacts")
        if [p.name for p in paths] not in ([], ["response-0.json"], ["response-0.json", "response-1.json"]):
            raise ValueError("Unexpected response sequence")
        records = [read(p) for p in paths]
        case = next(c for c in g5.cases() if c["id"] == row["case"])
        for stage, (path, record) in enumerate(zip(paths, records)):
            if record["prompt"] != g5.prompt(case, row["arm"], stage) or record["prompt_sha256"] != row["prompt_sha256"][stage]:
                raise ValueError("Response prompt changed")
            if record["system_sha256"] != sha256(g5.SYSTEM.encode()).hexdigest() or record["requested_model"] != g5.MODEL:
                raise ValueError("Transport identity changed")
            hashes[path.relative_to(root).as_posix()] = sha(path)
            if known_cost(record):
                costs["retained" if retained else "new"] += record["total_cost_usd"]
            else:
                unknown += 1
        if len(records) == 2 and g5.parse_response(records[0], {"inspect", "finish_from_note", "cancel"}) != "inspect":
            raise ValueError("Second call without inspection")
        scored = g5.score_episode(case, records)
        if paths:
            ledger = folder / "ledger.json"
            if read(ledger) != {"case": case["id"], "arm": row["arm"], "effects": scored["effects"]}:
                raise ValueError("Local effects do not replay")
            hashes[ledger.relative_to(root).as_posix()] = sha(ledger)
        observations.append({**row, **scored, "status": episode_status(g5, case, records),
                             "retained": retained, "calls": len(records),
                             "operational_answers": sum(g5.operational(r) for r in records)})
    summary, comparisons = summarize(observations)
    publication = root / REL / "publication.json"
    return dict(schema_version=1, study="G5-C development continuation", summary=summary, comparisons=comparisons,
                observations=observations, planned_episodes=36,
                all_adjudicated=all(r["status"] not in {"partial", "unstarted"} for r in observations),
                all_answered=all(r["status"] in {"valid_decision", "invalid"} for r in observations),
                all_valid_decisions=all(r["status"] == "valid_decision" for r in observations),
                known_cost_usd=round(sum(costs.values()), 9), new_known_cost_usd=round(costs["new"], 9),
                calls_with_unknown_cost=unknown, artifact_sha256=hashes, plan_sha256=sha(root / REL / "plan.json"),
                public_commit=read(publication)["commit"] if publication.exists() else None,
                finding="Conditional paired development comparison; refusals count against completion, not as moral errors. No global-risk estimate.")


def verify(root=ROOT):
    report = make_report(root)
    for name in ("report.json", "stop.json"):
        path = root / REL / name
        if path.exists() and (read(path) if name == "report.json" else read(path)["partial"]) != report:
            raise ValueError("Continuation report or evidence changed")
    return report


def run():
    plan = checked_plan()
    out = ROOT / REL
    if any((out / p).exists() for p in ("publication.json", "episodes", "report.json", "stop.json")):
        raise ValueError("Continuation already started; no retries or silent resumption")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True).split()[0]
    if commit != remote:
        raise ValueError("Publish the continuation before target calls")
    for path in list(plan["source_sha256"]) + list(plan["original_sha256"]) + [(REL / "plan.json").as_posix()]:
        if subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT) != (ROOT / path).read_bytes():
            raise ValueError("Public bytes differ: " + path)
    dump(out / "publication.json", {"commit": commit, "checked_at": datetime.now(timezone.utc).isoformat()})
    g5 = original()
    rows = [r for r in g5.checked_plan()["episodes"] if r["index"] in ELIGIBLE]
    for start in range(0, len(rows), 3):
        with ThreadPoolExecutor(max_workers=3) as pool:
            responses = list(pool.map(lambda row: run_episode(row, g5, out), rows[start:start+3]))
        report = make_report()
        print(json.dumps({"attempted": sum(r["status"] != "unstarted" for r in report["observations"]),
                          "new_known_cost_usd": report["new_known_cost_usd"], "summary": report["summary"]}), flush=True)
        if should_stop([r for episode in responses for r in episode], report["new_known_cost_usd"], plan["maximum_new_known_cost_usd"]):
            dump(out / "stop.json", {"reason": "Unclassified service failure, unknown usage or cost guard; no retries.", "partial": report})
            return
    dump(out / "report.json", report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["register", "run", "verify"])
    command = parser.parse_args().command
    if command == "run":
        run()
    else:
        result = register() if command == "register" else verify()
        print(json.dumps({k: v for k, v in result.items() if k not in {"observations", "artifact_sha256", "source_sha256", "original_sha256"}}, indent=2))
