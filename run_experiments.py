#!/usr/bin/env python3
import json
from pathlib import Path
from northstar_sim.irreversible_release import run_demo as run_release
from northstar_sim.delegated_stop import run_demo as run_stop

def main():
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    data = {"irreversible_release": run_release(), "delegated_stop": run_stop()}
    (out / "experiment-results.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
      "irreversible_release": {k:data["irreversible_release"][k] for k in ["protected_unapproved","irreversible_failure","ledger_chain_valid"]},
      "delegated_stop": {k:data["delegated_stop"][k] for k in ["post_stop_dispatch","post_stop_failure","ledger_chain_valid"]}
    }, indent=2))


if __name__ == "__main__":
    main()
