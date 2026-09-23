"""Tool-free, fresh-context Claude CLI calls with echoed-input verification (after MMS1)."""
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

CLI_VERSION = '2.1.280 (Claude Code)'
HELPER = 'claude-haiku-4-5-20251001'
# CLI 2.1.280 reports these built-in plugins even in safe/restricted mode; nothing else is accepted.
# Provider-side API retries are recorded but not fatal: the scored answer is still a single reply.
BUILTIN_PLUGINS = ('agents-md', 'telemetry')
TARGETS = {
    'haiku': {'model': 'claude-haiku-4-5-20251001', 'effort': None},
    'sonnet': {'model': 'claude-sonnet-5', 'effort': 'low'},
}
# Extended thinking off for every target: a short-deliberation agent decision.
OVERRIDES = {'CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING': '1', 'MAX_THINKING_TOKENS': '0',
             'CLAUDE_CODE_MAX_OUTPUT_TOKENS': '2048'}


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def executable():
    return shutil.which('claude') or str(Path.home() / '.local/bin/claude.exe')


def version():
    return subprocess.check_output([executable(), '--version'], text=True, timeout=15).strip()


def envelope(prompt):
    return json.dumps({'type': 'user', 'message': {'role': 'user', 'content': prompt},
                       'parent_tool_use_id': None, 'session_id': ''}, ensure_ascii=True) + '\n'


def text_content(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ''.join(x.get('text', '') for x in value if x.get('type') == 'text')
    return ''


def decode(stdout, prompt, returncode, model):
    events, errors = [], 0
    for line in stdout.splitlines():
        if line.strip():
            try:
                event = json.loads(line)
                if isinstance(event, dict):
                    events.append(event)
                else:
                    errors += 1
            except ValueError:
                errors += 1
    results = [e for e in events if e.get('type') == 'result']
    result = results[-1] if len(results) == 1 else {}
    raw = {k: result.get(k) for k in ('result', 'is_error', 'subtype', 'usage', 'modelUsage', 'total_cost_usd', 'num_turns')}
    initials = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
    assistants = [e.get('message', {}) for e in events if e.get('type') == 'assistant']
    users = [text_content(e.get('message', {}).get('content')) for e in events if e.get('type') == 'user']
    blocks = [b for m in assistants for b in m.get('content', [])]
    raw.update(returncode=returncode, parse_errors=errors, result_count=len(results),
               input_acknowledged=prompt in users, echoed_user_sha256=[digest(x) for x in users],
               init=[{k: e.get(k) for k in ('model', 'tools', 'mcp_servers', 'plugins', 'claude_code_version')} for e in initials],
               assistant_models=sorted({m.get('model', '') for m in assistants}),
               thinking_block_count=sum(b.get('type') in ('thinking', 'redacted_thinking') for b in blocks),
               tool_use_count=sum(b.get('type') == 'tool_use' for b in blocks),
               api_retries=[{k: e.get(k) for k in ('attempt', 'error_status', 'error')} for e in events if e.get('subtype') == 'api_retry'],
               stdout_sha256=digest(stdout), requested_model=model, thinking_settings=OVERRIDES)
    return raw


def operational(raw, model):
    cost = raw.get('total_cost_usd')
    usage = raw.get('modelUsage') or {}
    return (raw.get('returncode') == 0 and raw.get('is_error') is False and raw.get('num_turns') == 1
            and raw.get('result_count') == 1 and raw.get('parse_errors') == 0
            and raw.get('input_acknowledged') is True and isinstance(raw.get('result'), str)
            and raw.get('assistant_models') == [model] and raw.get('tool_use_count') == 0
            and len(raw.get('init', [])) == 1 and raw['init'][0]['model'] == model
            and not raw['init'][0].get('tools') and not raw['init'][0].get('mcp_servers')
            and all(x.get('path') == 'builtin' and x.get('name') in BUILTIN_PLUGINS for x in raw['init'][0].get('plugins') or [])
            and model in usage and set(usage) <= {model, HELPER}
            and type(cost) in (int, float) and math.isfinite(cost) and cost >= 0)


def call(target, system, prompt, cap, timeout):
    spec = TARGETS[target]
    args = [executable(), '--print', '--safe-mode', '--restricted', '--strict-mcp-config',
            '--no-chrome', '--no-session-persistence', '--disable-slash-commands', '--tools', '',
            '--model', spec['model'], '--settings', '{"alwaysThinkingEnabled":false}',
            '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose',
            '--replay-user-messages', '--system-prompt', system, '--max-budget-usd', str(cap)]
    if spec['effort']:
        args += ['--effort', spec['effort']]
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(('CODEX_', 'CLAUDE_')) and any(x in key for x in ('THREAD', 'SESSION', 'PARENT')):
            del env[key]
    env.update(OVERRIDES)
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix='northstar-nts-') as work:
            process = subprocess.run(args, input=envelope(prompt), text=True, encoding='utf-8', errors='replace',
                capture_output=True, cwd=work, env=env, timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        raw = decode(process.stdout, prompt, process.returncode, spec['model'])
        raw['stderr_sha256'] = digest(process.stderr)
        # Retain short CLI diagnostics only; no environment or account dumps.
        raw['stderr'] = process.stderr[:1000]
    except subprocess.TimeoutExpired:
        raw = {'result': '', 'error': 'timeout; usage unknown'}
    raw['elapsed_seconds'] = time.monotonic() - start
    return raw
