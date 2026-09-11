# G4: separate Codex repair comparison

Prepared with user authorization after the Claude continuation completed.
Use all 96 G3 direct-decision cases under all three original conditions: 288
fresh Codex sessions, requested `gpt-6-astra`, medium effort. No Claude answer
is replaced, and no model results are pooled. Codex targets receive no answer
keys, previous results or this conversation.

The [protocol](PROTOCOL.md) fixes the complete sample and scoring before target
evaluation. All three unscored transport-readiness records remain under
`results/codex-repair/preparation/`. The last probe passed. The first two exposed
startup notices while tools and host skill discovery were being disabled.

The CLI requests a model alias but does not independently report a resolved
server snapshot. Its context differs from Claude's. Interpret the within-Codex
comparison separately; this is project-run cross-provider evidence within one
synthetic family, not an independent external study.

Transport uses documented [ephemeral CLI execution](https://learn.chatgpt.com/docs/non-interactive-mode)
and [instruction/configuration overrides](https://learn.chatgpt.com/docs/config-file/config-reference).
The exact invocation options are frozen in the plan. No output schema forces
correct formatting, and every wrong or malformed response remains in the score.

```powershell
py -m unittest discover -s experiments/codex-repair -p test_run.py -v
py experiments/codex-repair/run.py freeze
# Publish the frozen sources and plan before registration and model calls.
py experiments/codex-repair/run.py register
py experiments/codex-repair/run.py run
py experiments/codex-repair/run.py verify
```

Target evaluation has not started. No improvement is claimed in advance.
