# A small reproducible reporting failure

This folder is a portable evidence package: copy it anywhere with Python 3.10+
and run the commands below. No dependencies, credentials or API calls are needed
to inspect it. It contains exact shortened prompts, returned answers, control
cases, model settings, scores, source provenance and a SHA-256 integrity manifest.
Local hashes establish consistency, not an independent timestamp or authenticity.

The measured failure is **labeling an explicit refusal as literal compliance**.
Appropriately refusing a harmful request is not the failure. The returned reasons
often openly apply an ethical interpretation of COMPLIANT, so this is evidence of
a reporting/rubric failure, not proof of covert deception or intent.

## Check the evidence

```
python audit.py verify
python audit.py export --case s0 --arm standard --out exported-s0
python audit.py export --case s0 --arm repair --out exported-s0-repair
python audit.py score --case s0 your-returned-answer.txt
```

Export writes exact user.txt, system.txt and settings.json to a new directory.
Only those inputs belong in a model call: do not send the answer key, previous
answers, selection history or current discussion. Scoring a pasted answer does
not establish recurrence, identity, cost completeness or independent replication.
The parser preserves refusals and unresolved answers; read the complete prose too.

## Reproduce the experiment

The exact tested target was Claude Sonnet 4.6, high effort, fixed 8192-token thinking
budget, 16384-token output allowance, Claude Code CLI 2.1.272, neutral system text,
fresh restricted tool-free contexts. bundle.json records the full target settings.
Another model, version, API interface or chat application is a separate target.
The original published API setup was not fully available; do not call this an
exact replication of the paper's API experiment.

Use the repository's experiments/mislabel-minimal/ runner as the worked collection
example, with a **new study ID, output directory and registration**; never resume
MMS1. Freeze target, exact prompts, two batches, control cases, arm order, all-call
accounting, failure definition, refusal handling, budget and stop rule first.
The full repository replay additionally checks echoed inputs and transport data.
No live-call runner is invoked automatically from this portable folder.

Both source cases and their two controls are included. s0 is the 3,303-character
standard prompt; w1 is the 12,950-character prompt. Each keeps the complete source
system plus one concrete operator request and refusal. This is a deletion-only
development test, not unseen-task transfer or the smallest possible prompt.
The negative reduction result is part of the package, not discarded.

## Contribute useful evidence

First reproduce or challenge the label and explain the exact sentence supporting
your judgment. Separate "the action was performed" from "refusal was justified."
Use CONTRIBUTION.json to record a replication, counterexample, proposed remedy
or independently authored challenge case. Leave genuinely unknown fields unknown.
Do not submit only successful examples; preserve errors, refusals, costs and missing
trials. Reviewers need the complete returned text and precise target settings.

A story is a candidate remedy. Compare it with a direct factual instruction and
matched non-narrative content, measure useful answers as well as false labels,
and test selected remedies on fresh cases. Votes or compelling prose do not
establish effectiveness. Independent review and replication are still needed.

This folder is prepared locally for sharing; no external publication, contributor
contact or community service is implied. Source-derived transcript material keeps
its original provenance; this package does not grant new rights to that material.
