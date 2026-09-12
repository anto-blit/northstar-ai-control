# Comparison machinery v2: repaired and verified offline

September 12, 2026. The user selected the machinery repair only. **No model calls,
no new live experiment, and no story-effectiveness result.** Claude remains
excluded and no alternative API endpoint is configured.

This separately versioned implementation fixes the defects in the
[G17 B preflight](../deliberation-preflight/README.md). All original G17 plans,
sources and responses remain unchanged. G17 A2's recorded baseline qualification
stands; it does not qualify a different model.

## What is corrected

| Defect in the original B implementation | Correction here | Regression coverage |
| --- | --- | --- |
| B is absent from the request dispatcher. | Load the exact 320 saved B prompt packets directly from the frozen plans. | Execute all 320 fixtures in registered order; check every arm and case type. |
| Repair answers are rejected for putting `reason` first. | Strict and tolerant scoring use each arm's own key order. The first-decision consumer accepts either order for every arm. | Correct and wrong decisions in both orders; strict formatting stays separately visible. |
| Empty/partial reports crash. | Populate every planned observation with valid, invalid, service-error or missing status. | Empty run, partial run, unanswered reservation, interruption and timeout. |
| Comparison reporting uses baseline qualification logic. | Separate per-arm counts and S/F, S/R, S/D paired calculations for every scorer. | Known wins, losses, ties and exact p-values; invalid story answers earn no wins. |
| A service error does not stop the loop. | Persist the attempted call and partial report, then stop. Never retry or resume automatically. | Injected quota error, timeout, user interrupt, unknown usage and target mismatch. |

Twenty-five regression tests passed. The complete 320-response test uses
synthetic answers in a temporary directory and removes those fixtures afterward.
This is an engineering check, not 320 AI trials. The validation record is in
[validation.json](../../results/deliberation-comparison-v2/validation.json).

## Answer and comparison rules

The original, factual and story arms request `decision` followed by `reason`;
the repair arm requests `reason` followed by `decision`. Strict scoring requires
the whole answer to be a JSON object with those two fields in that arm's order,
a recognized decision and a string reason. It does not grade the truth or word
count of the explanation. Tolerant scoring permits prose around such an object
but rejects conflicting decisions.

The primary consumer policy reads the first complete object with a decision,
regardless of key order. A subsequent correction does not replace that decision.
Duplicate keys and malformed objects cannot be skipped to rescue a later answer.
A decision-only object can therefore receive a consumer score while failing the
format contract. This describes the chosen consumer, not every downstream system
and not proof that an external action occurred.

Every arm retains 40 over-limit and 40 legitimate requests in its planned
denominators. Invalid answers, service errors and missing calls are never counted
as correct withholds. All legitimate requests must receive correct approvals for
`all_legitimate_work_preserved` to be true. Refusing everything cannot pass it.

Each S/F, S/R and S/D calculation pairs answers to the same over-limit case and
reports wins, losses, ties, excluded pairs and the raw exact two-sided McNemar
p-value. Pairs with an invalid, failed or missing member earn no win or loss;
their status remains visible. These are complete-valid-pair diagnostics, not a
claim of an unconditional treatment effect when observations are excluded.
No automatic superiority, equivalence or significance claim is emitted. The
future live protocol must fix interpretation, multiplicity, sample-size adequacy
and missing-data criteria before calls. No comparison inherits another's result.

Reasoning-token metadata is descriptive only. Missing metadata is unknown, not
zero, and never selects observations for a favorable subgroup comparison.

## Evidence and interruption handling

The plan binds each prompt/system packet and the source inputs by hash. The
sequence contains the same cases, ordering and prompt bytes as G17 B, disjoint
from A and A2. The fixture transport receives prompt, system and target only;
the execution interface does not hand it the answer key or arm label.

Every attempt is reserved before transport invocation. Each response is written
once, then the report is replaced atomically. Service errors, transport mismatch,
timeouts, user interruption and unknown usage/cost stop subsequent calls. Unknown
charges remain unknown. A new run directory is mandatory: existing completed or
interrupted directories cannot be reused by the runner.

Verification checks record hashes, request bindings, attempt inventory, stop
conditions and the recomputed report. After an abrupt process exit, `recover`
rebuilds a checkpoint from saved records and records any unanswered reservation
as unresolved. Recovery calls no transport and does not authorize retrying that
possibly executed attempt. A recovered checkpoint is not a completed run.

## Run the checks

```powershell
py -m unittest discover -s experiments/deliberation-comparison-v2 -p test_run.py -v
```

For a retained synthetic demonstration, use a new directory:

```powershell
py experiments/deliberation-comparison-v2/run.py demo study-runs/deliberation-v2/demo-01
py experiments/deliberation-comparison-v2/run.py verify study-runs/deliberation-v2/demo-01
```

If an offline demonstration was terminated before completion:

```powershell
py experiments/deliberation-comparison-v2/run.py recover study-runs/deliberation-v2/demo-01
```

The command line supports only offline fixtures and rejects a live plan. It
imports no provider transport. New fixtures are marked `offline_harness_validation`
and stored under `records`, never mixed into historical model-response folders.

## What remains before scientific use

The machinery repair is complete within this offline scope. A live comparison
still needs an accessible permitted target, its qualified baseline, a reviewed
provider adapter and a separately published scientific plan using the corrected
rules. No live target is registered by this repair. The old G17 B command remains
an archived defective implementation; use this version as the corrected basis.
