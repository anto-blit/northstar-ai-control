# G17 — story guidance with deliberation suppressed

Read [PROTOCOL.md](PROTOCOL.md) first. It was registered and committed before any
call.

## The point in one paragraph

Every failure this project has recorded on Claude happened on a call that did not
think; every call that did think was correct. Inside that non-thinking group, the
story arm was the only one that ever got it right — 7/7 against 0/16. That cannot
count as evidence, because we did not decide when the model thinks. G17 turns
deliberation into a setting we control instead of an outcome we observed, which is
the one change that makes the comparison fair.

## Status

**Stage A registered** — 40 calls, arm D only, on `claude-sonnet-5` at
`--effort low`. It asks a single question: does the failure recur at a usable
rate on this target while legitimate work survives? It must produce at least 4
valid wrong approvals in 32 over-limit attempts with all 8 controls correct, or
stage B is not registered and the baseline gate stays shut.

**Stage B not registered.** The four-arm comparison is sized from stage A's
observed rate, on cases stage A did not use.

## Commands

```powershell
py experiments/deliberation-comparison/run.py register A   # freeze the plan; no calls
py experiments/deliberation-comparison/run.py run A        # makes model calls
py experiments/deliberation-comparison/run.py verify A     # replay saved responses only
```

`verify` recomputes every score from saved responses and fails if the published
report does not match. `run` refuses to start if any inherited frozen source has
changed since registration.

## What is inherited rather than invented

Cases, arm texts and output contracts come unchanged from G12-B, whose 256 case
labels and calculations passed sixteen blind reviews. Only the target effort
differs. Every inherited hash is recorded in the plan.

This is deliberately **not** a resumption of G12-B. That study is closed and
incomplete at 72/1,024 calls; its evidence stays as it is. G17 is a new study at
a different target configuration.

## The comparator that matters

Arm R — justification-first with a consistency check — is the obvious fix for a
failure caused by not reasoning, and it already scores 72/72 in
[decision-repair](../decision-repair/README.md). If the story only matches R, the
honest conclusion is that stories are an expensive way to buy what a one-line
contract change already buys. The story has to beat R, or match it at lower cost,
to earn anything.

## Limits

One task family, one model, one harness, one frozen story/fact pair. A win would
support a bounded claim about this guidance, this model and this task under
suppressed deliberation — not about stories in general, not about agentic
settings with real effects, and not about global risk. The 10.00% reference is
unchanged regardless of outcome.
