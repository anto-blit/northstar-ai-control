# G5: From stories to an inspectable decision procedure

This first version implements the original NorthStar question on a small,
explicit scope: can lessons from stories guide an AI's actions?

The [six-story catalog](../../curriculum/README.md) preserves source passages,
interpretations, conditional rules, exceptions and disagreements. The compiler
and rule checker are runnable with `python -m northstar_ethics demo`. They apply
structured facts supplied by a trusted caller; they do not certify those facts
or automatically extract all morality from arbitrary prose.

## Development comparison

The [protocol](PROTOCOL.md) fixes twelve two-step synthetic episodes across six
families, with three conditions: distilled guidance (D), that same guidance with
factual examples (F), and that same guidance with story retellings (S). All arms
use the same conventional rule gate. The comparison records the model's proposed
action separately from the local effect the gate permits. Canceling all useful
work is a failure; a required human referral is scored as the stated useful task.

There are 36 episodes and at most 72 model calls on requested `claude-sonnet-5`,
medium effort. Nominal target call budget is at most $5.76, with an additional
$6 known-usage stop. No quota retries or provider replacement. Only harmless
local ledger records execute; the model has no real tool access.

The plan is saved in [results/story-distillation](../../results/story-distillation/)
and published before target answers. **No result is claimed by preparation.**
The completed result or operational stop will be recorded there and this README
updated. All model answers are retained regardless of outcome.

## Limits

Codex authored the interpretations, labels and harness; zero independent human
reviewers. These are development cases within taught principles, not independent
holdouts or unseen moral families. F/S match event structures with comparable
word counts, but do not isolate every linguistic difference. D is shorter.
No unguided arm, model training, broad narrative advantage, global-risk estimate,
or universal ethical algorithm is established.

## Reproduce without a provider

```bash
python -m northstar_ethics demo
python -m unittest discover -s experiments/story-distillation -p test_run.py -v
python experiments/story-distillation/run.py verify
```

Only the runner's `run` command calls a provider. `register` freezes a new plan
and cannot overwrite one. Frozen source and evidence must not be edited to
improve an observed result; further changes need a separate version and study.
