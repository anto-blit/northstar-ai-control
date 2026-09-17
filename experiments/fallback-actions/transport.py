"""Tool-free Claude CLI adapter. Only call() spends model quota."""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


MODEL = "claude-sonnet-5"
HELPER = "claude-haiku-4-5-20251001"


def executable():
    found = shutil.which("claude")
    if found:
        return found
    fallback = Path.home() / ".local/bin/claude.exe"
    if fallback.is_file():
        return str(fallback)
    raise RuntimeError("Claude CLI not installed")


def version():
    return subprocess.check_output([executable(), "--version"], text=True, timeout=15).strip()


def operational(raw):
    cost = raw.get("total_cost_usd")
    usage = raw.get("modelUsage") or {}
    return (raw.get("returncode") == 0 and raw.get("is_error") is False
            and isinstance(raw.get("result"), str) and raw.get("num_turns") == 1
            and isinstance(usage, dict) and MODEL in usage and set(usage) <= {MODEL, HELPER}
            and type(cost) in (int, float) and math.isfinite(cost) and cost >= 0)


def call(prompt, system, budget, timeout):
    args = [executable(), "--print", "--safe-mode", "--restricted", "--strict-mcp-config",
            "--no-chrome", "--no-session-persistence", "--disable-slash-commands", "--tools", "",
            "--model", MODEL, "--effort", "medium", "--output-format", "json",
            "--system-prompt", system, "--max-budget-usd", str(budget)]
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(("CODEX_", "CLAUDE_")) and any(s in key for s in ("THREAD", "SESSION", "PARENT")):
            del env[key]
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="northstar-fax1-") as work:
            process = subprocess.run(args, input=prompt, text=True, encoding="utf-8", errors="replace",
                                     capture_output=True, cwd=work, env=env, timeout=timeout,
                                     creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        try:
            value = json.loads(process.stdout)
        except ValueError:
            value = {}
        if not isinstance(value, dict):
            value = {}
        raw = {k: value.get(k) for k in ("result", "is_error", "subtype", "usage", "modelUsage", "total_cost_usd", "num_turns")}
        raw.update(returncode=process.returncode,
                   stdout_sha256=hashlib.sha256(process.stdout.encode()).hexdigest(),
                   stderr_sha256=hashlib.sha256(process.stderr.encode()).hexdigest())
    except subprocess.TimeoutExpired:
        raw = {"result": "", "is_error": True, "returncode": None, "error": "timeout; usage unknown"}
    raw.update(requested_model=MODEL, requested_effort="medium", elapsed_seconds=time.monotonic()-start,
               completed_at=datetime.now(timezone.utc).isoformat())
    return raw
