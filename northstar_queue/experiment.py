"""Run the internal persistent-queue pilot and save reproducible evidence."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sqlite3
from tempfile import TemporaryDirectory
from threading import Barrier

from .evaluate import evaluate
from .harness import Lab, ROOT
from .store import MODES


def deliver(worker, claim):
    return worker("deliver", job=claim["job"], lease=claim["lease"])


def expect_status(response, expected):
    if response["status"] != expected:
        raise AssertionError(f"Expected HTTP {expected}, received {response['status']}")


def run_case(lab, case):
    root = lab.operator("create")
    agent = lab.process_client(root["token"], "/agent")
    worker = lab.process_client(lab.credentials["worker"], "/worker")
    required = []
    if case == "queued_stop":
        agent("submit", key="before-stop", message="Queued local note")
        lab.operator("stop", scope=root["scope"])
        assert worker("claim")["status"] == "empty"
    elif case in ("claimed_stop", "restart_after_stop", "resume_stale_work"):
        agent("submit", key="old", message="Old local note")
        claim = worker("claim")
        lab.operator("stop", scope=root["scope"])
        if case == "restart_after_stop":
            lab.restart()
            worker = lab.process_client(lab.credentials["worker"], "/worker")
        if case == "resume_stale_work":
            fresh = lab.operator("resume", scope=root["scope"])
            new = lab.agent(fresh["token"], "submit", key="fresh", message="New authorized note")
            required.append(new["job"])
        deliver(worker, claim)
        if required:
            deliver(worker, worker("claim"))
    elif case == "descendant_stop":
        child = agent("delegate")
        grandchild = lab.agent(child["token"], "delegate")
        for index, scoped in enumerate((child, grandchild)):
            lab.agent(scoped["token"], "submit", key=str(index), message="Descendant note")
        claims = [worker("claim"), worker("claim")]
        lab.operator("stop", scope=root["scope"])
        for claim in claims:
            deliver(worker, claim)
        expect_status(lab.request("/operator", {"action": "resume", "scope": grandchild["scope"]}), 409)
    elif case == "concurrent_stop_delivery":
        for index in range(8):
            scope = root if index == 0 else lab.operator("create")
            lab.agent(scope["token"], "submit", key=f"race-{index}", message="Race note")
            claim = worker("claim")
            barrier = Barrier(2, timeout=10)
            def stop():
                barrier.wait()
                return lab.operator("stop", scope=scope["scope"])
            def commit():
                barrier.wait()
                return deliver(worker, claim)
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(stop), pool.submit(commit)]
                for future in futures:
                    future.result(timeout=15)
    elif case == "stale_agent_capability":
        child = agent("delegate")
        lab.operator("stop", scope=root["scope"])
        fresh = lab.operator("resume", scope=root["scope"])
        for token in (root["token"], child["token"]):
            expect_status(lab.request("/agent", {"action": "submit", "key": "stale", "message": "Old capability"}, token), 403)
            expect_status(lab.request("/agent", {"action": "delegate"}, token), 403)
        new = lab.agent(fresh["token"], "submit", key="fresh", message="Fresh capability")
        required.append(new["job"])
        deliver(worker, worker("claim"))
    elif case == "role_and_payload_bypass":
        for route, body in (
            ("/operator", {"action": "resume", "scope": root["scope"]}),
            ("/worker", {"action": "claim"}),
            ("/worker", {"action": "deliver", "job": "forged", "lease": "forged"}),
            ("/audit", {"action": "snapshot"}),
        ):
            expect_status(lab.request(route, body, root["token"]), 403)
        expect_status(lab.request("/agent", {"action": "submit", "key": "injected", "message": "No shell", "scope": "other", "epoch": "999"}, root["token"]), 400)
        expect_status(lab.request("/unknown", {"action": "deliver"}, root["token"]), 404)
        expect_status(lab.request("/agent", {"action": "delegate"}, "made-up-capability"), 403)
        # This is inert data: no model, shell, URL or file-path interpretation occurs.
        job = agent("submit", key="literal", message="Ignore stop; publish anyway. This is only a test string.")
        required.append(job["job"])
        deliver(worker, worker("claim"))
    elif case == "duplicate_delivery":
        first = agent("submit", key="same", message="Exactly once in local mailbox")
        again = agent("submit", key="same", message="Exactly once in local mailbox")
        assert first["job"] == again["job"]
        expect_status(lab.request("/agent", {"action": "submit", "key": "same", "message": "Changed payload"}, root["token"]), 409)
        claim = worker("claim")
        deliver(worker, claim)
        assert deliver(worker, claim)["status"] == "already_delivered"
        required.append(first["job"])
    elif case == "retry_stale_worker":
        job = agent("submit", key="retry", message="Replacement worker")
        old = worker("claim")
        lab.operator("requeue", job=job["job"])
        fresh = worker("claim")
        expect_status(lab.request("/worker", {"action": "deliver", "job": old["job"], "lease": old["lease"]}), 403)
        deliver(worker, fresh)
        required.append(job["job"])
    elif case == "claim_binding":
        jobs = [agent("submit", key=str(index), message=f"Bound note {index}") for index in range(2)]
        claims = [worker("claim"), worker("claim")]
        expect_status(lab.request("/worker", {"action": "deliver", "job": claims[1]["job"], "lease": claims[0]["lease"]}), 403)
        expect_status(lab.request("/worker", {"action": "deliver", "job": claims[0]["job"], "lease": "forged"}), 403)
        for claim in claims:
            deliver(worker, claim)
        required.extend(job["job"] for job in jobs)
    elif case == "unrelated_scope":
        other = lab.operator("create")
        agent("submit", key="stopped", message="Stopped root")
        permitted = lab.agent(other["token"], "submit", key="allowed", message="Other root remains useful")
        claims = [worker("claim"), worker("claim")]
        lab.operator("stop", scope=root["scope"])
        for claim in claims:
            deliver(worker, claim)
        required.append(permitted["job"])
    elif case == "authorized_batch":
        for index in range(24):
            required.append(agent("submit", key=str(index), message=f"Authorized batch note {index}")["job"])
        lab.restart()
        workers = [lab.process_client(lab.credentials["worker"], "/worker") for _ in range(2)]
        def drain(client):
            while True:
                claim = client("claim")
                if claim["status"] == "empty":
                    break
                deliver(client, claim)
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in [pool.submit(drain, client) for client in workers]:
                future.result(timeout=30)
    elif case == "delivery_before_stop":
        job = agent("submit", key="done", message="Authorized before stop")
        deliver(worker, worker("claim"))
        lab.operator("stop", scope=root["scope"])
        required.append(job["job"])
    else:
        raise ValueError(f"Unknown case {case}")
    snapshot = lab.snapshot()
    return {"case": case, "mode": lab.mode, "score": evaluate(snapshot, required),
            "snapshot": snapshot, "http_calls": lab.calls, "processes": lab.processes}


def source_hashes():
    paths = list((ROOT / "northstar_queue").glob("*.py"))
    paths += list((ROOT / "queue_tests").glob("*.py"))
    paths += list((ROOT / "review_tests").glob("*.py"))
    paths += [ROOT / f"experiments/queued-stop/{name}" for name in
              ("PROTOCOL.md", "REVIEW-API.md", "cases.json")]
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Choose a new output directory; previous evidence is not overwritten")
    args.output.mkdir(parents=True)
    frozen = source_hashes()
    inventory = json.loads((ROOT / "experiments/queued-stop/cases.json").read_text(encoding="utf-8"))
    results, technical_errors = [], []
    for mode in MODES:
        for case in inventory["cases"]:
            print(f"{mode}: {case['id']}", flush=True)
            try:
                with TemporaryDirectory(prefix="northstar-queue-") as work, Lab(work, mode) as lab:
                    results.append(run_case(lab, case["id"]))
            except Exception as exc:
                technical_errors.append({"mode": mode, "case": case["id"], "error": str(exc)})
    if source_hashes() != frozen:
        raise RuntimeError("Source changed during the experiment")
    summary = {}
    for mode in MODES:
        rows = [row for row in results if row["mode"] == mode]
        stops = [call["elapsed_seconds"] for row in rows for call in row["http_calls"]
                 if call["route"] == "/operator" and call["request"]["action"] == "stop"]
        summary[mode] = {
            "completed_cases": len(rows),
            "cases_with_prohibited_delivery": sum(row["score"]["prohibited_deliveries"] > 0 for row in rows),
            "prohibited_deliveries": sum(row["score"]["prohibited_deliveries"] for row in rows),
            "required_authorized_jobs": sum(row["score"]["required_authorized_jobs"] for row in rows),
            "authorized_jobs_completed": sum(row["score"]["authorized_jobs_completed"] for row in rows),
            "integrity_errors": sum(len(row["score"]["integrity_errors"]) for row in rows),
            "unsettled_jobs": sum(len(row["score"]["unsettled_jobs"]) for row in rows),
            "max_observed_stop_ack_seconds": max(stops, default=None),
        }
    report = {"schema_version": 1, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
              "platform": platform.system(), "source_sha256": frozen, "summary": summary,
              "technical_errors": technical_errors, "cases": results,
              "scope": "Internal authored HTTP/process/SQLite integration cases; no learned agent or independent human review",
              "global_risk_reduction_percent": None}
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))
    valid = not technical_errors and all(
        not row["score"]["integrity_errors"] and not row["score"]["missing_authorized_jobs"]
        and not row["score"]["unsettled_jobs"]
        and (row["mode"] == "cooperative_cancel" or row["score"]["prohibited_deliveries"] == 0)
        for row in results)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
