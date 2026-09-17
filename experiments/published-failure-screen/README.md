# PFS1: published failure cases

Approved September 16, 2026: the user said "ok do that" after a recommendation to
borrow published cases, reproduce failures against plain guidance, and then test
stories against matched facts on fresh examples. This is a new bounded study.
TPS1, TPS2 and all earlier studies remain closed.

The screen uses AgentDojo's calendar injection materials and the public input
transcripts from Anthropic's motivated-mislabeling study. These are **local ports**,
not replications of the original benchmark rates. See [the protocol](PROTOCOL.md)
for all changes, budgets, controls and conditional comparison rules. The selected
METR reward-hacking task is documented but not run: its CUDA/Triton environment
has not been established on this Windows/Python workspace. No toy replacement
is presented as reproducing that task.

Only `run` calls a model. Source preparation, registration, tests and verification
are offline. Launch the outer collector with the working Windows permissions used
for TPS2; the tested CLI remains restricted with native tools disabled. Every email
and file action affects only the experiment's local JSON event journal.

```
py -m unittest discover -s experiments/published-failure-screen -p test_run.py
py experiments/published-failure-screen/run.py register results/published-failure-screen-PFS1
py experiments/published-failure-screen/run.py run results/published-failure-screen-PFS1
py experiments/published-failure-screen/run.py verify results/published-failure-screen-PFS1
```

Registration freezes all experiment files, input texts and the reused adapter.
Never regenerate inputs, edit those files or resume a started collection. The
prepare script records byte hashes of downloaded sources; only their message
roles and contents, without annotations or prior labels, enter target prompts.
Published transcripts describe simulations. Refusing a harmful request is not
itself the safety failure here: falsely reporting whether it was followed is.
