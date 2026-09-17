"""Fresh agentic Codex CLI calls in a staged working directory.

Unlike the decision-only transport in experiments/codex-repair, this one leaves
the shell and file-edit tools enabled and uses the workspace-write sandbox: the
probe needs the model to actually edit a file and run a test suite. Everything
else is kept isolated the same way -- no user config, no project docs, no
memory, no inherited thread identifiers, no network.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

MODEL = "gpt-6-astra"
EFFORT = "medium"
HERE = Path(__file__).resolve().parent
# code_mode / code_mode_host are deliberately NOT disabled here: on this CLI the
# shell and patch tools route through them, and disabling them leaves the agent
# with no way to edit a file at all.
DISABLED = ("apps", "plugins", "hooks", "memories", "multi_agent", "multi_agent_v2",
            "browser_use", "browser_use_external", "computer_use", "image_generation",
            "view_image", "tool_suggest", "skill_search", "goals", "sleep_tool",
            "workspace_dependencies", "remote_plugin", "skill_mcp_dependency_install",
            "unbounded_connection_retries")


def options(system_path, working):
    args = ["exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
            "--sandbox", "workspace-write", "--model", MODEL, "--strict-config", "--json"]
    config = {"model_reasoning_effort": EFFORT, "model_instructions_file": str(system_path),
              "project_doc_max_bytes": 0, "web_search": "disabled", "approval_policy": "never",
              "hide_agent_reasoning": True, "personality": "none", "mcp_servers": {},
              "features.skip_host_skill_discovery": True,
              "suppress_unstable_features_warning": True}
    config.update({"features." + name: False for name in DISABLED})
    for key, value in config.items():
        args += ["-c", key + "=" + ("{}" if value == {} else json.dumps(value))]
    # --ignore-user-config also discards the per-project trust entries, and an
    # untrusted workdir silently downgrades workspace-write to read-only. Trust
    # only the staged directory, and keep the Windows restricted-token sandbox on.
    key = str(working).replace("/", os.sep).lower()
    args += ["-c", "projects.'" + key + "'.trust_level=" + json.dumps("trusted")]
    if sys.platform == "win32":
        args += ["-c", "windows.sandbox=" + json.dumps("unelevated")]
    return args + ["-"]


def parse_stream(stdout, returncode):
    """Summarize the event stream. Tool items are expected here, not a defect."""
    events, errors, notices, messages, item_types = [], [], [], [], []
    usage, thread_hash, starts, completions, failed = None, None, 0, 0, False
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            errors.append("non-JSON stdout")
            continue
        kind = event.get("type", "unknown")
        events.append(kind)
        if kind == "thread.started":
            starts += 1
            thread_hash = sha256(str(event.get("thread_id", "")).encode()).hexdigest()
        if kind == "item.completed":
            item = event.get("item") or {}
            item_types.append(item.get("type", "unknown"))
            if item.get("type") == "agent_message":
                messages.append(item.get("text", ""))
            if item.get("type") == "error":
                message = str(item.get("message") or item)[:1200]
                if "turn.started" not in events and "Code Mode is unavailable" in message:
                    notices.append(message)
                else:
                    errors.append(message)
        if kind in ("error", "turn.failed"):
            failed = True
            errors.append(str(event.get("message") or event.get("error") or "provider failure")[:1200])
        if kind == "turn.completed":
            completions += 1
            usage = event.get("usage")
    valid_usage = (isinstance(usage, dict) and isinstance(usage.get("input_tokens"), int)
                   and isinstance(usage.get("output_tokens"), int))
    operational = bool(returncode == 0 and starts == 1 and completions == 1
                       and valid_usage and not errors and not failed)
    return dict(result="\n\n".join(messages), operational=operational, usage=usage,
                event_types=events, completed_item_types=item_types,
                thread_id_sha256=thread_hash, errors=errors, startup_notices=notices)


def call(prompt, working, timeout):
    """Run one ephemeral agentic turn with `working` as the sandbox root."""
    executable = shutil.which("codex")
    if not executable:
        raise RuntimeError("Codex CLI is unavailable")
    system_path = (HERE / "system.txt").resolve()
    started, before = datetime.now(timezone.utc).isoformat(), time.monotonic()
    env = dict(os.environ)
    # Do not hand the new CLI thread a parent thread/session identifier.
    for key in list(env):
        if key.startswith("CODEX_") and any(word in key for word in ("THREAD", "SESSION", "PARENT")):
            del env[key]
    args = [executable] + options(system_path, working)
    try:
        proc = subprocess.run(args, input=prompt, text=True, encoding="utf-8", errors="replace",
                              capture_output=True, cwd=str(working), env=env, timeout=timeout,
                              creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        parsed = parse_stream(proc.stdout, proc.returncode)
        parsed.update(returncode=proc.returncode,
                      stdout_sha256=sha256(proc.stdout.encode()).hexdigest(),
                      stderr_tail=proc.stderr.strip()[-600:])
    except subprocess.TimeoutExpired:
        parsed = dict(result="", operational=False, usage=None, returncode=None,
                      errors=[f"timeout after {timeout}s; provider usage unknown"],
                      event_types=[], completed_item_types=[], thread_id_sha256=None,
                      startup_notices=[])
    parsed.update(requested_model=MODEL, requested_effort=EFFORT, started_at=started,
                  elapsed_seconds=round(time.monotonic() - before, 2), prompt=prompt,
                  prompt_sha256=sha256(prompt.encode()).hexdigest(),
                  system_sha256=sha256(system_path.read_bytes()).hexdigest())
    return parsed
