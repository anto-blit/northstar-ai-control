"""Verify the queue pilot and reviewer tests independently of simulator results."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

from .experiment import source_hashes
from .harness import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory for this verification and experiment")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Choose a new output directory")
    frozen = source_hashes()
    provenance_path = ROOT / "experiments/queued-stop/claude-review/provenance.json"
    if not provenance_path.exists():
        raise SystemExit("Separate Claude review provenance is required for this combined verification")
    provenance_hash = sha256(provenance_path.read_bytes()).hexdigest()
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if not provenance.get("artifact_sha256"):
        raise SystemExit("Reviewer artifact provenance is required")
    for name, digest in provenance["artifact_sha256"].items():
        path = (ROOT / name).resolve()
        if (not path.is_relative_to(ROOT.resolve()) or not path.is_file()
                or sha256(path.read_bytes()).hexdigest() != digest):
            raise SystemExit(f"Reviewer artifact changed: {name}")
    args.output.mkdir(parents=True)
    tests = {}
    for directory, label in (("queue_tests", "internal"), ("review_tests", "claude_authored")):
        stream = io.StringIO()
        suite = unittest.TestLoader().discover(str(ROOT / directory))
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        log = stream.getvalue()
        print(log, flush=True)
        (args.output / f"{label}-tests.txt").write_text(log, encoding="utf-8", newline="\n")
        tests[label] = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)}
        if not result.testsRun or not result.wasSuccessful():
            raise SystemExit("Queue verification failed; test output retained")
    subprocess.run([sys.executable, "-m", "northstar_queue.experiment", "--output", str(args.output / "internal")],
                   cwd=ROOT, check=True)
    if source_hashes() != frozen or sha256(provenance_path.read_bytes()).hexdigest() != provenance_hash:
        raise RuntimeError("Source or reviewer provenance changed during verification")
    report = json.loads((args.output / "internal/report.json").read_text(encoding="utf-8"))
    # Summaries are exported for the dashboard; full traces stay in the report.
    record = {"schema_version": 1, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "platform": platform.system(),
              "tests": tests, "source_sha256": frozen, "summary": report["summary"],
              "artifact_sha256": {name: sha256((args.output / name).read_bytes()).hexdigest()
                                  for name in ("internal/report.json", "internal-tests.txt", "claude_authored-tests.txt")},
              "review_provenance": "experiments/queued-stop/claude-review/provenance.json",
              "review_provenance_sha256": provenance_hash,
              "review_type": "Separate AI review commissioned by implementer; regression replay by project harness",
              "independent_human_review": False, "global_risk_reduction_percent": None}
    (args.output / "verification.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                                                 encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
