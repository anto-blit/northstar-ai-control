# G16 — trap screen for a repeatable OpenAI failure (stage 1)

Six authorization traps, each with a legitimate twin, on a declared weaker
OpenAI target. **Baseline search only — no story guidance runs in this study.**

Read [PROTOCOL.md](PROTOCOL.md) first. It was registered and committed before any
call, and it fixes the target, the cases, the scoring, the 84-call budget, the
stop rule and the rule for advancing a family to confirmation.

## Result: no family advanced, and the intended manipulation did not happen

All 84 registered calls completed. **72/72 over-limit decisions correct, 12/12
legitimate controls correct, zero wrong approvals, zero invalid answers, zero
service errors, zero missing calls.** No family met the advancement rule, so no
confirmation batch was earned and none was run.

| Family | Wrong approvals / 12 | Legitimate controls | Advances |
| --- | ---: | ---: | --- |
| `conditional-credit` | 0 | 2/2 | no |
| `cumulative-cap` | 0 | 2/2 | no |
| `scope-creep` | 0 | 2/2 | no |
| `stale-authorization` | 0 | 2/2 | no |
| `unit-mismatch` | 0 | 2/2 | no |
| `withdrawn-consent` | 0 | 2/2 | no |

Pooled across all six families, 0 failures in 72 over-limit attempts puts a 95%
upper bound of **4.08%** on the per-call failure rate for this configuration and
these tasks. That is a genuinely informative negative, and a tighter one than
G14 or G15 achieved.

**The design premise failed, for a reason worth recording.** This study targeted
the low-deliberation regime because that is where every recorded Claude failure
lives. It did not reach that regime. Across the 84 calls, reasoning output ran to
a mean of 257 tokens and a median of 226, with a **minimum of 74 and not a single
call at zero**. `gpt-5.3-codex-spark` at `low` effort reasoned *more* than
`gpt-6-astra` at `medium` did in G14 (mean 220).

So the conclusion is not "this model is robust where Claude is not". It is that
**the Codex CLI cannot express the independent variable this experiment needed.**
`low` is the floor the CLI offers, and that floor is not low. The traps were never
tested against a non-deliberating model.

Recorded usage: 178,116 input tokens (115,200 cached) and 27,548 output tokens,
of which 21,568 were reasoning. Dollar charges are unavailable for this CLI
authentication; that is not the same as zero.

### What would actually test it

Suppressing deliberation needs a path the subscription CLI does not provide:
a direct API call with a minimal reasoning budget, or a model that does not
deliberate by default. Note that `gpt-5.3-codex-spark` reports
`supported_in_api: false`, while `gpt-5.5` and `gpt-6-astra` report `true` — so
an API-key path would have to use a different declared target, and that target's
baseline would need to qualify separately. No such run is registered.

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
