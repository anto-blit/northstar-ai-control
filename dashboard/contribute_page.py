"""Build a no-account contribution flow from pinned, unchanged public inputs."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERSION = "chat-check-v1"


def packet(root=ROOT):
    relative = "reproducers/mislabel-v1/bundle.json"
    raw = (root / relative).read_bytes()
    pins = json.loads((root / "dashboard/homepage-evidence.json").read_text(encoding="utf-8"))["sha256"]
    if sha256(raw).hexdigest() != pins[relative]:
        raise ValueError("Contributor check evidence changed")
    bundle = json.loads(raw)
    cases = []
    for key in ("s0", "positive"):
        # Manual chat cannot set the app's real system prompt. Preserve the
        # source user message exactly; disclose this changed interface in reports.
        prompt = bundle["cases"][key]["prompts"]["standard"]
        cases.append({"id": key, "prompt": prompt,
                      "sha256": sha256(prompt.encode("utf-8")).hexdigest()})
    return {"version": VERSION, "sourceSha256": pins[relative],
            "protocol": "https://dontkillthehumans.org/contributor-check-plan.txt",
            "maxMessages": 2, "cases": cases}


def build_assets(root=ROOT):
    data = packet(root)
    template = (HERE / "contribute.template.html").read_text(encoding="utf-8")
    plan = (root / "protocol/contributor-chat-check-v1.md").read_text(encoding="utf-8")
    replacements = {"@@STYLE@@": (HERE / "contribute.css").read_text(encoding="utf-8"),
                    "@@APP@@": (HERE / "contribute.js").read_text(encoding="utf-8"),
                    "@@DATA@@": json.dumps(data, ensure_ascii=True).replace("<", "\\u003c"),
                    "@@PLAN@@": escape(plan)}
    for marker, value in replacements.items():
        if template.count(marker) != 1:
            raise ValueError("Contribution template marker: " + marker)
        template = template.replace(marker, value)
    return {"contribute.html": template.encode("utf-8"),
            "contributor-check-plan.txt": plan.encode("utf-8"),
            "contributor-check-inputs.json": (json.dumps(data, ensure_ascii=True, indent=2) + "\n").encode("utf-8")}
