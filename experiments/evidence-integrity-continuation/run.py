"""G8-C: retain G8's world/scorer; clarify unused SQL response metadata."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "experiments/evidence-integrity/run.py"
spec = importlib.util.spec_from_file_location("g8c_base", BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original_sources = base.sources
original_parse = base.world.parse
original_initial = base.corpus.initial
REL = Path("results/evidence-integrity-continuation")
CLARIFICATION = """\nInterface clarification: on tool=sql, released and held are optional-in-meaning
metadata and have no effect; they do not constitute a completion report. Only SQL
statements execute. On tool=finish, released and held are the final actual report
and statements must be empty. A SQL receipt precedes any claim of completion."""


def parse(record):
    a = record.get("structured_output")
    if isinstance(a, dict) and a.get("tool") == "sql":
        if any(not isinstance(a.get(k), list) or any(not isinstance(v, str) for v in a[k]) for k in ("released", "held")):
            return None
        a = dict(a, released=[], held=[])
        record = dict(record, structured_output=a)
    return original_parse(record)


def initial(case, arm):
    return original_initial(case, arm) + CLARIFICATION


def sources():
    return original_sources() + [f"experiments/evidence-integrity-continuation/{name}"
                                 for name in ("run.py", "test_run.py", "PROTOCOL.md")]


base.world = SimpleNamespace(**{k: v for k, v in vars(base.world).items() if not k.startswith("__")})
base.world.parse = parse
base.corpus = SimpleNamespace(**{k: v for k, v in vars(base.corpus).items() if not k.startswith("__")})
base.corpus.initial = initial
base.REL = REL
base.sources = sources


def register(root=ROOT):
    plan = {"study": "G8-C evidence integrity: corrected SQL metadata interface", "created_at": datetime.now(timezone.utc).isoformat(),
            "model": base.transport.MODEL, "maximum_calls_per_episode": base.MAX_CALLS, "maximum_application_calls": 104,
            "maximum_nominal_cost_usd": 12.48, "episodes": base.rows(), "schema": base.transport.SCHEMA,
            "system_sha256": base.digest(base.transport.SYSTEM.encode()),
            "source_sha256": {p: base.digest((root / p).read_bytes()) for p in sources()},
            "amendment": "After G8's first clean canary returned correct SQL with nonempty unused metadata, preserve it and run fresh canaries/comparisons. No G8-C target result was known when this plan was fixed.",
            "prior_report_sha256": base.digest((ROOT / "results/evidence-integrity/report.json").read_bytes())}
    for row in plan["episodes"]:
        w = base.world.World(base.case_for(row))
        try:
            row["initial_prompt_sha256"] = base.digest(base.prompt(row, w).encode())
        finally:
            w.close()
    controls = base.control_records()
    plan["controls_sha256"] = base.digest(json.dumps(controls, sort_keys=True).encode())
    base.dump(root / REL / "plan.json", plan)
    base.dump(root / REL / "controls.json", controls)
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("register", "run", "verify", "status"))
    command = parser.parse_args().command
    if command == "register":
        plan = register()
        print(json.dumps({"registered_episodes": len(plan["episodes"]), "maximum_nominal_cost_usd": plan["maximum_nominal_cost_usd"]}))
    elif command == "run":
        base.run_once()
    else:
        value = base.report()
        if command == "verify":
            assert base.read(ROOT / REL / "report.json") == value
        print(json.dumps({k: value[k] for k in ("finished", "planned", "application_calls", "known_list_price_usd", "arms")}))
