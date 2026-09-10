#!/usr/bin/env python3
"""Solve the finite recoverability game and write results/recoverability.json."""
import json
from pathlib import Path

from northstar_sim.analysis.recoverability import analyze


def main():
    data = analyze()
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    (out / "recoverability.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    windows = [
        {key: row[key] for key in ("environment", "control", "turn_order", "recoverable",
                                   "deadline", "requires_intervention")}
        for row in data["delegation"] + data["release"]
        if row.get("max_pending_jobs", row.get("max_staged_proposals")) == 1
    ]
    print(json.dumps({"intervention_windows_at_depth_1": windows}, indent=2))


if __name__ == "__main__":
    main()
