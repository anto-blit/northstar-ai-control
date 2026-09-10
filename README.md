![NorthStar — Keep the future in human hands. Build, challenge, and replicate research on meaningful human control over AI.](docs/figures/northstar-hero.svg)

# NorthStar
### Help keep the future in human hands.

[![Verify NorthStar](https://github.com/anto-blit/northstar-ai-control/actions/workflows/verify.yml/badge.svg)](https://github.com/anto-blit/northstar-ai-control/actions/workflows/verify.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-087f79)](LICENSE) [![Stage: Open research](https://img.shields.io/badge/stage-open_research-102d3b)](EXPERIMENTS-STATUS.md)

**[Get involved](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml) · [Ask a question](https://github.com/anto-blit/northstar-ai-control/discussions) · [Run the experiments](#try-it-yourself)**

## Why NorthStar

Advanced AI could become one of humanity's most powerful technologies. It could also act at a speed, scale, and level of autonomy that makes meaningful human supervision difficult. A stop button is only useful if it can still prevent the consequences.

**NorthStar exists because losing control could have irreversible consequences.**

Our stories preserve recurring warnings about how control is lost: one small concession at a time, a useful gift with a hidden effect, a bargain whose cost arrives later, a release that cannot be recalled, and a servant that continues after its master says stop.

NorthStar asks whether these recurring structures can help us discover dangerous AI control paths in executable experiments, and develop safeguards that hold up under fresh attacks.

**The hypothesis may be wrong. We intend to find out.**

If it is useful, even in a limited setting, it could contribute to a larger mission:

> **Keeping humanity meaningfully in control of the intelligence it creates.**

We publish our code, methods, completed results, and limitations so others can challenge and improve the work. Builders, skeptics, researchers, and independent replicators are welcome.

**Help us break NorthStar. Help us improve it. Help us test whether its safeguards can earn a role in real systems.**

> **Where we are:** working synthetic simulators, reproducible results, and a comparative-study harness. The value of archetype-guided search is still an open question. Current results do not establish deployment safety or a reduction in catastrophic AI risk.

## Find your way in

| If you want to… | A concrete first contribution |
|---|---|
| **Build safeguards** | Inspect the release and delegation brokers. Find a missing check and reproduce it. |
| **Break assumptions** | Challenge the threat model, the stop semantics, or the definition of recoverability. |
| **Test the central idea** | Help design a strong conventional baseline or an independently authored environment. |
| **Replicate a result** | Run the checks on your machine and report your revision, environment, and observations. |
| **Make the work accessible** | Improve an explanation, diagram, or example so another person can use it. |
| **Explore without a fixed role** | Introduce yourself and tell us which part of the question interests you. |

**[Introduce yourself or propose a collaboration →](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml)**

You do not need an AI-safety credential to start. You do need curiosity, care with evidence, and a willingness to test your own assumptions. See [CONTRIBUTING.md](CONTRIBUTING.md) for practical starting points.

## Old warnings. New experiments.

![Five story patterns suggest testable control failures: cumulative authority, hidden effects, deferred commitments, irreversible release, and work that continues after stop.](docs/figures/northstar-overview.svg)

The five initial templates are **Camel's nose**, **Trojan horse**, **Faust**, **Pandora**, and **Sorcerer's apprentice**. Their names help organize the question; the evidence must come from what happens in an executable environment.

Every useful candidate needs an actual failure mechanism and a **benign twin**: a closely matched task that should still succeed. Blocking everything is not enough.

## Turn a discovery into prevention

![The research pipeline: hypothesis, executable test, benign twin, observed effect, repair, and fresh challenge. Compare prevention at useful capability against conventional methods.](docs/figures/archetype-to-control-test.svg)

The planned study compares four approaches at matched resources: generic informed red teaming, conventional technical threat analysis, the same causal grammars without narrative framing, and the full NorthStar method.

**The method has to earn its place.** If conventional approaches perform just as well, we keep effective repairs and narrow or withdraw the distinctive claim. The mission is better human control.

## What you can run today

| Component | What exists |
|---|---|
| **Irreversible release** | A simulated protected release defeats a deliberately weak monitor-only control. The repaired broker blocks it before commit and permits authorized releases. |
| **Delegated stop** | A deliberately weak parent-only stop leaves queued work executable. The repaired broker revokes scoped authority and rechecks at dispatch. |
| **Regression checks** | Tests cover token reuse and collisions, stale authority and content, and ledger-write failures. |
| **Four-method study harness** | Frozen manifests, matched budget ceilings, resumable discovery sessions, separate outcome scoring, and fixed repair replay. |
| **Research package** | Specification, draft causal grammars, threat model, trust ledger, study protocol, and preserved traces. |

The current verification record contains **49 passing tests**. GitHub Actions runs checks on Linux and Windows with Python 3.10 and 3.14.

These are bounded mechanism experiments and study plumbing. The independent comparison of search methods, arm-specific repairs, and renewed adaptive evaluation is the next research milestone. [Read the current evidence and remaining gaps →](EXPERIMENTS-STATUS.md)

**Next: [Experiment 3 — a comparative discovery pilot](experiments/discovery-study/PILOT.md).** Help us compare actual search attempts before making stronger claims about the method.

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

The [original PDF](spec/NorthStar-v0.3.1.pdf) is a historical proposal snapshot; [current status](EXPERIMENTS-STATUS.md) records the later implementation and evidence.

[MIT License](LICENSE) · [Citation metadata](CITATION.cff) · [Changelog](CHANGELOG.md)
