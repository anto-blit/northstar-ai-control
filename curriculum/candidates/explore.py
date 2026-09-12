"""Candidate-only practice with the existing checker. No model or effect calls."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def engine(root=ROOT):
    spec = importlib.util.spec_from_file_location("candidate_existing_engine", root / "northstar_ethics/engine.py")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def load(root=ROOT):
    catalog = json.loads((root / "curriculum/candidates/catalog.json").read_text(encoding="utf-8"))
    if (catalog.get("schema_version") != 1 or catalog.get("status") != "candidate"
            or catalog.get("deployment_approved") is not False or type(catalog.get("model_calls")) is not int
            or catalog["model_calls"] != 0 or catalog.get("behavioral_result") is not None
            or type(catalog.get("human_reviewers")) is not int or catalog["human_reviewers"] != 0):
        raise ValueError("Candidate material cannot claim deployment approval, human review or a model result")
    for key in ("sources", "themes", "lessons", "practice_cases", "boundaries"):
        ids = [row["id"] for row in catalog[key]]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("Missing or duplicate candidate identities")
    source_ids = {s["id"] for s in catalog["sources"]}
    for row in catalog["lessons"] + catalog["themes"]:
        if not set(row["sources"]) <= source_ids:
            raise ValueError("Unknown source reference")
    for lesson in catalog["lessons"]:
        if lesson["action_type"] not in {"report", "assign"} or not lesson["action_scope"]:
            raise ValueError("A candidate needs an explicit supported task scope")
        rules = catalog["boundaries"] + lesson["rules"]
        if len({r["id"] for r in rules}) != len(rules) or len({r["fact"] for r in rules}) != len(rules):
            raise ValueError("Duplicate candidate rule or fact")
        for rule in rules:
            if (type(rule["expected"]) is not bool or rule["failure"] not in {"BLOCK", "REVIEW"}
                    or not rule["fact"].isidentifier() or not rule["reason"]):
                raise ValueError("Invalid candidate rule")
    return catalog


def assess(catalog, lesson_id, facts, root=ROOT):
    lesson = next(row for row in catalog["lessons"] if row["id"] == lesson_id)
    rules = [{**row, "actions": [lesson["action_type"]], "story_id": None,
              "basis": "Explicit practice contract, not inferred from a story"} for row in catalog["boundaries"]]
    rules += [{**row, "actions": [lesson["action_type"]], "story_id": lesson_id,
               "basis": "Untested project interpretation; not a universal moral rule"} for row in lesson["rules"]]
    return engine(root).assess({"rules": rules}, lesson["action_type"], facts)


def prepare(root=ROOT):
    catalog = load(root)
    results = []
    for case in catalog["practice_cases"]:
        value = assess(catalog, case["lesson"], case["facts"], root)
        if value["disposition"] != case["expected"]:
            raise ValueError(f"Practice case disagrees with its declared contract: {case['id']}")
        results.append({**case, "assessment": value})
    return {"catalog": catalog, "cases": results,
            "claim_limit": "Rule examples under supplied facts only. No model calls, executed actions or measured narrative benefit."}


if __name__ == "__main__":
    data = prepare()
    print(data["claim_limit"])
    for row in data["cases"]:
        print(f"{row['assessment']['disposition']:6} {row['id']}: {row['title']}")
