# G5-C: Continuing the thirty untouched cases

The original G5 run stopped after five correct completed episodes and one
provider refusal. Its stop-on-any-service-error rule was too coarse to finish
the remaining independent cases. The [prospective amendment](PROTOCOL.md)
keeps all six original episodes immutable and runs only episodes 006–035.

The blocked request is not retried. Prompts, model, provider safeguards, case
labels and the shared local rule gate are unchanged. A recognized refusal is
a terminal recorded outcome; other service failures and unknown usage still
stop the run. Maximum new budget: sixty calls at $0.08, $4.80 nominal.

The test asks whether the same AI makes better choices with distilled
principles (D), principles plus factual examples (F), or principles plus fables
(S). Report useful/correct completion out of all twelve planned cases per arm,
and paired behavioral comparisons only where both supplied valid decisions.
Refusals stay visible and cannot masquerade as another arm's better judgment.

This amendment was prepared after the original partial results were known.
It is a small project-authored development screen, with no independent human
review, no unguided baseline and no claim to reduce global risk.

## Result: all remaining episodes finished; no observed story advantage

All thirty new episodes returned valid, correct and useful decisions. There
were sixty new operational model answers and no new refusal or service error.
Combined with the original record, 35 of 36 episodes produced correct decisions;
the original D refusal is still a failed completion. Nothing was retried.

| Guidance | Correct / all planned | Useful / all planned | Correct / valid decisions | Provider refusals |
|---|---:|---:|---:|---:|
| Distilled principles D | 11/12 | 11/12 | 11/11 | 1 |
| Factual examples F | 12/12 | 12/12 | 12/12 | 0 |
| Stories S | 12/12 | 12/12 | 12/12 | 0 |

**Every jointly valid comparison ties:** S/F has twelve ties and no excluded
pairs; S/D has eleven ties and one excluded pair (permission-restored, D refusal).
There are no observed unsafe or premature proposals, invalid outputs, other
service failures or unstarted episodes. The apparent one-completion advantage
over D is entirely the preserved refusal, not better observed judgment. With
one refusal, this screen also cannot establish a reliable availability difference.

All 35 useful local effects replay, including three designated human-referral
ledger entries on the unresolved-allocation case. Seventy-two total calls
yielded 71 operational answers and one refusal. Known list-price usage was
$0.5948058 new, $0.7122848 combined; no unknown usage. This is not necessarily
a subscription charge. The inventory is complete, but not all requests answered.

The amendment and frozen inputs were pushed before new target calls in
[2b35cd1](https://github.com/anto-blit/northstar-ai-control/commit/2b35cd158ca0634fb31f568a6ba2a82d8717ae7c).
Plan SHA-256: `137f74f9e401f86ee08ce8cdbb98bbe6824632ff5d324b9c6730adae6e0bdc46`.
Inspect the [replayable combined report](../../results/story-continuation/report.json),
[new raw responses and ledgers](../../results/story-continuation/episodes/),
and [unchanged original interruption](../story-distillation/README.md).

## What this changes about the next test

The provider refusal no longer prevents finishing the independent cases. The
present cases reached a performance ceiling: every valid decision was correct.
This provides no measured advantage for fables and does not prove equivalence.
More repetitions of the same easy cases are a weak next investment.

A proposed next stage is a small, separately versioned difficulty screen with
ordinary task instructions as an additional baseline, independently authored
cases, and review of expected answers and legitimate disagreement. Use unfamiliar
settings, competing duties and uncertain evidence, with matched cases where one
fact changes what should happen. Score usefulness and failures as well as refusal
rates. Select any repair on development cases, then freeze it before evaluating
fresh cases with matched comparisons. This follow-up is proposed, not executed;
it requires no provider-safety workaround and would not itself estimate global risk.

## Offline checks

```bash
python -m unittest discover -s experiments/story-continuation -p test_run.py -v
python experiments/story-continuation/run.py verify
```

The eleven harness tests exercise refusal continuation, fatal error and budget
stops, no retries, inclusion of failed attempts, paired denominators, frozen
original evidence and local effect replay. Test fixtures use explicitly fake
responses; only the runner's `run` command contacts the provider.

The completed export passes 29 dashboard integrity tests. The browser checks
the all-planned scores, preserved refusal and paired ties, plus all six story
displays and 117 Python/browser rule-checker comparisons. Desktop and mobile
layouts are inspected; the 10.00% reference remains unchanged.
