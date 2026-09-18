"""Build the small contributor download from explicit, verified local files."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_FILES = ("audit.py", "bundle.json", "CONTRIBUTION.json", "manifest.json", "README.md", "RESULTS.md")
GUIDE_FILES = {"START-HERE.md": "START-HERE.md", "prompt.txt": "contributor-prompt.txt",
              "report-template.md": "report-template.md"}


def build_assets(root=ROOT):
    pins = json.loads((root / "dashboard/homepage-evidence.json").read_text(encoding="utf-8"))["sha256"]
    files = {}
    for name in PACKAGE_FILES:
        relative = "reproducers/mislabel-v1/" + name
        content = (root / relative).read_bytes()
        if sha256(content).hexdigest() != pins[relative]:
            raise ValueError("Contributor evidence changed: " + relative)
        files["mislabel-v1/" + name] = content
    for source, destination in GUIDE_FILES.items():
        files[destination] = (root / "contributor-kit" / source).read_bytes()
    files["LICENSE.txt"] = (root / "LICENSE").read_bytes()
    bundle = json.loads(files["mislabel-v1/bundle.json"])
    for case in ("s0", "w1", "positive", "negative"):
        for arm in ("standard", "repair"):
            folder = f"inputs/{case}/{arm}/"
            files[folder + "user.txt"] = bundle["cases"][case]["prompts"][arm].encode("utf-8")
            files[folder + "system.txt"] = bundle["target"]["system"].encode("utf-8")
            files[folder + "settings.json"] = (json.dumps(bundle["target"], indent=2) + "\n").encode("utf-8")
    files["SHA256SUMS.txt"] = "".join(f"{sha256(content).hexdigest()}  {name}\n"
                                    for name, content in sorted(files.items())).encode("utf-8")
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_STORED) as archive:
        for name, content in sorted(files.items()):
            # Fixed metadata and no compression make identical bytes on all CI platforms.
            info = ZipInfo("northstar-contributor-kit/" + name, date_time=(2026, 9, 17, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return {"northstar-contributor-kit.zip": buffer.getvalue(),
            "contributor-prompt.txt": files["contributor-prompt.txt"],
            "report-template.md": files["report-template.md"]}
