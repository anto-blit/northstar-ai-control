"""Build a portable dashboard from hash-checked, committed experiment evidence.

The thermometer uses 10% as a project reference, the lower end of Hinton's
subjective 10-20% extinction estimate discussed in the linked interview.
Experiment counts and outcomes never feed a humanity-wide probability estimate.
No external packages or network calls are needed to build or open the exported HTML.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def checked_file(root, relative, expected):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Evidence path must stay inside the repository")
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Evidence has changed since verification: {relative}")
    return path


def load_evidence(root=ROOT):
    record = root / "results/verification.json"
    verification = json.loads(record.read_text(encoding="utf-8"))
    if verification["failures"] or verification["errors"]:
        raise ValueError("Cannot publish passing evidence from a failed verification")
    if not verification["source_sha256"] or not verification["artifact_sha256"]:
        raise ValueError("Verification must include source and artifact provenance")
    for relative, digest in verification["source_sha256"].items():
        checked_file(root, relative, digest)
    artifacts = {}
    for name, digest in verification["artifact_sha256"].items():
        path = checked_file(root, "results/" + name, digest)
        artifacts[name] = json.loads(path.read_text(encoding="utf-8"))
    recovery = artifacts["recoverability.json"]
    monitor = artifacts["monitor-sweep.json"]
    if recovery["schema_version"] != 2 or monitor["schema_version"] != 2:
        raise ValueError("Dashboard requires reviewed analysis schema 2")
    return {
        "risk": {
            "assumedBaselinePercent": 10.0,
            "aspirationPercent": 0.0,
            "currentEstimatePercent": None,
            "quantifiedReductionPercent": None,
            "potentialGlobalReductionPercent": None,
            "claimedEvent": "AI destroys humanity",
            "claimSource": "https://www.wbur.org/onpoint/2025/12/29/godfather-of-ai-geoffrey-hinton",
            "claimAttribution": "Geoffrey Hinton",
            "claimRangePercent": [10.0, 20.0],
            "claimInterviewDate": "2025-01-10",
            "claimTimeHorizon": "Within 30 years, as discussed in the cited interview; not a rolling horizon",
            "demonstratedProtectionScope": "Fixed synthetic broker comparisons only",
            "basis": "The project selects the lower end of Hinton's subjective range as a reference assumption, not a current assessment or expert consensus. Global reduction is unestimated.",
        },
        "verification": {
            "tests": verification["tests_run"],
            "recordedAt": verification["started_at"],
            "python": verification["python"],
            "sourceCount": len(verification["source_sha256"]),
            "artifactCount": len(artifacts),
            "recordSha256": sha256(record.read_bytes()).hexdigest(),
            "artifactSha256": verification["artifact_sha256"],
        },
        "recovery": recovery,
        "monitor": monitor,
        "milestones": json.loads((HERE / "milestones.json").read_text(encoding="utf-8")),
    }


def render(root=ROOT):
    # Escape '<' so evidence text can never close its inert JSON script element.
    payload = json.dumps(load_evidence(root), ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")
    template = (HERE / "template.html").read_text(encoding="utf-8")
    replacements = {
        "@@STYLE@@": (HERE / "style.css").read_text(encoding="utf-8"),
        "@@DATA@@": payload,
        "@@APP@@": (HERE / "app.js").read_text(encoding="utf-8"),
    }
    for marker, value in replacements.items():
        if template.count(marker) != 1:
            raise ValueError(f"Template must contain exactly one {marker}")
        template = template.replace(marker, value)
    return template


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "index.html")
    parser.add_argument("--check", action="store_true", help="Fail if the exported dashboard is stale")
    args = parser.parse_args()
    content = render()
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != content.encode("utf-8"):
            raise SystemExit("Dashboard export is stale; run python dashboard/build_dashboard.py")
        print("Dashboard matches the hash-checked evidence and presentation sources.")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8", newline="\n")
        print(f"Built {args.output}")


if __name__ == "__main__":
    main()
