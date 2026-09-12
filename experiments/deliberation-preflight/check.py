"""Offline engineering checks of G17 B. Never calls a provider or changes G17.

Synthetic answers below test the harness, not a model. The few patched objects
isolate later defects behind the missing B dispatcher; all patches are temporary.
"""
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import argparse
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
G17 = ROOT / "experiments/deliberation-comparison"
sys.path.insert(0, str(G17))
spec = importlib.util.spec_from_file_location("g17_preflight_target", G17 / "run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def capture(operation):
    try:
        value = operation()
    except Exception as error:
        return {"exception": type(error).__name__, "message": str(error)}
    return {"returned": value}


def inspect():
    plan_path = ROOT / "results/deliberation-comparison/stage-B/plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = runner.materials.stage_b_requests(40, 40)
    fields = ("index", "case", "pair", "arm", "expected", "prompt_sha256")
    dispatch = capture(lambda: len(runner.materials.REQUESTS["B"]()))
    synthetic_repair = {"result": '{"reason":"The cost exceeds the cap.",'
                                  '"decision":"WITHHOLD"}', "returncode": 0}
    repair_scores = {name: getattr(runner.scoring, name)(synthetic_repair, "WITHHOLD")
                     for name in ("strict", "tolerant", "first_object")}
    # Isolate report behavior beyond the missing dispatcher. No source is edited.
    with patch.dict(runner.materials.REQUESTS, {"B": lambda: rows}):
        empty_report = capture(lambda: runner.report(plan, {}, "B"))
        synthetic = {}
        for row in rows:
            body = ({"reason": "Synthetic fixture.", "decision": row["expected"]}
                    if row["arm"] == "R" else
                    {"decision": row["expected"], "reason": "Synthetic fixture."})
            synthetic[row["index"]] = {
                "result": json.dumps(body), "returncode": 0,
                "usage": {"output_tokens_details": {"thinking_tokens": 0}},
                "total_cost_usd": 0,
            }
        complete_report = capture(lambda: runner.report(plan, synthetic, "B"))
        # Do not invoke real transport or writes. An error should stop this loop.
        error_record = {"result": "", "is_error": True, "returncode": 1,
                        "subtype": "error", "usage": None}
        with (patch.object(runner, "call", return_value=error_record) as fake_call,
              patch.object(runner, "write_json") as fake_write,
              patch.object(runner, "report", return_value={}),
              redirect_stdout(StringIO())):
            loop = capture(lambda: runner.command_run("B", 2))
        stop_probe = {"synthetic_transport_invocations": fake_call.call_count,
                      "writes_intercepted": fake_write.call_count, "outcome": loop}

    sources = [Path(__file__).resolve(), G17 / "run.py", G17 / "materials.py",
               G17 / "scoring.py", plan_path,
               ROOT / "experiments/decision-repair/run.py"]
    return {
        "kind": "offline engineering preflight; synthetic fixtures, no model experiment",
        "provider_calls": 0,
        "source_sha256": {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        "existing_stage_b_responses": len(runner.load_responses("B")),
        "registered_source_hashes_match": plan["sources_sha256"] == runner.plan("B")["sources_sha256"],
        "inherited_hashes_match": plan["inherited_sha256"] == runner.materials.inherited_hashes(),
        "registered_requests_match": plan["requests"] == [{k: r[k] for k in fields} for r in rows],
        "registered_calls": len(rows),
        "stage_b_dispatch": dispatch,
        "contract_compliant_repair_answer": repair_scores,
        "empty_report_with_dispatch_isolated": empty_report,
        "complete_report_with_dispatch_isolated": complete_report,
        "stop_after_first_service_error_with_dispatch_and_report_isolated": stop_probe,
        "ready": False,
        "interpretation": "Known blockers reproduced in the frozen G17 B harness. "
                          "This is not evidence about story effectiveness. "
                          "Fix in a new version before any live comparison.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    report = inspect()
    if args.verify:
        if json.loads(args.verify.read_text(encoding="utf-8")) != report:
            raise SystemExit("Preflight differs from saved report; inspect changes.")
        print("Saved offline preflight reproduced; G17 B is not ready. Zero provider calls.")
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))
