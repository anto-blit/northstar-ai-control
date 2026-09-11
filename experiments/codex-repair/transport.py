"""Fresh Codex CLI calls; no repository context, saved history, or enabled agent tools."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

MODEL = "gpt-6-astra"
EFFORT = "medium"
HERE = Path(__file__).resolve().parent
DISABLED = ("apps", "plugins", "hooks", "memories", "shell_tool", "unified_exec",
            "multi_agent", "multi_agent_v2", "browser_use", "browser_use_external",
            "computer_use", "image_generation", "view_image", "code_mode",
            "code_mode_host", "tool_suggest", "skill_search", "goals", "sleep_tool",
            "shell_snapshot", "workspace_dependencies", "remote_plugin",
            "skill_mcp_dependency_install", "unbounded_connection_retries")


def options(system_path):
    args = ["exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
            "--sandbox", "read-only", "--model", MODEL, "--strict-config", "--json"]
    config = {"model_reasoning_effort": EFFORT, "model_instructions_file": str(system_path),
              "project_doc_max_bytes": 0, "web_search": "disabled", "approval_policy": "never",
              "hide_agent_reasoning": True, "personality": "none", "mcp_servers": {},
              "features.skip_host_skill_discovery": True, "suppress_unstable_features_warning": True}
    config.update({"features." + name: False for name in DISABLED})
    for key, value in config.items():
        args += ["-c", key + "=" + ("{}" if value == {} else json.dumps(value))]
    return args + ["-"]


def parse_stream(stdout, returncode):
    events, errors, notices, messages, item_types, usage = [], [], [], [], [], None
    thread_hash, starts, completions, failed = None, 0, 0, False
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
                if "turn.started" not in events and message == ("Code Mode is unavailable because code-mode host is disabled. "
                        "Code mode will fail closed; enable `features.code_mode_host` and install `codex-code-mode-host`."):
                    notices.append(message)
                else:
                    errors.append(message)
        if kind == "item.started" and event.get("item", {}).get("type") not in ("agent_message", "reasoning"):
            failed = True
        if kind in ("error", "turn.failed"):
            failed = True
            errors.append(str(event.get("message") or event.get("error") or "provider failure")[:1200])
        if kind == "turn.completed":
            completions += 1
            usage = event.get("usage")
    unexpected = [kind for kind in item_types if kind not in ("agent_message", "reasoning", "error")]
    valid_usage = (isinstance(usage, dict) and isinstance(usage.get("input_tokens"), int)
                   and isinstance(usage.get("output_tokens"), int))
    operational = bool(returncode == 0 and starts == 1 and completions == 1 and len(messages) >= 1
                       and valid_usage and not errors and not failed and not unexpected)
    return dict(result="\n\n".join(messages), operational=operational, usage=usage,
                event_types=events, completed_item_types=item_types, thread_id_sha256=thread_hash,
                errors=errors, startup_notices=notices, tool_or_unexpected_item=bool(unexpected or failed))


def call(prompt, timeout=120):
    executable = shutil.which("codex")
    if not executable:
        raise RuntimeError("Codex CLI is unavailable")
    system_path = (HERE / "system.txt").resolve()
    started, before = datetime.now(timezone.utc).isoformat(), time.monotonic()
    # Separate OS-temp working root. No experiment files, labels, or past responses are placed here.
    with tempfile.TemporaryDirectory(prefix="northstar-codex-") as working:
        env = dict(os.environ)
        # Do not hand the new CLI thread a parent thread/session identifier.
        for key in list(env):
            if key.startswith("CODEX_") and any(word in key for word in ("THREAD", "SESSION", "PARENT")):
                del env[key]
        args = [executable] + options(system_path)
        try:
            proc = subprocess.run(args, input=prompt, text=True, encoding="utf-8", errors="replace",
                                  capture_output=True, cwd=working, env=env, timeout=timeout,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            parsed = parse_stream(proc.stdout, proc.returncode)
            parsed.update(returncode=proc.returncode, stdout_sha256=sha256(proc.stdout.encode()).hexdigest(),
                          stderr_sha256=sha256(proc.stderr.encode()).hexdigest())
        except subprocess.TimeoutExpired:
            parsed = dict(result="", operational=False, usage=None, returncode=None,
                          errors=["timeout; provider usage unknown"], event_types=[], completed_item_types=[],
                          thread_id_sha256=None, tool_or_unexpected_item=False)
    parsed.update(requested_model=MODEL, requested_effort=EFFORT, started_at=started,
                  elapsed_seconds=time.monotonic()-before, prompt=prompt,
                  prompt_sha256=sha256(prompt.encode()).hexdigest(), system_sha256=sha256(system_path.read_bytes()).hexdigest())
    return parsed


if __name__ == "__main__":
    folder = HERE.parents[1] / "results/codex-repair/preparation"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"readiness-{len(list(folder.glob('readiness-*.json'))):02}.json"
    response = call("Reply with exactly OK. Do not use tools or read files.")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(response, stream, indent=2)
        stream.write("\n")
    print(json.dumps(response, indent=2))
    sys.exit(0 if response["operational"] and response["result"].strip() == "OK" else 1)
