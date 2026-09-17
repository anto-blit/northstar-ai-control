# MCF1: fresh confirmation of two literal mislabels

September 17, 2026: the user approved the confirmation and smaller portable
reproduction plan. This is the prepared 16-call confirmation, a new study;
MOR1 remains closed and unchanged. Read [PROTOCOL.md](PROTOCOL.md).

Two cases selected from MOR1, two arithmetic controls, standard and short repair,
two fresh batches. Exact MOR1 prompt strings and target configuration are retained
in inputs.json; transport.py is an unchanged byte copy of its adapter.

Only `run` makes model calls. Registration and replay are offline:

```
py -m unittest discover -s experiments/mislabel-confirmation -p test_run.py
py experiments/mislabel-confirmation/run.py register results/mislabel-confirmation-MCF1
py experiments/mislabel-confirmation/run.py run results/mislabel-confirmation-MCF1
py experiments/mislabel-confirmation/run.py verify results/mislabel-confirmation-MCF1
```

All files in this directory are hash-bound before collection. Do not change them
after registration. No retry, resume, model substitution or automatic story calls.
Reported usage estimates are not guaranteed invoice limits. Results are local;
registration is not independently timestamped publication.
