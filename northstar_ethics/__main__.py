"""Run with: python -m northstar_ethics compile | assess input.json | demo"""
import argparse
import json
from pathlib import Path

from .engine import ROOT, assess, compile_catalog, load_catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["compile", "assess", "demo"])
    parser.add_argument("input", nargs="?", type=Path)
    args = parser.parse_args()
    compiled = compile_catalog(load_catalog())
    if args.command == "compile":
        output = compiled
    elif args.command == "assess":
        if args.input is None:
            parser.error("assess requires a JSON file with action_type and facts")
        row = json.loads(args.input.read_text(encoding="utf-8"))
        output = assess(compiled, row["action_type"], row["facts"])
    else:
        cases = json.loads((ROOT / "curriculum/demos.json").read_text(encoding="utf-8"))
        output = [{"id": row["id"], "situation": row["situation"],
                   **assess(compiled, row["action_type"], row["facts"])} for row in cases]
    print(json.dumps(output, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
