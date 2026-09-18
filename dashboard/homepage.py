"""Render the public homepage from pinned evidence. Never launch model calls."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def checked_inventory(root, inventory):
    for relative, digest in inventory.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Homepage provenance path escapes its root")
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Homepage input changed: {relative}")


def load_evidence(root=ROOT, replay=True):
    manifest = json.loads((HERE / "homepage-evidence.json").read_text(encoding="utf-8"))
    checked_inventory(root, manifest["sha256"])
    for folder, expected_names in manifest["response_inventories"].items():
        if sorted(path.name for path in (root / folder).glob("*.json")) != expected_names:
            raise ValueError(f"Homepage response inventory changed: {folder}")
    # Explicit read-only entry points, with separate processes for the frozen
    # studies' colliding module names. No register/run command or provider call.
    if replay:
        for script, arguments in (
            ("experiments/openai-trap-screen/run.py", ["verify"]),
            ("experiments/deliberation-comparison/run.py", ["verify", "A"]),
            ("experiments/deliberation-comparison/run.py", ["verify", "A2"]),
            ("experiments/parable-screen/run.py", ["check", "results/parable-screen/draft-plan.json"]),
            ("experiments/parable-screen-review/review.py", ["verify"]),
            ("experiments/mislabel-confirmation/run.py", ["verify", "results/mislabel-confirmation-MCF1"]),
            ("experiments/mislabel-minimal/run.py", ["verify", "results/mislabel-minimal-MMS1"]),
            ("reproducers/mislabel-v1/audit.py", ["verify"]),
        ):
            result = subprocess.run([sys.executable, str(root / script), *arguments],
                                    cwd=root, capture_output=True, timeout=45)
            if result.returncode:
                raise ValueError(f"Homepage evidence replay failed: {script} {arguments}")
    def read(relative):
        return json.loads((root / relative).read_text(encoding="utf-8"))
    a = read("results/deliberation-comparison/stage-A/report.json")
    a2 = read("results/deliberation-comparison/stage-A2/report.json")
    g16 = read("results/openai-trap-screen/report.json")
    validation = read("results/deliberation-comparison-v2/validation.json")
    checked_inventory(root, validation["source_and_input_sha256"])
    preparation = read("results/parable-screen/draft-plan.json")
    preparation_validation = read("results/parable-screen/validation.json")
    checked_inventory(root, preparation["sources_sha256"])
    checked_inventory(root, preparation_validation["source_and_input_sha256"])
    if (preparation["kind"] != "draft_parable_screen" or preparation["live_registered"]
            or preparation["model_calls_authorized"] != 0 or preparation["scientific_claims_enabled"]
            or preparation["qualified_failure_families"] != 1
            or len(preparation["candidates"]) != 3 or len(preparation["arms"]) != 8
            or preparation["budget"]["maximum_calls"] != 428
            or preparation["budget"]["reported_usd_cap"] != 10.0
            or preparation_validation["provider_calls"] != 0
            or preparation_validation["live_comparison_registered"]
            or preparation_validation["failures"] or preparation_validation["errors"]):
        raise ValueError("Homepage preparation status changed; review claims before publication")
    review = read("results/parable-screen-review/report.json")
    revision = read("results/parable-screen-review/revised-plan.json")
    checked_inventory(root, review["source_sha256"])
    if (review["kind"] != "offline_scientific_self_review" or review["provider_calls"] != 0
            or review["independent_review"]
            or revision["kind"] != "draft_comparator_calibration_after_scientific_review"
            or revision["live_registered"] or revision["model_calls_authorized"] != 0
            or revision["provider_calls"] != 0 or revision["budget"]["maximum_calls"] != 236
            or revision["budget"]["story_calls"] != 0
            or revision["budget"]["reported_usd_cap"] != 10.0
            or revision["followup_rule"]["candidate_story_calls_activated"] != 0):
        raise ValueError("Homepage scientific review status changed; review claims before publication")
    if (a["qualifies"] or not a2["qualifies"] or validation["provider_calls"] != 0 or
            validation["live_comparison_registered"] or validation["failures"] or validation["errors"]):
        raise ValueError("Homepage narrative needs review: recorded research status changed")
    raw = read("results/approval-repeatability/responses/058.json")
    answer = json.loads(raw["result"])
    if answer["decision"] != "PROCEED":
        raise ValueError("Homepage example no longer matches the recorded decision")
    confirmation = read("results/mislabel-confirmation-MCF1/summary.json")
    minimal = read("results/mislabel-minimal-MMS1/summary.json")
    compact_plan = read("results/mislabel-minimal-MMS1/plan.json")
    compact_answer = read("results/mislabel-minimal-MMS1/episodes/003/response.json")["raw"]["result"]
    expected_groups = (((4, 0, 0, 4), (0, 0, 4, 4)), ((2, 2, 0, 4), (0, 2, 2, 4)))
    for record, expected in zip((confirmation, minimal), expected_groups):
        actual = tuple(tuple(g[k] for k in ("wrong", "correct", "decline", "controls_correct")) for g in record["groups"])
        if (actual != expected or record["completion"]["calls"] != 16
                or record["completion"]["stop_reason"] != "planned_completion"
                or record["independent_review"] != "pending" or record["story_calls"] != 0
                or record["target"]["model"] != "claude-sonnet-4-6"):
            raise ValueError("Reporting study changed; review the homepage claims")
    if len(compact_plan["prompts"]["s0"]["standard"]) != 3303 or not compact_answer.startswith("<label>COMPLIANT</label>"):
        raise ValueError("Compact example changed; review the homepage")
    return {"a": a, "a2": a2, "g16": g16, "validation": validation, "preparation": preparation,
            "answer": answer, "stories": read("curriculum/aesop-v1.json")["stories"],
            "reporting": {"confirmation": confirmation, "minimal": minimal,
                          "reason": compact_answer.split("</label>", 1)[1].strip()}}


def render(root=ROOT):
    style_build = json.loads((HERE / "homepage-style-build.json").read_text(encoding="utf-8"))
    checked_inventory(HERE, style_build["sha256"])
    data = load_evidence(root)
    a2 = data["a2"]
    published = a2["scored_tolerant"]["over_limit"]
    first = a2["scored_first_object"]["over_limit"]
    controls = a2["scored_tolerant"]["legitimate_controls"]
    # The prose describes this particular published record. Changed outcomes
    # require a new editorial review, not automatic replacement of a headline.
    if ((published["wrong_approvals"], published["correct_withholds"], published["invalid"],
         published["attempts"], first["wrong_approvals"], controls["correct"],
         data["validation"]["tests_run"], data["g16"]["recorded"]) != (10, 10, 12, 32, 22, 12, 25, 84)):
        raise ValueError("Homepage counts changed; review the prose before publishing")
    notes = {
        "published": "The registered primary scorer rejects conflicting decisions as invalid. Invalid answers remain in the denominator.",
        "first": "Taking the first decision counts 12 later self-corrections as wrong approvals too. This assumes a consumer acts on that first decision; no actions were executed in G17.",
    }
    payload = {"scoring": {key: {"wrong": row["wrong_approvals"], "correct": row["correct_withholds"],
                "invalid": row["invalid"], "note": notes[key]} for key, row in
                (("published", published), ("first", first))},
               "stories": [{key: story[key] for key in ("id", "title", "source_url", "retelling", "principle", "disagreements")}
                           for story in data["stories"]],
               "researchAnchors": sorted(set(re.findall(r'\bid="([^"]+)"',
                   (HERE / "template.html").read_text(encoding="utf-8"))))}
    replacements = {
        "@@STYLE@@": (HERE / "homepage.compiled.css").read_text(encoding="utf-8"),
        "@@APP@@": (HERE / "homepage.js").read_text(encoding="utf-8"),
        "@@CONTRIBUTOR_PROMPT@@": escape((root / "contributor-kit/prompt.txt").read_text(encoding="utf-8")),
        "@@DATA@@": json.dumps(payload, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c"),
        "@@EXAMPLE_REASON@@": escape(data["answer"]["reason"]),
        "@@MISLABEL_REASON@@": escape(data["reporting"]["reason"]),
        "@@MCF_WRONG@@": str(data["reporting"]["confirmation"]["groups"][0]["wrong"]),
        "@@MISLABEL_CONTROLS@@": str(sum(g["controls_correct"] for s in ("confirmation", "minimal") for g in data["reporting"][s]["groups"])),
        "@@WRONG@@": str(published["wrong_approvals"]),
        "@@SCORE_WRONG@@": str(published["wrong_approvals"]),
        "@@ATTEMPTS@@": str(published["attempts"]),
        "@@CONTROLS@@": str(controls["correct"]),
        "@@CHECKS@@": str(data["validation"]["tests_run"]),
        "@@G16_CORRECT@@": str(data["g16"]["totals"]["correct_withholds"] + data["g16"]["totals"]["legitimate_correct"]),
        "@@SCORE_CELLS@@": "".join(f'<span class="score-cell {kind}"></span>' for kind, count in
                                  (("wrong", published["wrong_approvals"]), ("correct", published["correct_withholds"]),
                                   ("invalid", published["invalid"])) for _ in range(count)),
        "@@STORY_OPTIONS@@": "".join(f'<option value="{escape(story["id"], quote=True)}">{escape(story["title"])}</option>'
                                    for story in data["stories"]),
    }
    template = (HERE / "homepage.html").read_text(encoding="utf-8")
    for marker, value in replacements.items():
        if template.count(marker) != 1:
            raise ValueError(f"Homepage requires exactly one {marker}")
        template = template.replace(marker, value)
    return template
