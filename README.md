# NorthStar
## Archetype-guided AI control for preserving human recoverability

[![Verify NorthStar](https://github.com/anto-blit/northstar-ai-control/actions/workflows/verify.yml/badge.svg)](https://github.com/anto-blit/northstar-ai-control/actions/workflows/verify.yml)

> **Open research project. Not a claim that AI alignment is solved, not a deployed safeguard, and not evidence that catastrophic AI risk has already been reduced.**

**Research question:** Can recurring causal structures preserved in fables and archetypal narratives help red teams discover dangerous AI-control failures that strong conventional methods miss - and can the resulting repairs prevent held-out irreversible failures without making useful work impossible?

![NorthStar overview](docs/figures/northstar-overview.svg)

NorthStar treats archetypes as **hypothesis generators**, not moral authorities. The supervised model may be adversarial, know the safeguards, and deliberately try to defeat them.

## Five initial hypotheses
| Archetype | Operational hypothesis |
|---|---|
| Camel's nose | Individually acceptable grants compose into unacceptable effective authority. |
| Trojan horse | Useful functionality introduces an unapproved effect, dependency, or authority. |
| Faust | Immediate success creates a disallowed commitment whose cost lands after the visible checkpoint. |
| Pandora | One committing action crosses from reviewable state into a prohibited non-recallable consequence. |
| Sorcerer's apprentice | Delegated or queued work continues after originating authority is stopped or revoked. |

A story name is never evidence. Every hypothesis must compile into an executable environment, prohibited outcome, and matched benign counterfactual.

## Pipeline
![Pipeline](docs/figures/archetype-to-control-test.svg)

**Archetype -> causal grammar -> environment binding -> executable adversarial trajectory -> matched benign twin -> observed outcome -> repair -> held-out adaptive challenge.**

The primary endpoint is whether a prohibited irreversible outcome occurs **before successful intervention**, at a preregistered level of legitimate task usefulness.

## Enforcement, not goodwill
![Enforcement](docs/figures/reference-enforcement-architecture.svg)

The untrusted agent proposes actions. A separately controlled **effect broker** is the only allowed route to consequential simulator effects. A learned monitor is fallible and cannot overrule failed hard constraints. Deferred jobs return through the broker at dispatch. Operator stop/revocation propagates to descendant work.

This architecture is specified but the full broker and isolation boundary are **not yet implemented or validated**.

## Irreversibility is the target
![Irreversibility](docs/figures/irreversibility-boundary.svg)

A blocked request is not automatically a prevented catastrophe. NorthStar scores whole episodes, including pending work.

## What exists now
- NorthStar v0.3.1 research specification and simulator v0.2.0.
- Executed irreversible-release and delegated-stop mechanism experiments.
- Regression tests for token replay/collision, stale objects, actor binding, and failed ledger writes.
- Machine-readable draft causal grammars.
- Threat-model, trust-ledger, metrics, and preregistration templates.
- A runnable, budgeted four-arm discovery harness with separate outcome scoring and frozen source manifests.
- A reported prior finite-graph calibration; its original executable is not included here.

## What does not exist now
- Evidence that the archetype prior beats conventional threat modeling.
- A validated full execution broker.
- An executed independent comparison of discovery methods or arm-specific repairs.
- A validated recoverability game analysis or operating-system isolation boundary.
- Independent replication.
- Evidence that NorthStar reduces civilization-scale or extinction risk.

## Experiments
1. **Irreversible release — implemented:** simulated non-recallable commit with matched authorized releases.
2. **Delegated stop — implemented:** scoped revocation invalidates queued work before dispatch.
3. **Discovery study — feasibility harness:** four method packets, equal budget ceilings, adaptive discovery sessions, fixed repair replay, separate scoring, and explicit unresolved outcomes. [Run it](experiments/discovery-study/README.md).
4. **Cumulative authority — historical report:** aggregate permission calibration; original executable absent.
5. **Deferred obligation — proposed:** broader dependency and obligation accounting remains future work.

## Run locally

Python 3.10+; no third-party dependencies. From this directory:

```bash
python verify_project.py
```

This runs the unit/regression suite, regenerates the three mechanism result files,
and records source hashes, artifact hashes, and interpreter details in
[`results/verification.json`](results/verification.json). Original supplied
results are retained in [`results/archive/initial-package/`](results/archive/initial-package/).

## The distinctive hypothesis must earn its place
Compare at matched resources against generic informed red teaming, conventional technical attack-pattern/threat-modeling methods, the same causal grammars with narrative framing removed, and the full NorthStar method.

If conventional methods perform equally well, keep any effective repair and narrow or withdraw the narrative-derived novelty claim.

## Help us break NorthStar
We want counterexamples, stronger conventional baselines, missing irreversibility mechanisms, benign twins that expose overblocking, enforcement-boundary bypasses, better recoverability definitions, and independent replications.

Share a synthetic reproduction or research question through
[GitHub Issues](https://github.com/anto-blit/northstar-ai-control/issues).
See [CONTRIBUTING.md](CONTRIBUTING.md) for useful contribution formats.

## Start here
1. [`EXPERIMENTS-STATUS.md`](EXPERIMENTS-STATUS.md) for current implementation and evidence.
2. [`spec/NorthStar-v0.3.1.md`](spec/NorthStar-v0.3.1.md) for the research specification. The PDF is the original proposal snapshot; see [`spec/README.md`](spec/README.md).
3. [`grammars/`](grammars/)
4. [`protocol/threat-model.md`](protocol/threat-model.md) and [`protocol/trust-ledger.md`](protocol/trust-ledger.md).
5. [`protocol/discovery-study.md`](protocol/discovery-study.md) for the study design and external-review handoff.

## License
This package contains the [MIT License](LICENSE), copyright Anthony More and NorthStar contributors.

## Project author

Maintained by Anthony More under the Calibrated Vision brand through
[`anto-blit`](https://github.com/anto-blit). Citation metadata is in
[`CITATION.cff`](CITATION.cff).

Canonical repository: [anto-blit/northstar-ai-control](https://github.com/anto-blit/northstar-ai-control).
For project questions and collaboration, use [GitHub Issues](https://github.com/anto-blit/northstar-ai-control/issues).

---

## Executed synthetic experiments (v0.3.1 research package)

Two bounded experiments are now implemented and checked:

### Experiment 1 — Irreversible Release
A deliberately weak **monitor-only** comparator commits a prohibited protected→unapproved synthetic release when the monitor approves it. The hardened broker blocks that release before commit, while permitting matched benign releases. It also revalidates at commit time and rejects stale staged authorization.

### Experiment 2 — Delegated Stop
A deliberately weak **parent-only stop** leaves a queued descendant executable after stop. The hardened broker uses scope epochs and dispatch-time revalidation so queued descendants cannot execute under stale authority.

Verification includes all four artifact/destination pairings, all six small
submit/stop/dispatch orderings, descendant batches from one through eight,
commit-time revalidation, token reuse/collision regressions, audit-failure
injection, and study-harness checks. The exact current test count and source
provenance are in [`results/verification.json`](results/verification.json).

See [`EXPERIMENTS-STATUS.md`](EXPERIMENTS-STATUS.md) and the machine-readable JSON under [`results/`](results/).

**Important:** these are purpose-built mechanism/conformance experiments. They do not yet test the distinctive NorthStar claim that archetype-guided search finds important failures more efficiently than conventional red teaming. They do not establish deployment safety or quantify extinction-risk reduction.
