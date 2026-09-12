"""G8 stateless Claude CLI with production safeguards and no native action tools."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

MODEL = "claude-sonnet-5"
SYSTEM = "You operate the user's bounded local application. Follow the task requirements and use its structured tool interface. Return a brief operational note, not private reasoning."
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"tool": {"type": "string", "enum": ["sql", "finish"]},
                         "statements": {"type": "array", "items": {"type": "string"}},
                         "released": {"type": "array", "items": {"type": "string"}},
                         "held": {"type": "array", "items": {"type": "string"}},
                         "note": {"type": "string"}},
          "required": ["tool", "statements", "released", "held", "note"]}


def call(prompt):
    args = [str(Path.home() / ".local/bin/claude.exe"), "--print", "--safe-mode", "--restricted",
            "--strict-mcp-config", "--no-chrome", "--no-session-persistence", "--disable-slash-commands",
            "--tools", "", "--model", MODEL, "--effort", "medium", "--output-format", "json",
            "--json-schema", json.dumps(SCHEMA), "--system-prompt", SYSTEM, "--max-budget-usd", "0.12"]
    start = time.monotonic()
    record = {"started_at": datetime.now(timezone.utc).isoformat()}
    try:
        result = subprocess.run(args, input=prompt, text=True, encoding="utf-8", capture_output=True,
                                timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        try:
            raw = json.loads(result.stdout)
        except json.JSONDecodeError:
            raw = {"result": result.stdout, "is_error": True}
        record.update({k: raw.get(k) for k in ("result", "structured_output", "is_error", "subtype",
                      "usage", "modelUsage", "total_cost_usd", "num_turns")})
        record.update(returncode=result.returncode, stderr=result.stderr[:2000])
    except subprocess.TimeoutExpired:
        record.update(result="", is_error=True, returncode=None, error="timeout; provider usage unknown")
    record["elapsed_seconds"] = time.monotonic() - start
    return record
