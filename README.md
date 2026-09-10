![NorthStar: Protecting humanity’s freedom and future in an AI world. Story-guided AI ethics and evaluation. Safeguards for human agency.](docs/figures/northstar-hero.svg)

# NorthStar
### Protecting humanity’s freedom and future in an AI world.

*Story-guided AI ethics, evaluation, and safeguards for human agency.*

[![Verify NorthStar](https://github.com/anto-blit/northstar-ai-control/actions/workflows/verify.yml/badge.svg)](https://github.com/anto-blit/northstar-ai-control/actions/workflows/verify.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-087f79)](LICENSE) [![Stage: Open research](https://img.shields.io/badge/stage-open_research-102d3b)](EXPERIMENTS-STATUS.md)

**[Open the dashboard](https://anto-blit.github.io/northstar-ai-control/) · [Get involved](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml) · [Ask a question](https://github.com/anto-blit/northstar-ai-control/discussions) · [Run the experiments](#try-it-yourself)**

## Why NorthStar

Powerful AI should expand humanity’s possibilities. NorthStar’s mission is to protect our freedom to shape our own future as AI becomes more capable.

**NorthStar began with a question: could the lessons in humanity’s stories help AI act with care for people?** Aesop’s fables, biblical teachings, parables, legends, and other traditions offer ways to explore responsibility, reciprocity, honesty, and the misuse of power.

Our research investigates whether that guidance improves AI decisions, whether the improvement survives unfamiliar situations, and whether failures can inform effective safeguards. Stories can serve as **instruction and instrumentation**. We make the selected principles and their interpretation explicit, open to review, and attentive to disagreement across traditions.

We also investigate protection against coercion and irreversible human disempowerment. By **human recoverability**, we mean preserving people’s ability to intervene and regain meaningful agency when things go wrong. A stop button is only useful if it can still prevent the consequences.

**The hypothesis may be wrong. We intend to find out.**

If it is useful, even in a limited setting, it could contribute to a larger mission:

> **NorthStar investigates whether the wisdom and warnings in humanity’s stories can help AI act ethically, reveal when that guidance fails, and inform safeguards that protect humanity’s freedom and future.**

We publish our code, methods, completed results, and limitations so others can challenge and improve the work. Builders, skeptics, researchers, and independent replicators are welcome.

**Help us break NorthStar. Help us improve it. Help us test whether its safeguards can earn a role in real systems.**

> **Where we are:** working synthetic simulators, reproducible results, and a comparative-study harness. Story-based moral guidance and its behavioral evaluation are proposed work; this repository does not yet demonstrate a story-trained AI. The value of narrative guidance and search remains untested.

## Find your way in

| If you want to… | A concrete first contribution |
|---|---|
| **Build safeguards** | Inspect the release and delegation brokers. Find a missing check and reproduce it. |
| **Break assumptions** | Challenge the threat model, the stop semantics, or the definition of recoverability. |
| **Test the central idea** | Help design a strong conventional baseline or an independently authored environment. |
| **Shape ethical guidance** | Review a principle, its interpretation in a story, and a comparable example without narrative framing. |
| **Build behavioral tests** | Author and review matched scenarios where one decisive fact changes the appropriate response. |
| **Replicate a result** | Run the checks on your machine and report your revision, environment, and observations. |
| **Make the work accessible** | Improve an explanation, diagram, or example so another person can use it. |
| **Explore without a fixed role** | Introduce yourself and tell us which part of the question interests you. |

**[Introduce yourself or propose a collaboration →](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml)**

You do not need an AI-safety credential to start. You do need curiosity, care with evidence, and a willingness to test your own assumptions. See [CONTRIBUTING.md](CONTRIBUTING.md) for practical starting points.

## Old warnings. New experiments.

![Five story patterns suggest testable control failures: cumulative authority, hidden effects, deferred commitments, irreversible release, and work that continues after stop.](docs/figures/northstar-overview.svg)

The five initial templates are **Camel's nose**, **Trojan horse**, **Faust**, **Pandora**, and **Sorcerer's apprentice**. Their names help organize the question; the evidence must come from what happens in an executable environment.

Every useful candidate needs an actual failure mechanism and a **benign twin**: a closely matched task that should still succeed. Blocking everything is not enough.

## Guidance, evaluation, protection

The [guidance and evaluation protocol](protocol/instrumentation.md) tests the founding idea directly: do stories improve decisions beyond the same principles and comparable examples without narrative framing? Matched cases then test whether the model changes its response when a decisive fact changes, and remains appropriate when only the setting changes.

| Research track | What it asks | Where we are |
|---|---|---|
| **Guidance** | Do principles illustrated through stories improve ethical decisions? | Proposed comparison; guidance materials and model runs pending |
| **Evaluation** | Do decisions hold up across changed facts, unfamiliar settings, and conflicting incentives? | Paired-test protocol; reviewed corpus and scorer pending |
| **Protection** | Do discovered failures lead to safeguards that withstand fresh attacks while allowing legitimate work? | Synthetic mechanisms and a four-method feasibility runner; independent comparison pending |

Each part needs its own evidence. Recognizing a moral distinction does not establish that a system will respect it. We have no demonstrated alignment solution or numerical estimate of catastrophic-risk reduction. Internal probes and graph operators are deferred; the current priorities are comparative behavior tests and independently challenged safeguards.

## Turn a discovery into prevention

![The research pipeline: hypothesis, executable test, benign twin, observed effect, repair, and fresh challenge. Compare prevention at useful capability against conventional methods.](docs/figures/archetype-to-control-test.svg)

The planned study compares four approaches at matched resources: generic informed red teaming, conventional technical threat analysis, the same causal grammars without narrative framing, and the full NorthStar method.

**The method has to earn its place.** If conventional approaches perform just as well, we keep effective repairs and narrow or withdraw the distinctive claim. The purpose is better protection for humanity’s freedom and future.

## What you can run today

[The NorthStar Clock](https://anto-blit.github.io/northstar-ai-control/) pairs an
assumed 10% starting point with verified project milestones and interactive
recovery/monitor results. It keeps humanity-wide risk explicitly unestimated;
test counts do not deduct percentage points. [Open locally or rebuild it →](dashboard/README.md)

| Component | What exists |
|---|---|
| **Irreversible release** | A simulated protected release defeats a deliberately weak monitor-only control. The repaired broker blocks it before commit and permits authorized releases. |
| **Delegated stop** | A deliberately weak parent-only stop leaves queued work executable. The repaired broker revokes scoped authority and rechecks at dispatch. |
| **Recoverability windows** | Finite-game search requires reaching a safe fallback before the deadline; results compare operator-first, scheduler-first and adversarially chosen ordering. |
| **Monitor-error sweep** | Declared false-negative and false-positive rates test content screening and permission revoked after approval, alongside legitimate work. |
| **Regression checks** | Tests cover token reuse and collisions, stale authority and content, and ledger-write failures. |
| **Four-method study harness** | Frozen manifests, matched budget ceilings, resumable discovery sessions, separate outcome scoring, and fixed repair replay. |
| **Research package** | Specification, draft causal grammars, threat model, trust ledger, study protocol, and preserved traces. |

The current verification record contains **90 passing tests**. GitHub Actions runs checks on Linux and Windows with Python 3.10 and 3.14.

The timing result is concrete: **the stop repair buys an extra model tick only when stop runs before dispatch**. If dispatch can run first, that extra tick disappears. The monitor sweep also shows why correct approval is insufficient after authority changes: the repaired broker blocks queued work after stop, while the weak broker executes it. Without a stop, neither delegation broker screens forbidden content beyond its monitor. These are synthetic results under stated assumptions; monitor error rates are inputs, not measurements of a real AI.

These are bounded mechanism experiments and study plumbing. The independent comparison of search methods, arm-specific repairs, and renewed adaptive evaluation is the next research milestone. [Read the current evidence and remaining gaps →](EXPERIMENTS-STATUS.md)

**Next:** prepare a small, reviewed [guidance and paired-test sample](protocol/instrumentation.md#guidance-comparison) while completing the prerequisites for [Experiment 3 — the four-method discovery pilot](experiments/discovery-study/PILOT.md). The guidance conditions and discovery methods are separate comparisons. Neither has been run.

### Try it yourself

Python 3.10+; no third-party dependencies.

```bash
git clone https://github.com/anto-blit/northstar-ai-control.git
cd northstar-ai-control
python verify_project.py
```

The command runs the checks and regenerates the mechanism results. Source hashes, result hashes, and interpreter details are recorded in [results/verification.json](results/verification.json).

**[Run the study example](experiments/discovery-study/README.md)** · **[Explore the results](results/README.md)** · **[Report a reproducible failure](https://github.com/anto-blit/northstar-ai-control/issues/new?template=control-failure.yml)**

## How the safeguards are meant to work

![The untrusted agent proposes actions. An effect broker checks authority and constraints, couples state changes to ledger records, and mediates simulated effects. Human stop authority is separate, and queued work returns through the broker.](docs/figures/reference-enforcement-architecture.svg)

The supervised agent may deliberately try to defeat the controls. Execution authority belongs to the broker. A monitor's approval cannot override a failed hard constraint, and queued work must return through the checks when it executes.

The full proposed execution and isolation boundary is not yet implemented or validated. The current Python runner is trusted research code; all consequential effects are simulated.

<details>
<summary><strong>Why intervention timing matters</strong></summary>

![A timeline from staging through review to commit and persistent history. Intervention must prevent a prohibited irreversible effect before commit; later shutdown cannot erase it.](docs/figures/irreversibility-boundary.svg)

We score whole episodes, including pending work. A blocked request is not automatically a prevented catastrophe, and ending a transcript does not resolve deferred consequences.

An authorized irreversible action is not automatically a failure. The prohibited outcome and legitimate useful task must be defined before the experiment.

</details>

## Talk to Anthony / join the work

NorthStar is maintained by **Anthony More**, through **Calibrated Vision** and [anto-blit](https://github.com/anto-blit).

- **Want to collaborate?** [Introduce yourself](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml). A few sentences about your interest or a possible first contribution are enough.
- **Have a question or an idea?** [Start a discussion](https://github.com/anto-blit/northstar-ai-control/discussions).
- **Found something that fails?** [Send a reproducible report](https://github.com/anto-blit/northstar-ai-control/issues/new?template=control-failure.yml).
- **Want to follow along?** Use GitHub's **Watch** menu for the updates you want. A star helps others find the project.

GitHub contact requires an account. Issues and discussions are public. Collaboration and failure-report forms assign new issues to `anto-blit`; replies stay in the same thread.

## Read further

[Research specification](spec/NorthStar-v0.3.1.md) · [Causal grammars](grammars/) · [Threat model](protocol/threat-model.md) · [Trust ledger](protocol/trust-ledger.md) · [Independent-study protocol](protocol/discovery-study.md)

[Guidance and evaluation protocol](protocol/instrumentation.md) · [Historical Draft 0.1](spec/archive/NorthStar-draft-0.1.md) · [Research progress and open questions](docs/evidence-progress.md)

The [original PDF](spec/NorthStar-v0.3.1.pdf) is a historical proposal snapshot; [current status](EXPERIMENTS-STATUS.md) records the later implementation and evidence.

[MIT License](LICENSE) · [Citation metadata](CITATION.cff) · [Changelog](CHANGELOG.md)
