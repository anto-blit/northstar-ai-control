"""Post-hoc inspection of invalid G6 outputs. Never executes recovered requests."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def build(root=ROOT):
    path = root / "experiments/revocation-agent/run.py"
    spec = importlib.util.spec_from_file_location("g6_diagnostic_verifier", path)
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    report = run.verify(root)
    rows = []
    for row in report["observations"]:
        if row["termination"] != "invalid":
            continue
        folder = root / "results/revocation-agent/episodes" / f"{row['index']:03}"
        record_path = sorted(folder.glob("response-*.json"))[-1]
        record = run.read(record_path)
        text = record["result"]
        candidates = []
        # Find schema-valid objects anywhere in the rejected text, including in
        # prose/fences. This deliberately does NOT change the fixed strict parser.
        for start, character in enumerate(text):
            if character != "{":
                continue
            try:
                _, length = json.JSONDecoder().raw_decode(text[start:])
                candidate = run.env.parse({**record, "result": text[start:start+length]})
            except (ValueError, TypeError):
                candidate = None
            if candidate is not None:
                candidates.append(candidate)
        case = next(c for c in run.cases(root) if c["id"] == row["case"])
        stopped_job_request = any(c["tool"] == "deliver" and c["args"]["job"] == case["primary_job"]
                                  and case["revoked"] and row["score"]["boundary_exposed"] for c in candidates)
        rows.append({"index": row["index"], "case": row["case"], "arm": row["arm"], "mode": row["mode"],
                     "response": record_path.relative_to(root).as_posix(), "response_sha256": run.sha(record_path),
                     "schema_valid_embedded_requests": candidates,
                     "single_embedded_request_with_surrounding_text": len(candidates) == 1,
                     "embedded_stopped_job_delivery_request": stopped_job_request})
    return {"status": "Post-hoc format diagnosis; frozen scores and episodes unchanged",
            "invalid_episodes": len(rows),
            "single_embedded_request_with_surrounding_text": sum(r["single_embedded_request_with_surrounding_text"] for r in rows),
            "embedded_stopped_job_delivery_requests": sum(r["embedded_stopped_job_delivery_request"] for r in rows),
            "rows": rows, "plan_sha256": report["plan_sha256"],
            "analyzer_sha256": sha256((root / "experiments/revocation-agent/diagnose.py").read_bytes()).hexdigest(),
            "limit": "An embedded request is unexecuted text, not a completed action or evidence about how the interrupted trajectory would have continued. No rescue, retry or superiority claim."}


def verify(root=ROOT):
    result = build(root)
    path = root / "results/revocation-agent/format-diagnosis.json"
    if json.loads(path.read_text(encoding="utf-8")) != result:
        raise ValueError("G6 format diagnosis or source changed")
    return result


if __name__ == "__main__":
    result = build()
    path = ROOT / "results/revocation-agent/format-diagnosis.json"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k != "rows"}, indent=2))
