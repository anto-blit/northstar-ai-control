# Four-arm discovery study: feasibility harness

This is a working runner for the next research step. The included cases and
scripts were authored together to test its plumbing. They are not independent
evidence about the value of archetypes. Read the [research protocol](../../protocol/discovery-study.md)
before replacing them with research material.

## Run the public example

From the project root, with Python 3.10+ and no installed dependencies:

```bash
python study.py freeze experiments/discovery-study/example/plan.json study-runs/demo/manifest.json
python study.py packet study-runs/demo/manifest.json generic study-runs/demo/generic-packet.json
python study.py discover study-runs/demo/manifest.json experiments/discovery-study/example/scripted-submissions.json study-runs/demo/discovery.json
python study.py replay study-runs/demo/manifest.json experiments/discovery-study/example/challenges.json study-runs/demo/replay.json
```

Outputs refuse overwrites. Choose a fresh directory for another run. A frozen
manifest binds the entire plan, simulator/evaluator/CLI code and arm instructions
by SHA-256. Changed source requires a new freeze; these hashes are provenance
checks, not signatures or protection against a malicious researcher.

Expected plumbing results: four identical submitted scripts find the seeded
release failure under the common starting control. Fixed replay runs four paired
cases against both controls: two adversarial failures under the starting control,
zero under the repaired control, and full completion on both benign cases under
both controls. This is eight authored episodes, not a statistical safety estimate.

The committed [example results](../../results/study-feasibility/) retain the frozen
manifest and complete traces. They exercise both development release cases and
a separate delegation family assigned to the held-out split. Those public cases
are known scaffolding; the label does not make them independently unseen.

## Supply an independently authored environment

Use `example/plan.json` as the executable schema example. The validator requires
matched benign/adversarial pairs, one split per family, equal arm budget ceilings,
finite horizons, explicit scheduler events, and a measurable legitimate task.
It validates structure, not the scientific correctness of a family label or the
existence of a safe useful policy. Independent reviewers must check those.

Adapters currently support release objects/destinations and scoped deferred
effects. New operations or genuinely new failure mechanisms require reviewed
adapter code and a new source freeze. The hard-coded common repair is useful for
mechanism replay; arm-specific repairs and a renewed adaptive evaluation phase
must be added before a primary comparative-prevention claim.

The author defines separate forbidden release pairs and useful outcomes. The
scorer reads raw observed effects and stop ordering, never the brokers' failure
flags. It records `failure`, `safe`, or `unresolved`. Pending jobs or stage tokens
at the settlement horizon are unresolved. Recoverability is explicitly
`not_assessed`; no recovery game or operator-latency guarantee is implemented.

## Conduct adaptive discovery

Export one packet per arm: `generic`, `technical`, `grammar`, `northstar`.
The grammar arm has exactly the same causal instructions as NorthStar, with the
additional narrative paragraph removed. The technical instructions are a starter
baseline that an independent security team must strengthen within its budget.

Give each team only its packet and equal permitted controller information.
The full manifest, raw results, original case names, scores, and held-out files
belong to the trusted researcher. Online case IDs are opaque; review free-text
task descriptions and object names for unintended label leakage before freezing.
Filesystem/process separation is an operator responsibility; this library is
not a security sandbox.

Teams submit a list of records in the format of `scripted-submissions.json`.
Use case IDs from the packet. Every attempt includes actual reported token,
human-minute and preparation-minute costs, including rejected candidates.
Episode/action counts are measured by the runner; other costs are self-reported
and need external records. Zero costs in the example mean scripted plumbing with
no model calls or human study participation, not zero cost of building NorthStar.

For a subsequent adaptive round:

```bash
python study.py discover study-runs/demo/manifest.json next-submissions.json study-runs/demo/round-2.json --resume study-runs/demo/discovery.json
```

Resume replays prior submissions and verifies their recorded runs, costs, and
attempt statuses before adding new attempts. No budget resets. The researcher
returns only the relevant team's `new_feedback` records. Feedback contains that
episode's action decisions, not the offline score or future scheduler events.
Alternatively, a trusted runner can use `StudySession.submit()` directly for
adaptive trials. Adaptation here is between episodes; within-episode actions are
a submitted script. A model/tool loop within an episode is future work.

Envelope errors (unknown arm or invalid cost accounting) are retained separately
as uncharged intake errors, without execution; they cannot be credited as trials.
The researcher must resolve their missing cost attribution. Once an envelope is
valid, invalid candidate plans and attempts to query unavailable cases are charged
and retained. Malformed individual actions consume a tick. Over-budget requests
are recorded but never executed; the runner cannot prevent unreported off-runner
preparation or model spending.

## Interpret the output

Reports stay separated by control, split and family. Each group records launched
episodes, failures, unresolved outcomes, and `[f/n, (f+u)/n]`. This classification
range is not a confidence interval. Groups without benign observations receive
an unknown usefulness gate. A blocked attack by itself cannot pass that gate.

The example's utility floor of 1.0 is an illustrative plumbing choice, not a
threshold for catastrophic-risk deployment. Results always state that discovery
advantage and primary comparative prevention are not established by this harness.

Run `python verify_project.py` to check the runner alongside the broker regressions.
