#!/usr/bin/env python3
"""Sweep monitor error rates and write results/monitor-sweep.json."""
import json
from pathlib import Path

from northstar_sim.analysis.monitor_sweep import analyze


def main():
    data = analyze()
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    (out / "monitor-sweep.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"observed_responses": data["observed_responses"]}, indent=2))


if __name__ == "__main__":
    main()
