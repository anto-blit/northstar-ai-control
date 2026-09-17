"""Reuse reviewed tool-free adapters; only call() contacts a model."""
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import environment as env

claude = env.module('sg_claude', 'experiments/fallback-actions/transport.py')
codex = env.module('sg_codex', 'experiments/codex-repair/transport.py')
codex.MODEL, codex.EFFORT = 'gpt-5.5', 'medium'
TARGETS = {
    'claude': {'model': 'claude-sonnet-5', 'effort': 'medium', 'cli_version': '2.1.272 (Claude Code)', 'helper': claude.HELPER},
    'openai': {'model': 'gpt-5.5', 'effort': 'medium', 'cli_version': 'codex-cli 0.154.0', 'helper': None},
}


def version(target):
    executable = claude.executable() if target == 'claude' else shutil.which('codex')
    return subprocess.check_output([executable, '--version'], text=True, timeout=15).strip()


def operational(target, raw):
    if target == 'claude':
        return claude.operational(raw)
    usage = raw.get('usage') or {}
    return (raw.get('operational') is True and raw.get('returncode') == 0
            and raw.get('requested_model') == 'gpt-5.5' and raw.get('requested_effort') == 'medium'
            and raw.get('tool_or_unexpected_item') is False
            and isinstance(raw.get('thread_id_sha256'), str) and len(raw['thread_id_sha256']) == 64
            and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens')))


def usage(target, raw):
    if target == 'claude':
        cost = raw.get('total_cost_usd')
        return {'reported_usd': cost if type(cost) in (int, float) and math.isfinite(cost) and cost >= 0 else None,
                'input_tokens': None, 'output_tokens': None}
    u = raw.get('usage') or {}
    return {'reported_usd': None, **{k: u.get(k) if type(u.get(k)) is int and u[k] >= 0 else None for k in ('input_tokens', 'output_tokens')}}


def call(target, prompt, system, cap, timeout):
    if target == 'claude':
        return claude.call(prompt, system, cap, timeout)
    # The old adapter reads the exact supplied system text from this isolated file.
    with tempfile.TemporaryDirectory(prefix='northstar-side-gate-system-') as folder:
        codex.HERE = Path(folder)
        (codex.HERE / 'system.txt').write_text(system, encoding='utf-8', newline='\n')
        return codex.call(prompt, timeout=timeout)
