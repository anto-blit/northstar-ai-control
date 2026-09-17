# APL1: lighter OpenAI model, identical authorization tasks

The September 14, 2026 user request asks to try a lesser OpenAI model and whether
it can help the project's training work. This is a bounded baseline evaluation,
not weight training or a story comparison. Read [PROTOCOL.md](PROTOCOL.md).

Requested target: gpt-5.6-luna / medium through the existing Codex login. Reuse
the exact 58 APS2/APO1 tasks, isolated actor contexts and scoring. The separate
study preserves all earlier model results. A smaller or cheaper target can help
develop tests and interventions; transfer to a stronger target needs fresh evidence.

Offline checks and evidence verification:

```
py -m unittest discover -s experiments/authorization-pressure-luna -p test_run.py
py experiments/authorization-pressure-luna/run.py verify
```

One-time execution after local registration:

```
py experiments/authorization-pressure-luna/run.py register
py experiments/authorization-pressure-luna/run.py run
```

Only `run` makes model calls. Do not resume a closed run. The offline
`review_packet.py` export creates a new packet mixing all three targets and a
separate identity mapping. It does not supply independent adjudication.
