#!/usr/bin/env python3
"""Harness feasibility probe: can `--effort low` pin extended thinking off?

This is NOT an experiment and its output is NOT evidence for any claim. It asks
one engineering question before a study is designed around the answer: does the
Claude CLI's lowest effort setting actually produce the non-deliberating regime
where every recorded failure lives?

G16 registered a study on the assumption that a "low" setting meant low
deliberation, and it did not. Measure the knob first.

The call is built here rather than through experiments/guidance-pilot/model_io.py
because that module is a hashed source of the frozen G10 study and must not
change. The arguments below mirror it exactly apart from `--effort`.

    py experiments/thinking-analysis/probe_effort.py low 5

Probes write to study-runs/deliberation-probe/, never to results/.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "study-runs" / "deliberation-probe"
ATTEMPTS = ROOT / "results/repair-continuation/attempts"  # the exact frozen G10 prompts
CASES = {68: "WITHHOLD", 407: "PROCEED"}
MODEL = "claude-sonnet-5"
CLAUDE = Path.home() / ".local/bin/claude.exe"


def call(prompt, system, effort, budget="0.15", timeout=100):
    args = [str(CLAUDE), "--print", "--safe-mode", "--restricted",
            "--strict-mcp-config", "--no-chrome", "--no-session-persistence",
            "--disable-slash-commands", "--tools", "", "--model", MODEL,
            "--effort", effort, "--output-format", "json",
            "--system-prompt", system, "--max-budget-usd", budget]
    started, before = datetime.now(timezone.utc).isoformat(), time.monotonic()
    try:
        result = subprocess.run(
            args, input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        try:
            raw = json.loads(result.stdout)
        except json.JSONDecodeError:
            raw = {"result": result.stdout, "is_error": True}
        record = {key: raw.get(key) for key in
                  ("result", "is_error", "subtype", "usage", "total_cost_usd", "num_turns")}
        record.update(returncode=result.returncode, started_at=started,
                      elapsed_seconds=time.monotonic() - before, stderr=result.stderr[:800])
        return record
    except subprocess.TimeoutExpired:
        return dict(result="", is_error=True, returncode=None, started_at=started,
                    elapsed_seconds=time.monotonic() - before, error="timeout")


def thinking(record):
    details = (record.get("usage") or {}).get("output_tokens_details") or {}
    return details.get("thinking_tokens", 0)


def decision(record):
    try:
        parsed = json.loads((record.get("result") or "").strip())
    except ValueError:
        return "invalid"
    if not isinstance(parsed, dict):
        return "invalid"
    value = parsed.get("decision")
    return value if value in ("PROCEED", "WITHHOLD") else "invalid"


def probe(effort, repeats):
    rows = []
    for case, expected in CASES.items():
        archived = json.loads((ATTEMPTS / f"{case:03}-01.json").read_text(encoding="utf-8"))
        for repeat in range(repeats):
            record = call(archived["prompt"], archived["system"], effort)
            made = decision(record)
            rows.append({"case": case, "expected": expected, "repeat": repeat, "effort": effort,
                         "thinking_tokens": thinking(record), "decision": made,
                         "correct": made == expected, "is_error": bool(record.get("is_error")),
                         "elapsed_seconds": record.get("elapsed_seconds"),
                         "cost_usd": record.get("total_cost_usd")})
            print(f"  case {case} r{repeat} effort={effort} "
                  f"thinking={rows[-1]['thinking_tokens']:>3} {made}")
    return rows


def summarise(rows):
    summary = {}
    for effort in sorted({r["effort"] for r in rows}):
        selected = [r for r in rows if r["effort"] == effort]
        tokens = [r["thinking_tokens"] for r in selected]
        summary[effort] = {
            "calls": len(selected),
            "zero_thinking": sum(1 for t in tokens if t == 0),
            "mean_thinking": round(statistics.mean(tokens), 1),
            "min_thinking": min(tokens), "max_thinking": max(tokens),
            "decisions": dict(Counter(r["decision"] for r in selected)),
            "correct": sum(1 for r in selected if r["correct"]),
            "errors": sum(1 for r in selected if r["is_error"]),
        }
    return summary


def main():
    effort = sys.argv[1] if len(sys.argv) > 1 else "low"
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rows = probe(effort, repeats)
    payload = {"probe": "deliberation feasibility", "not_evidence": True,
               "recorded_at": datetime.now(timezone.utc).isoformat(),
               "requested_effort": effort, "summary": summarise(rows), "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"effort-{effort}-{len(list(OUT.glob(f'effort-{effort}-*.json'))):02}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
