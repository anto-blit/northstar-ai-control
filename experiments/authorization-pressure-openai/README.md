# APO1: isolated OpenAI authorization-pressure search

The user authorized a similar OpenAI run and requested blindness for fairness on
September 14, 2026. Read [PROTOCOL.md](PROTOCOL.md) before using the runner.

This uses the exact 58 APS2 user prompts, custom system text, pair mapping and
order, with requested GPT-6 Astra at medium effort in fresh isolated Codex CLI
sessions. The tested model receives no Claude responses, expected labels,
repository context or current discussion. No model tools are enabled.

The [regular process](../../protocol/authorization-pressure-process.md) now includes
pressure probes and review of all proposed actions, including fallbacks. The
study is a bounded exploratory comparison, not a provider ranking or story test.

Commands:

```
py -m unittest discover -s experiments/authorization-pressure-openai -p test_run.py
py experiments/authorization-pressure-openai/run.py register
py experiments/authorization-pressure-openai/run.py run
py experiments/authorization-pressure-openai/run.py verify
py experiments/authorization-pressure-openai/review_packet.py
```

Only `run` makes model calls, once after registration. The other commands work
offline. The packet export strips provider/model names and separates its identity
mapping; no independent reviewer is implied by generating it. Original APS2
responses and scores remain frozen. No old experiment is resumed.
