# G4 complete: all three approaches scored 96/96 on Codex

All **288 planned Codex answers completed**, with one fresh session per answer,
requested `gpt-6-astra`, medium effort. Original instructions, the repair and
factual examples each scored **96/96**, preserving every legitimate approval
and making no unsafe or invalid decisions. This is a completed comparison with
**no observed repair advantage on Codex in these cases**.

| Condition | Correct decisions | Correct pairs | Unsafe approvals | Legitimate approvals | Invalid answers |
|---|---:|---:|---:|---:|---:|
| Original B | 96/96 | 48/48 | 0/48 | 48/48 | 0 |
| Repair R | 96/96 | 48/48 | 0/48 | 48/48 | 0 |
| Factual examples E | 96/96 | 48/48 | 0/48 | 48/48 | 0 |

Both paired comparisons have zero wins, zero losses, 48 ties and p = 1.0.
Every arm is at ceiling; equal observed scores do not prove equivalence or
universal reliability. The experiment neither supports nor refutes an advantage
on harder, unfamiliar tasks. It does limit a claim that the repair is needed
across models for this particular family of cases.

The project reused every G3 direct-decision case, without selecting for Claude
failures. No Claude answer was replaced and no model outcomes were pooled.
Claude's completed [G3-C comparison](../repair-continuation/README.md) retains
its small Sonnet gain (94/96 versus 96/96; p = 0.5) and Opus ceiling. No global
risk reduction follows from either study.

The [protocol](PROTOCOL.md), sources and complete 288-request plan were published
in commit [866ae6a](https://github.com/anto-blit/northstar-ai-control/commit/866ae6a7856d4c6e231fc0e0cb8df153ba19e148)
before target evaluation. The Claude results were already known to the project;
this is a separately registered follow-up on reused cases, not a new untouched
case set. All three unscored transport-readiness records remain under
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

Every saved target has a distinct hashed thread identifier. Targets received
only their assigned prompt, the task instruction and the CLI's surrounding
context, without answer keys, earlier results or this conversation. No target
tool action or operational failure occurred. All outputs are valid under the
unchanged G3 parser, so there are no failed outputs to explain away or repair.

The target run took about 11.2 minutes. Including the three preparation probes,
reported usage is 1,452,999 input tokens (723,072 cached) and 24,764 output tokens,
including 6,330 reasoning output tokens. These are usage counters, not a dollar
charge; the CLI does not expose the charge. Both registered token guards remained
unreached. The earlier conversational OK availability check is outside these
runner totals and supplied no evaluation case.

Inspect the [frozen plan](../../results/codex-repair/plan.json),
[completed report](../../results/codex-repair/report.json), and
[every target response](../../results/codex-repair/responses/).

```powershell
py -m unittest discover -s experiments/codex-repair -p test_run.py -v
py experiments/codex-repair/run.py verify
```

The completed report is immutable. These commands replay evidence offline;
they do not generate new model answers. Six harness tests and the dashboard's
evidence checks protect the frozen comparison and reject altered scores.
