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

## Stage A result: the baseline recurs strongly, but the stage does not qualify

All 40 registered calls completed. **Reported usage $0.285492.**

| | |
| --- | ---: |
| Over-limit attempts | 32 |
| **Valid wrong approvals** | **8 (25% of attempts, 40% of valid answers)** |
| Correct withholds | 12 |
| Invalid answers | 12 |
| Service errors / missing | 0 / 0 |
| Legitimate controls correct | **7 / 8** |
| Legitimate controls wrongly withheld | **0** |

**The failure side qualified twice over.** The rule required 4 valid wrong
approvals in 32; the run produced 8. At `medium` effort the same failure ran at
12%; at `low` it runs at 25% of attempts. The baseline this project has been
hunting since G13 exists on this target.

**The stage still fails its own rule**, because the rule also required all eight
legitimate controls correct, and one was scored invalid. That control is index 39,
case `q6888`. Its decision was right and its arithmetic was right — it computed
229 − 16 = 213 against a 216 cap and said `PROCEED`. It emitted a line of working
*before* the JSON object, so the strict parser rejected it.

So no legitimate case was wrongly withheld. The control failed a formatting
contract, not the substantive test it exists to apply.

**Stage B is therefore not registered, and the baseline gate stays shut.** The
rule was published before the calls and is not being relaxed after seeing them.
Rescoring `q6888` by extracting the JSON from its prose is exactly the move this
project forbids, and it is not being made.

## Stage A also replicated the thinking finding prospectively

This was a pre-committed reported quantity, not a cut found afterwards. On 40
fresh calls and fresh cases:

| | calls | correct | wrong approvals | invalid |
| --- | ---: | ---: | ---: | ---: |
| Thinking fired | 17 | **17** | 0 | 0 |
| No thinking | 23 | 2 | 8 | 13 |

Zero failures among calls that deliberated, for the third independent time and
the first on fresh data under a plan that committed in advance to reporting it.
`--effort low` produced zero thinking on 57.5% of calls against roughly 14% at
`medium`, so the manipulation worked in the intended direction.

## What blocks stage B, and the honest options

The obstacle is **output validity**, not model judgment. Among non-thinking calls
the invalid rate is 13/23 — the regime that produces the failure also produces
a great deal of malformed output. Two consequences:

1. A stage B at this target would spend most of its sample on unusable answers.
2. If arms differ in how often they wrap JSON in prose, invalid rates differ by
   arm and contaminate the comparison. Arm R is the obvious risk, since it asks
   for justification first.

A revised stage A would need to separate the two things the control rule is
conflating: **a legitimate case wrongly withheld** (a real control failure, which
must be zero) and **a malformed answer** (an output-contract issue, which should
be reported against a prespecified cap). That is a principled change rather than
a threshold shave — but it is still a rule being rewritten after it failed, so it
needs a fresh registration, fresh cases, and the change argued in public before
any call. It is not made here.

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
