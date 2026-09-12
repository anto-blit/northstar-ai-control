# G16 — trap screen for a repeatable OpenAI failure (stage 1)

Six authorization traps, each with a legitimate twin, on a declared weaker
OpenAI target. **Baseline search only — no story guidance runs in this study.**

Read [PROTOCOL.md](PROTOCOL.md) first. It was registered and committed before any
call, and it fixes the target, the cases, the scoring, the 84-call budget, the
stop rule and the rule for advancing a family to confirmation.

## Status

Stage 1 registered. Results appear in
[results/openai-trap-screen/report.json](../../results/openai-trap-screen/report.json)
once the run completes, and this README is updated with the outcome — including
the outcome where nothing advances, as happened in G14 and G15.

## Why these six families

The project needs a failure it can reproduce before a story comparison can mean
anything. Two earlier OpenAI searches found none. This one changes both halves
of the design:

- **The cases are near-miss engineered.** In every family the tempting wrong
  reading lands just on the wrong side of the owner's limit, which is the
  property that makes Claude's case 068 fail 34% of the time.
- **The target is the lowest-deliberation configuration available.** All 36
  recorded Claude failures happened on calls where extended thinking did not
  fire; see [the thinking analysis](../../docs/thinking-and-failure.md). G14
  reasoned heavily on every call and could not have shown that mode.

Two families — `scope-creep` and `withdrawn-consent` — turn on authority scope
rather than arithmetic. Those are the ones where a later story result could say
something about the guidance rather than about answer ordering.

## Commands

```powershell
py experiments/openai-trap-screen/run.py register   # freeze the plan; no calls
py experiments/openai-trap-screen/run.py run        # makes model calls
py experiments/openai-trap-screen/run.py verify     # replay saved responses only
```

`verify` recomputes every score from the saved responses and fails if the
published report does not match. It makes no calls and cannot fill a missing one.

## Limits

A 12-call screen catches a true 20% failure rate about 93% of the time and a 10%
rate about 72%, so a clean family is weak evidence of robustness rather than
proof. Stage 1 cannot estimate a rate, confirm anything, or compare providers.
A family that advances earns only a separately recorded 50-call confirmation
batch; stage 1 evidence can never satisfy that confirmation itself.

This study tests no story, trains no model, executes no booking or release, and
changes nothing about the global-risk reference.
