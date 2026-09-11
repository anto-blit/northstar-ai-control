"""Continue only unanswered G3 slots; preserve every answer and quota attempt."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "results/repair-continuation"
OLD = ROOT / "results/repair-replication"
spec = importlib.util.spec_from_file_location("g3c_original", ROOT / "experiments/repair-replication/run.py")
g3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g3)
read, save, digest, require = g3.read, g3.save, g3.digest, g3.require
NOT_BEFORE = "2026-09-11T06:50:05+00:00"


def quota_only(record):
    return bool(record and record.get("is_error") is True and record.get("returncode") not in (None, 0)
                and not record.get("modelUsage") and isinstance(record.get("result"), str)
                and record["result"].startswith("You've hit your session limit"))


def choose(original, attempts):
    """Selection never consults expected labels, correctness or JSON parsing."""
    selected = original if original and not quota_only(original) else None
    for record in attempts:
        require(selected is None, "A returned answer cannot be replaced by another attempt")
        if not quota_only(record):
            selected = record
    return selected


def freeze():
    old_report = g3.verify(emit=False)
    old_plan = read(OLD / "plan.json")
    retained, eligible = [], []
    for request in old_plan["requests"]:
        path = OLD / "responses" / f"{request['index']:03}.json"
        record = read(path) if path.exists() else None
        if record and not quota_only(record):
            require(g3.operational(record, request["model"]), "Unexpected original non-quota operational failure")
            retained.append(request["index"])
        else:
            eligible.append(request["index"])
    require(len(retained) == 27 and len(eligible) == 693, "Original interrupted inventory changed")
    files = [HERE / name for name in ("PROTOCOL.md", "run.py", "test_run.py")]
    plan = dict(schema=1, frozen_at=datetime.now(timezone.utc).isoformat(), not_before=NOT_BEFORE,
                original_plan_sha256=digest(OLD / "plan.json"), original_report_sha256=digest(OLD / "report.json"),
                source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in files},
                retained_indices=retained, eligible_indices=eligible, original_known_cost_usd=old_report["total_known_cost_usd"],
                max_new_quota_attempts_per_slot=3, total_known_usage_guard_usd=15, request_slots=720)
    save(OUT / "plan.json", plan)
    print(json.dumps(dict(retained=len(retained), eligible=len(eligible), not_before=NOT_BEFORE, plan_sha256=digest(OUT / "plan.json"))))


def checked_plan(root=ROOT):
    folder, old = root / "results/repair-continuation", root / "results/repair-replication"
    plan = read(folder / "plan.json")
    g3.check_hashes(root, plan["source_sha256"])
    require(digest(old / "plan.json") == plan["original_plan_sha256"] and digest(old / "report.json") == plan["original_report_sha256"], "Original frozen run changed")
    g3.verify(root, emit=False)
    return plan, read(old / "plan.json")


def register():
    checked_plan()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], text=True).split()[0]
    committed = subprocess.check_output(["git", "show", commit + ":results/repair-continuation/plan.json"])
    require(commit == remote and g3.sha256(committed).hexdigest() == digest(OUT / "plan.json"), "Continuation plan must be public before registration")
    save(OUT / "registration.json", dict(registered_at=datetime.now(timezone.utc).isoformat(), public_commit=commit,
                                        plan_sha256=digest(OUT / "plan.json")))
    print(json.dumps(dict(public_continuation_commit=commit)))


def ready():
    plan, old_plan = checked_plan()
    registration = read(OUT / "registration.json")
    require(registration["plan_sha256"] == digest(OUT / "plan.json"), "Registered continuation changed")
    require(datetime.now(timezone.utc) >= datetime.fromisoformat(plan["not_before"]), "Requested waiting period has not ended")
    ordinal = len(list((OUT / "readiness").glob("*.json")))
    probes = []
    for model_name in old_plan["models"]:
        require(current_usage() < plan["total_known_usage_guard_usd"], "Known usage guard reached before readiness probe")
        record = g3.transport.call("Reply with exactly OK.", model_name, budget="0.10", timeout=120)
        save(OUT / "readiness" / f"{ordinal:03}.json", record)
        ordinal += 1
        probes.append(g3.operational(record, model_name))
    require(all(probes), "Both models must be available before target submissions")
    print("Both exact models are available; readiness probes preserved.", flush=True)


def histories(root, request):
    index = request["index"]
    old_path = root / "results/repair-replication/responses" / f"{index:03}.json"
    original = read(old_path) if old_path.exists() else None
    paths = sorted((root / "results/repair-continuation/attempts").glob(f"{index:03}-*.json"))
    attempts = [read(path) for path in paths]
    selected = choose(original, attempts)
    selected_path = old_path if original and not quota_only(original) else next((p for p, r in zip(paths, attempts) if not quota_only(r)), None)
    return original, paths, attempts, selected, selected_path


def current_usage(root=ROOT):
    folder = root / "results/repair-continuation"
    plan = read(folder / "plan.json")
    files = list((folder / "attempts").glob("*.json")) + list((folder / "readiness").glob("*.json"))
    return math.fsum([plan["original_known_cost_usd"]] + [read(p).get("total_cost_usd") or 0.0 for p in files])


def check_new_response(request, record, plan, registration):
    g3.check_response(request, record, dict(frozen_at=plan["frozen_at"]), registration)
    require(record["started_at"] >= plan["not_before"], "Continuation response predates wait boundary")


def execute():
    require(not (OUT / "report.json").exists(), "Continuation already has a final report")
    ready()
    plan, old_plan = checked_plan()
    registration = read(OUT / "registration.json")
    requests, pending = old_plan["requests"], []
    for request in requests:
        original, paths, attempts, selected, _ = histories(ROOT, request)
        if selected is None and len(attempts) < plan["max_new_quota_attempts_per_slot"]:
            require(request["index"] in plan["eligible_indices"], "Retained answer scheduled again")
            pending.append(request)
    db_folder = ROOT / "study-runs/repair-continuation"
    db_folder.mkdir(parents=True, exist_ok=True)
    ledger = g3.executor.BookingLedger(db_folder / "bookings.sqlite3")
    try:
        # Restore previously selected decisions into an isolated continuation ledger.
        for request in requests:
            _, _, _, selected, source = histories(ROOT, request)
            if selected and request["phase"] == "execution":
                record_effect(ledger, request, selected, source)
        stopped, consecutive_errors = None, 0
        started = time.monotonic()
        with ThreadPoolExecutor(max_workers=3) as pool:
            for offset in range(0, len(pending), 3):
                if current_usage() >= plan["total_known_usage_guard_usd"]:
                    stopped = "known usage guard"
                    break
                batch = [(r, pool.submit(g3.transport.call, r["prompt"], r["model"], system=r["system"], budget="0.10", timeout=120))
                         for r in pending[offset:offset+3]]
                for request, future in batch:
                    _, paths, _, _, _ = histories(ROOT, request)
                    path = OUT / "attempts" / f"{request['index']:03}-{len(paths)+1:02}.json"
                    record = dict(**future.result(), request_index=request["index"], prompt_sha256=request["prompt_sha256"], system=request["system"])
                    save(path, record)
                    check_new_response(request, record, plan, registration)
                    if quota_only(record):
                        stopped = "quota rejection; pause until access returns"
                    else:
                        consecutive_errors = 0 if g3.operational(record, request["model"]) else consecutive_errors+1
                        if consecutive_errors >= 3:
                            stopped = "three consecutive non-quota operational errors"
                        if request["phase"] == "execution":
                            record_effect(ledger, request, record, path)
                if (offset+len(batch)) % 12 == 0 or stopped:
                    print(json.dumps(dict(new_slots_attempted=offset+len(batch), pending_at_start=len(pending),
                        known_cost_usd=round(current_usage(), 6), elapsed_seconds=round(time.monotonic()-started, 1), stopped=stopped)), flush=True)
                if stopped:
                    break
        snapshot = dict(recorded_at=datetime.now(timezone.utc).isoformat(), reason=stopped or "pending slots exhausted", bookings=ledger.export())
        save(OUT / "checkpoints" / f"{len(list((OUT / 'checkpoints').glob('*.json'))):03}.json", snapshot)
    finally:
        ledger.close()
    result = compute_report()
    if result["answered_slots"] == 720 or not stopped or stopped != "quota rejection; pause until access returns":
        save(OUT / "report.json", result)
    else:
        save(OUT / "partial-reports" / f"{len(list((OUT / 'partial-reports').glob('*.json'))):03}.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("observations", "artifact_sha256")}, indent=2))


def record_effect(ledger, request, record, source):
    trace = ledger.dispatch(request["index"], request["case_id"], record, request["model"])
    trace.update(response_source=source.relative_to(ROOT).as_posix(), carried_from_original=source.is_relative_to(OLD))
    path = OUT / "execution" / f"{request['index']:03}.json"
    if path.exists():
        require(read(path) == trace, "Existing continuation effect changed")
    else:
        save(path, trace)


def compute_report(root=ROOT):
    plan, old_plan = checked_plan(root)
    folder = root / "results/repair-continuation"
    registration = read(folder / "registration.json")
    require(registration["plan_sha256"] == digest(folder / "plan.json"), "Continuation registration changed")
    cases = {c["id"]: c for c in read(root / "results/repair-replication/cases.json")["cases"]}
    ledger = g3.executor.BookingLedger()
    rows, new_quota, new_attempts = [], 0, 0
    try:
        for request in old_plan["requests"]:
            original, paths, attempts, selected, source = histories(root, request)
            require(len(paths) <= plan["max_new_quota_attempts_per_slot"], "Quota-only attempt cap exceeded")
            require(not paths or request["index"] in plan["eligible_indices"], "Original answer was retried")
            for record in attempts:
                check_new_response(request, record, plan, registration)
            new_quota += sum(quota_only(r) for r in attempts)
            new_attempts += len(attempts)
            case = cases[request["case_id"]]
            choice = g3.executor.decision(selected, request["model"])
            committed = None
            if request["phase"] == "execution":
                trace = ledger.dispatch(request["index"], case["id"], selected, request["model"])
                committed = trace["committed"]
                path = folder / "execution" / f"{request['index']:03}.json"
                if selected:
                    trace.update(response_source=source.relative_to(root).as_posix(), carried_from_original=source.is_relative_to(root / "results/repair-replication"))
                    require(path.exists() and read(path) == trace, "Continuation execution does not replay")
            rows.append(dict(index=request["index"], case_id=case["id"], pair=case["pair"], phase=case["phase"], model=request["model"], condition=request["condition"],
                expected=case["expected"], decision=choice, correct=choice == case["expected"], committed=committed,
                operational=g3.operational(selected, request["model"]), cost_usd=(selected.get("total_cost_usd") or 0.0) if selected else 0.0,
                response_source=source.relative_to(root).as_posix() if source else None))
        checkpoints = sorted((folder / "checkpoints").glob("*.json"))
        require(checkpoints and read(checkpoints[-1])["bookings"] == ledger.export(), "Continuation ledger does not replay")
        bookings = ledger.export()
    finally:
        ledger.close()
    answered = sum(r["operational"] for r in rows)
    phases = {phase: {m: g3.summarize([r for r in rows if r["phase"] == phase and r["model"] == m], answered == 720)
                     for m in old_plan["models"]} for phase in old_plan["phases"]}
    artifacts = [folder / "registration.json"]
    for name in ("attempts", "execution", "checkpoints", "readiness"):
        artifacts += sorted((folder / name).glob("*.json"))
    return dict(schema=1, plan_sha256=digest(folder / "plan.json"), public_continuation_commit=registration["public_commit"],
        original_report_sha256=plan["original_report_sha256"], planned_slots=720, retained_answers=27, new_attempts=new_attempts,
        original_quota_rejections=9, new_quota_rejections=new_quota, answered_slots=answered, all_answered=answered == 720,
        known_total_cost_usd=current_usage(root), phases=phases, bookings=bookings, observations=rows,
        artifact_sha256={p.relative_to(folder).as_posix(): digest(p) for p in artifacts})


def verify(root=ROOT, emit=True):
    folder = root / "results/repair-continuation"
    path = folder / "report.json"
    if not path.exists():
        partials = sorted((folder / "partial-reports").glob("*.json"))
        require(bool(partials), "No continuation report is available yet")
        path = partials[-1]
    report = read(path)
    g3.check_hashes(root, {"results/repair-continuation/"+p: h for p, h in report["artifact_sha256"].items()})
    require(report == compute_report(root), "Continuation report does not reproduce")
    if emit:
        print(json.dumps({k: v for k, v in report.items() if k not in ("observations", "artifact_sha256", "bookings")}, indent=2))
    return report


if __name__ == "__main__":
    {"freeze": freeze, "register": register, "ready": ready, "run": execute, "verify": verify}[sys.argv[1]]()
