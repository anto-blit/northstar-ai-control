"""G4: separately registered Codex comparison on the complete G3 direct-case set."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "results/codex-repair"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


g3 = module("g4_original", ROOT / "experiments/repair-replication/run.py")
transport = module("g4_transport", HERE / "transport.py")
read, save, digest, require = g3.read, g3.save, g3.digest, g3.require


def requests_from(original):
    selected = [r for r in original["requests"] if r["phase"] == "replication" and r["model"] == "claude-sonnet-5"]
    return [dict(r, index=i, source_index=r["index"], model=transport.MODEL) for i, r in enumerate(selected)]


def freeze():
    g3.verify(emit=False)
    original = g3.checked_plan()
    probes = sorted((OUT / "preparation").glob("readiness-*.json"))
    require(probes and read(probes[-1])["operational"] and read(probes[-1])["result"].strip() == "OK", "Readiness must pass")
    files = [HERE / name for name in ("PROTOCOL.md", "run.py", "transport.py", "system.txt", "test_run.py")]
    source = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    plan = dict(schema=1, frozen_at=datetime.now(timezone.utc).isoformat(), requested_model=transport.MODEL,
                requested_effort=transport.EFFORT, model_identity="Requested model; resolved server snapshot not exposed by CLI",
                cli_version=subprocess.check_output([shutil.which("codex"), "--version"], text=True).strip(),
                source_sha256=source, original_plan_sha256=digest(ROOT / "results/repair-replication/plan.json"),
                preparation_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in probes},
                transport_options=transport.options("SYSTEM_FILE"), requests=requests_from(original), request_count=288,
                cases=96, pairs=48, concurrency=3, timeout_seconds=120, target_retries=0,
                input_token_guard=3000000, output_token_guard=100000, cost_usd=None,
                selection="All G3 direct cases; no outcome-based selection; G3 Sonnet request order retained",
                prior_results_known="G2 and the completed Claude continuation were known to the project before this registration")
    save(OUT / "plan.json", plan)
    checked_plan()
    print(json.dumps(dict(planned=288, plan_sha256=digest(OUT / "plan.json"))))


def checked_plan(root=ROOT):
    folder = root / "results/codex-repair"
    plan = read(folder / "plan.json")
    g3.check_hashes(root, plan["source_sha256"])
    g3.check_hashes(root, plan["preparation_sha256"])
    require(digest(root / "results/repair-replication/plan.json") == plan["original_plan_sha256"], "G3 plan changed")
    original = g3.checked_plan(root)
    require(plan["requests"] == requests_from(original), "Codex case/arm inventory or prompts changed")
    require(plan["request_count"] == len(plan["requests"]) == 288 and plan["pairs"] == 48 and plan["cases"] == 96, "Wrong sample size")
    require(plan["requested_model"] == transport.MODEL and plan["requested_effort"] == transport.EFFORT, "Codex model settings changed")
    require(plan["transport_options"] == transport.options("SYSTEM_FILE"), "Transport settings changed")
    systems = {r["system"] for r in plan["requests"]}
    require(systems == {(root / "experiments/codex-repair/system.txt").read_text(encoding="utf-8").strip()}, "System instruction changed")
    return plan


def register():
    plan = checked_plan()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], text=True).split()[0]
    require(commit == remote, "Registration commit must be public")
    frozen = dict(plan["source_sha256"], **plan["preparation_sha256"])
    frozen["results/codex-repair/plan.json"] = digest(OUT / "plan.json")
    for path, expected in frozen.items():
        require(sha256(subprocess.check_output(["git", "show", commit + ":" + path])).hexdigest() == expected, "Published bytes differ: " + path)
    save(OUT / "registration.json", dict(public_commit=commit, registered_at=datetime.now(timezone.utc).isoformat(),
                                         plan_sha256=digest(OUT / "plan.json")))
    print(json.dumps(dict(public_commit=commit)))


def check_response(request, record, plan, registration, root):
    require(record["request_index"] == request["index"] and record["prompt"] == request["prompt"]
            and record["prompt_sha256"] == request["prompt_sha256"], "Codex response request mismatch")
    require(record["requested_model"] == plan["requested_model"] and record["requested_effort"] == plan["requested_effort"], "Codex response model mismatch")
    require(record["started_at"] >= max(plan["frozen_at"], registration["registered_at"]), "Response predates public registration")
    require(record["system_sha256"] == digest(root / "experiments/codex-repair/system.txt"), "Response system changed")
    if record["operational"]:
        require(record["returncode"] == 0 and not record["errors"] and not record["tool_or_unexpected_item"]
                and record["event_types"].count("thread.started") == 1 and record["event_types"].count("turn.completed") == 1
                and record["completed_item_types"].count("agent_message") >= 1 and record["usage"] is not None,
                "Invalid operational-response claim")


def decision(record):
    if not record or not record["operational"]:
        return None
    # Adapt only in memory to reuse the exact frozen G3 JSON parser. No provider usage or model identity is fabricated in saved evidence.
    return g3.executor.decision(dict(result=record["result"], returncode=0, is_error=False,
                                    modelUsage={transport.MODEL: {}}), transport.MODEL)


def usage_totals(records):
    return {key: sum((r.get("usage") or {}).get(key, 0) for r in records)
            for key in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens")}


def compute_report(root=ROOT):
    folder = root / "results/codex-repair"
    plan, registration = checked_plan(root), read(folder / "registration.json")
    require(registration["plan_sha256"] == digest(folder / "plan.json"), "Registered Codex plan changed")
    cases = {c["id"]: c for c in read(root / "results/repair-replication/cases.json")["cases"]}
    expected_files = {f"{r['index']:03}.json" for r in plan["requests"]}
    actual_files = {p.name for p in (folder / "responses").glob("*.json")}
    require(actual_files <= expected_files, "Unexpected extra target responses")
    rows, records, thread_ids = [], [], []
    for request in plan["requests"]:
        path = folder / "responses" / f"{request['index']:03}.json"
        record = read(path) if path.exists() else None
        if record:
            check_response(request, record, plan, registration, root)
            records.append(record)
            if record.get("thread_id_sha256"):
                thread_ids.append(record["thread_id_sha256"])
        choice = decision(record)
        case = cases[request["case_id"]]
        rows.append(dict(index=request["index"], case_id=case["id"], pair=case["pair"], condition=request["condition"],
                         expected=case["expected"], decision=choice, correct=choice == case["expected"],
                         operational=bool(record and record["operational"]), committed=None, cost_usd=0.0))
    require(len(thread_ids) == len(set(thread_ids)), "Target threads must be distinct")
    answered = sum(r["operational"] for r in rows)
    summary = g3.summarize(rows, answered == 288)
    for row in summary["conditions"].values():
        row["known_cost_usd"] = None  # CLI returns token usage, not a dollar charge.
    for row in rows:
        row["cost_usd"] = None
    artifacts = sorted((folder / "responses").glob("*.json")) + [folder / "registration.json"]
    if (folder / "stop.json").exists():
        artifacts.append(folder / "stop.json")
    preparation = [read(root / path) for path in plan["preparation_sha256"]]
    return dict(schema=1, plan_sha256=digest(folder / "plan.json"), public_commit=registration["public_commit"],
                requested_model=plan["requested_model"], model_identity=plan["model_identity"],
                planned=288, attempted=len(records), answered=answered, all_answered=answered == 288,
                summary=summary, observations=rows, target_usage=usage_totals(records), total_usage=usage_totals(records + preparation),
                dollar_cost=None, unique_target_threads=len(thread_ids),
                artifact_sha256={p.relative_to(folder).as_posix(): digest(p) for p in artifacts})


def verify(root=ROOT, emit=True):
    folder = root / "results/codex-repair"
    report = read(folder / "report.json")
    g3.check_hashes(root, {"results/codex-repair/" + p: h for p, h in report["artifact_sha256"].items()})
    rebuilt = compute_report(root)
    require(report == rebuilt, "Codex report does not reproduce")
    if emit:
        print(json.dumps({k: v for k, v in report.items() if k not in ("observations", "artifact_sha256")}, indent=2))
    return report


def execute():
    plan, registration = checked_plan(), read(OUT / "registration.json")
    require(registration["plan_sha256"] == digest(OUT / "plan.json"), "Registration changed")
    require(not (OUT / "report.json").exists() and not (OUT / "stop.json").exists(), "Run already finalized")
    require(subprocess.check_output([shutil.which("codex"), "--version"], text=True).strip() == plan["cli_version"], "Codex CLI version changed")
    records = [read(p) for p in sorted((OUT / "responses").glob("*.json"))]
    preparation = [read(ROOT / p) for p in plan["preparation_sha256"]]
    pending = [r for r in plan["requests"] if not (OUT / "responses" / f"{r['index']:03}.json").exists()]
    started, stop = time.monotonic(), None
    with ThreadPoolExecutor(max_workers=3) as pool:
        for offset in range(0, len(pending), 3):
            total = usage_totals(records + preparation)
            if total["input_tokens"] >= plan["input_token_guard"] or total["output_tokens"] >= plan["output_token_guard"]:
                stop = "declared token guard reached"
                break
            batch = [(r, pool.submit(transport.call, r["prompt"], plan["timeout_seconds"])) for r in pending[offset:offset+3]]
            for request, future in batch:
                record = dict(future.result(), request_index=request["index"])
                save(OUT / "responses" / f"{request['index']:03}.json", record)
                check_response(request, record, plan, registration, ROOT)
                records.append(record)
                if not record["operational"]:
                    stop = "operational failure; every submitted response retained without retry"
            if (offset+3) % 12 == 0 or stop:
                print(json.dumps(dict(attempted=len(records), planned=288, elapsed_seconds=round(time.monotonic()-started, 1), stop=stop)), flush=True)
            if stop:
                break
    if stop:
        save(OUT / "stop.json", dict(reason=stop, recorded_at=datetime.now(timezone.utc).isoformat()))
    report = compute_report()
    save(OUT / "report.json", report)
    verify(emit=False)
    print(json.dumps({k: v for k, v in report.items() if k not in ("observations", "artifact_sha256")}, indent=2))


if __name__ == "__main__":
    {"freeze": freeze, "register": register, "run": execute, "verify": verify}[sys.argv[1]]()
