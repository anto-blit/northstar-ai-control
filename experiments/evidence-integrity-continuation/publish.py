"""Re-execute both recorded studies, then seal their publication inputs."""
import argparse
from hashlib import sha256
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compute():
    original = load("g8_publication_original", ROOT / "experiments/evidence-integrity/run.py")
    current = load("g8_publication_continued", HERE / "run.py")
    for runner in (original, current.base):
        replayed = runner.report()
        if replayed != runner.read(ROOT / runner.REL / "report.json"):
            raise ValueError("Publication requires matching full replay")
    report = current.base.report()
    controls = current.base.control_records()
    weak = [r for r in controls if r["strategy"] != "legitimate" and not r["guarded"]]
    strong = [r for r in controls if r["strategy"] != "legitimate" and r["guarded"]]
    comparison = [r for r in report["episodes"] if r["phase"] == "comparison"]
    summary = {"planned": report["planned"], "finished": report["finished"],
               "applicationCalls": report["application_calls"], "cliTurns": report["cli_turns"],
               "knownCost": report["known_list_price_usd"], "modelUsageKeys": report["model_usage_keys"],
               "arms": report["arms"], "comparisons": report["comparisons"],
               "terminationCounts": {name: sum(r["termination"] == name for r in report["episodes"])
                                     for name in ("finished", "invalid", "provider_refusal", "service_failure", "exhausted", "unstarted")},
               "comparisonUseful": sum(r["score"]["useful_releases"] for r in comparison if r["score"]),
               "comparisonRequired": len(comparison) * 5,
               "evidenceEditEpisodes": sum(bool(r["score"]["changed_evidence_tables"]) for r in comparison if r["score"]),
               "unauthorizedReleaseEpisodes": sum(bool(r["score"]["unauthorized_releases"]) for r in comparison if r["score"]),
               "controls": {"attacks": len(weak),
                            "weakUnauthorized": sum(len(r["score"]["unauthorized_releases"]) for r in weak),
                            "guardedUnauthorized": sum(len(r["score"]["unauthorized_releases"]) for r in strong),
                            "guardedUseful": sum(r["score"]["useful_releases"] for r in strong),
                            "guardedRequired": sum(r["score"]["required_releases"] for r in strong)},
               "originalCanary": {"status": "invalid", "calls": 1, "knownCost": .021211},
               "publicCommit": current.base.read(ROOT / current.REL / "publication.json")["commit"]}
    paths = []
    for folder in ("results/evidence-integrity", "results/evidence-integrity-continuation"):
        paths.extend(p for p in (ROOT / folder).rglob("*.json") if p.name != "verification.json")
    return {"schema_version": 1, "verification": "Every saved original and continued action, receipt, database effect and score replays; all 24 scripted controls re-execute.",
            "source_sha256": {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in current.sources() + ["experiments/evidence-integrity-continuation/publish.py"]},
            "artifact_sha256": {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},
            "summary": summary}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("record", "verify"))
    command = parser.parse_args().command
    current = load("g8_publish_io", HERE / "run.py")
    value = compute()
    path = ROOT / current.REL / "verification.json"
    if command == "record":
        current.base.dump(path, value)
    elif current.base.read(path) != value:
        raise ValueError("Publication evidence changed")
    print({"sources": len(value["source_sha256"]), "artifacts": len(value["artifact_sha256"]), "summary": value["summary"]})
