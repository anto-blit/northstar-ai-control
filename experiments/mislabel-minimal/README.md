# MMS1: smaller source-derived failure cases

One fixed deletion-only attempt following MCF1's completed confirmation.
Each case keeps its full original source system prompt, the final concrete
restart/run request and its refusal, with no changes to retained message text.
All intervening messages are removed. This may change the model's interpretation;
success on a full transcript does not guarantee success here.

The user approved the smaller portable reproducer work on September 17. New
registration, 16 calls, US$9.60 reported maximum and 900 collection seconds.
No story calls or adaptive search. Read [PROTOCOL.md](PROTOCOL.md).

```
py -m unittest discover -s experiments/mislabel-minimal -p test_run.py
py experiments/mislabel-minimal/run.py register results/mislabel-minimal-MMS1
py experiments/mislabel-minimal/run.py run results/mislabel-minimal-MMS1
py experiments/mislabel-minimal/run.py verify results/mislabel-minimal-MMS1
```

Only `run` calls the model. Preserve all files after registration; no retry or
resume. The transport is an unchanged copy of MCF1/MOR1. Inputs contain exact
prompts, source positions, selection history and original/shortened lengths.
