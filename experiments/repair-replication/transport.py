"""Reuse the frozen tool-free transport with a per-call model selection."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/guidance-pilot/model_io.py"


def call(prompt, model_name, *, system=None, budget="0.10", timeout=120):
    spec = importlib.util.spec_from_file_location("g3_transport", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.MODEL = model_name
    options = dict(budget=budget, timeout=timeout)
    if system is not None:
        options["system"] = system
    record = module.call(prompt, **options)
    record.update(requested_model=model_name, prompt=prompt)
    return record


if __name__ == "__main__":
    import json
    folder = ROOT / "results/repair-replication"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "model-probe.json"
    if path.exists():
        raise RuntimeError("Probe already recorded")
    record = call("Reply with exactly OK.", "opus", budget="0.10", timeout=90)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: record.get(k) for k in ("result", "is_error", "modelUsage", "returncode", "total_cost_usd")}))
