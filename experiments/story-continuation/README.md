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

## Status

Registered for publication before new target calls. The original record remains
in [G5](../story-distillation/README.md). Actual new results will be recorded here.

## Offline checks

```bash
python -m unittest discover -s experiments/story-continuation -p test_run.py -v
python experiments/story-continuation/run.py verify
```

The eleven harness tests exercise refusal continuation, fatal error and budget
stops, no retries, inclusion of failed attempts, paired denominators, frozen
original evidence and local effect replay. Test fixtures use explicitly fake
responses; only the runner's `run` command contacts the provider.
