# APE1: the low-deliberation regime was reached, and the failure did not appear

September 15, 2026 local date. Registered design:
[PROTOCOL.md](../../experiments/authorization-pressure-loweffort/PROTOCOL.md)
and [plan.json](plan.json), both saved before calls. APO1 is closed and was not
rerun; this is a separate study on the same 58 frozen APS2 requests.

## Result

| Endpoint | APE1 (`gpt-6-astra`/low) |
|---|---:|
| Structured decisions correct | 58/58 |
| Joint decision pairs correct | 29/29 |
| Invalid / service-failed / missing | 0 / 0 / 0 |
| **Calls reporting zero reasoning tokens** | **58/58** |

Runtime 465.54 seconds, stopped by the planned call limit. Reported usage
277,614 input tokens (150,528 cached) and 6,168 output tokens, of which
**0 reasoning tokens**.

## Why the last row is the finding

This study existed to test one hypothesis: the
[thinking analysis](../../experiments/thinking-analysis/README.md) observed that
all 36 recorded Claude failures sit in the 43 non-thinking calls, while 257/257
thinking calls were correct. That is the only OpenAI failure hypothesis in this
repository with evidence behind it.

[G16](../../experiments/openai-trap-screen/README.md) aimed at that regime and
**missed it**: no zero-reasoning calls were observed on `gpt-5.3-codex-spark`/low,
so its clean sheet said little about the hypothesis. That model is no longer in
the account's catalog.

APE1 reached the regime on every single call. `gpt-6-astra` at low effort
reported zero reasoning tokens 58 times out of 58 — and still returned the
correct decision every time, including on `external_comms.L5.trap`, the exact
case that produces Claude's clearest repeated failure.

So the hypothesis is tested rather than dodged, and on this target it does not
hold: **removing visible deliberation did not reproduce the failure.** Whatever
drives the Claude fallback, "the model was not thinking" does not explain this
target's success on the same prompts.

## What this does not establish

Zero reasoning *tokens reported* is not proof of zero internal computation; it
is what the CLI reports, and platform-added context was not independently
captured or attested. The 58 requests are 29 related pairs, not 58 independent
tasks. A clean sheet at one effort setting on one model does not bound the
failure rate across the family, and 58 calls cannot rule out a low single-digit
percentage rate.

This qualifies no baseline, supports no provider ranking, and authorizes no
further calls, story arm or training work. It adds 58 calls to the running
OpenAI negative and is published as a negative, per standing direction.

## Comparison hygiene

The task strings, system text, schedule and scorer are identical to APO1's; the
only declared change is `model_reasoning_effort`, medium to low, and
`checked_plan()` refuses to run if the registered model or effort differs.

The **provider wrappers remain uncontrolled**, as APO1's review already records:
Claude was called through Claude Code's print process and these calls through
OpenAI's own Codex CLI. These are two vendor stacks, not two models on a level
field. Isolating the model from its vendor harness requires a raw-API path, for
which no key exists on this host.

Evidence: [plan](plan.json), [responses](responses), [report](report.json),
[completion](completion.json).
