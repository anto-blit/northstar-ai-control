#!/usr/bin/env python3
"""Run the conformance suite and regenerate results with source provenance."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import platform
import sys
import unittest

import compare_baselines
import monitor_analysis
import property_checks
import recoverability_analysis
import run_experiments

ROOT = Path(__file__).resolve().parent


def sources():
    paths = list(ROOT.glob("*.py"))
    paths += list((ROOT / "northstar_sim").glob("*.py"))
    paths += list((ROOT / "northstar_sim/analysis").glob("*.py"))
    paths += list((ROOT / "tests").glob("*.py"))
    paths += list((ROOT / "protocol/study-arms").glob("*.md"))
    paths += list((ROOT / "experiments/discovery-study/example").glob("*.json"))
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def main():
    started = datetime.now(timezone.utc).isoformat()
    frozen_sources = sources()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    run_experiments.main()
    property_checks.main()
    compare_baselines.main()
    recoverability_analysis.main()
    monitor_analysis.main()
    if sources() != frozen_sources:
        raise RuntimeError("source files changed during verification")
    artifacts = ("experiment-results.json", "property-check-results.json",
                 "baseline-comparison.json", "recoverability.json", "monitor-sweep.json")
    report = {"started_at": started, "python": platform.python_version(), "tests_run": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors),
              "source_sha256": frozen_sources,
              "artifact_sha256": {name: sha256((ROOT / "results" / name).read_bytes()).hexdigest() for name in artifacts},
              "scope": "Synthetic mechanism/conformance verification; not a discovery-method comparison."}
    (ROOT / "results/verification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"Verified {result.testsRun} tests and regenerated {len(artifacts)} result artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
