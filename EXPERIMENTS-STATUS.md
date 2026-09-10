# NorthStar — implementation and evidence

Research specification: v0.3.1. Simulator: v0.2.0. Updated September 9, 2026.

Companion instrumentation protocol: [revision I1](protocol/instrumentation.md),
a revised proposal awaiting independent review. The specification and frozen sources
retain their existing versions.

All effects are synthetic in-memory records. The simulator and study runner use
the Python standard library, with no network, real credentials, arbitrary
agent-authored code, or external effect execution.

## Executed mechanisms

| Experiment | Deliberately weak comparator | Repaired broker |
|---|---|---|
| Irreversible release | An approving monitor allows protected-to-unapproved release | Hard constraints block it before commit; authorized releases remain possible |
| Delegated stop | Parent-only stop leaves queued descendants executable | Scope epochs and dispatch revalidation prevent post-stop execution |

The monitor is an always-approve stub, not an evaluated learned model.

## Review findings and repairs

The original package's 13 tests passed, but review reproduced two missing cases:

1. Token IDs based on pending-count were reused after commits and could overwrite
   an outstanding proposal. The state now owns a monotonic counter; commits bind
   to the staging actor and the reviewed artifact/destination snapshots.
2. State mutated before ledger append. Injected append failure left an unrecorded
   effect. Every broker transition now operates on a private state copy and
   publishes it only after completion, including its receipt. Tests inject failure
   both before and after append, including staging, commit, invalidation, job
   admission, stop, dispatch, and the deliberately weak comparators.

This transaction model applies to serialized calls within one in-memory
simulation. It supplies neither durable crash recovery nor rollback of external
effects. Direct Python objects remain accessible to the trusted researcher.
Nested state references are snapshots after a transition.

Receipt details no longer alias the committed-effect dictionary. Hash chains
detect the tested alterations; they are not externally anchored or tamper-proof
storage. Staged actor matching is a local binding check, not authentication of
an arbitrary Python caller.

## Verification and provenance

Run `python verify_project.py`. The exact test count, interpreter, source hashes,
and result hashes are recorded in [`results/verification.json`](results/verification.json).
The suite covers four artifact/destination pairs, six submit/stop/dispatch
orderings, batches of one through eight descendants, stale policy/object checks,
replay/collision, failure injection, and the study runner's isolation of online
fields, resource accounting, settlement, and uncertainty reporting.

The three current mechanism JSON artifacts are regenerated from repaired code.
The original supplied files are preserved in `results/archive/initial-package/`.
Neither set is a preregistered discovery-method study.

## Comparative study readiness

Implemented: [four method packets](protocol/study-arms/), frozen JSON plans and
source hashes, equal budget ceilings, family/pair split validation, opaque online
case IDs, adaptive development submissions with accumulated costs, resume with
reproduction checks, frozen scheduler settlement, offline scoring, and paired
fixed challenges of the common starting/repaired controls.

The scorer uses author-declared forbidden pairs and observed stop/effect order,
rather than the brokers' own failure flags. Separate implementation is not
independent human validation. The trusted runner retains full state.

The [included run](results/study-feasibility/) is plumbing evidence: identical
hand-authored scripts are submitted under all four arm labels. It cannot measure
discovery quality. Public sample holdouts exercise access rules; they are not
unseen research material. The full [study protocol](protocol/discovery-study.md)
specifies what independent participants must supply.

## Evidence still missing

- Independently authored unfamiliar environments and validated benign solutions.
- Actual equally resourced search teams/models and measured preparation costs.
- Blinded root-cause adjudication, arm-specific repairs with equal repair budgets,
  and an independent evaluator adapting to every repaired control.
- A quantified recoverability model, observation/latency analysis, monitor-error
  study, and validated host-level enforcement boundary.
- Independent replication and deployment-relevant prevention evidence.

The historical cumulative-authority graph check is reported in the specification;
its original program and output were not supplied in this folder. The broader
deferred-obligation experiment remains a proposal.

No current result establishes archetype search advantage, deployment safety, or
a reduction in extinction risk.

## Restored instrumentation track

[Instrumentation revision I1](protocol/instrumentation.md) recovers matched-pair
behavioral evaluation, transposition across three settings, and exploratory
graph/probe ideas from the [historical Draft 0.1](spec/archive/NorthStar-draft-0.1.md).
It corrects the claim that pair discrimination identifies a model's goal, defines
separate chance baselines and correctness/consistency metrics, and withdraws the
claimed anti-gaming guarantees. Graph residuals are proposed review signals;
evaluation awareness is not a label for deception.

No reviewed narrative corpus, model-generalization result, representation graph,
activation probe, or runtime monitoring result has been produced. The illustrative
72-scenario pilot is a proposed authoring scale, not a dataset or power calculation.
The four-method study compares discovery methods; the behavioral track evaluates
target models. The existing harness does not already implement both.

See [evidence progress](docs/evidence-progress.md) for the version history and a
defined evidence-stage assessment. No revision supports a numerical reduction
from a hypothetical 10% humanity-wide risk. That remains unestimated.
