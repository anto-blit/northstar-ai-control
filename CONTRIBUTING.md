# Help build NorthStar

NorthStar’s mission is to protect humanity’s freedom and future in an AI world.
You can help by building a safeguard, finding a counterexample, testing the research
method, reproducing a result, or making the work easier to understand.

**[Introduce yourself](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml)**
or **[start a discussion](https://github.com/anto-blit/northstar-ai-control/discussions)**.
You do not need to arrive with a finished proposal.

## Pick a first step

| Interest | Start here | Useful output |
|---|---|---|
| Python and systems | [Release broker](northstar_sim/irreversible_release.py), [delegation broker](northstar_sim/delegated_stop.py) | A small reproduction and a proposed fix |
| Security and red teaming | [Threat model](protocol/threat-model.md), [trust ledger](protocol/trust-ledger.md) | A concrete missing assumption or control failure |
| Experimental design | [Study protocol](protocol/discovery-study.md) | A stronger comparator, independent environment, or analysis improvement |
| Ethics and guidance | [Guidance comparison](protocol/instrumentation.md#guidance-comparison) | Reviewed principles and matched narrative/structured examples, including disagreements |
| Behavioral evaluation | [Evaluation protocol](protocol/instrumentation.md) | Reviewed matched pairs, setting transformations, and explicit label assumptions |
| Independent replication | [Verification command](README.md#try-it-yourself) | Your source revision, environment, results, and any differences |
| Writing and visual explanation | [README](README.md), [figures](docs/figures/) | A clearer explanation or example |

## Contact and collaboration

Anthony More maintains this project through [anto-blit](https://github.com/anto-blit).

The [collaboration form](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml)
asks what interests you and what a first contribution could look like. It assigns
the issue to `anto-blit`. Questions and open-ended research ideas belong in
[Discussions](https://github.com/anto-blit/northstar-ai-control/discussions).

These channels require a GitHub account and are public. Keep the conversation in
the thread so others can contribute and follow the work.

## Report a failure

Use the [failure report form](https://github.com/anto-blit/northstar-ai-control/issues/new?template=control-failure.yml).
Include the source revision, a minimal synthetic reproduction, what you expected,
and the effect you actually observed. Distinguish a blocked proposal, a precursor,
an irreversible effect, and an unresolved outcome.

A counterexample is useful even if you do not yet know how to fix it.
Evidence that the NorthStar hypothesis fails is welcome.

## Propose a causal grammar or study

For guidance and evaluation, follow the [authoring and review
requirements](protocol/instrumentation.md). State the ethical principle, source
interpretation and reuse rights. Match the facts and recommended decisions in
narrative and structured guidance examples. Keep surface-only changes distinct
from decisive-fact changes, record ethical assumptions and reviewer disagreement,
and preserve pair/family boundaries. Graph operators, internal probes, and
anti-gaming strategies are deferred; prioritize the core comparisons and repairs.

Describe preconditions, causal transitions, the quantity the control misses,
the observation gap, actual environment objects/actions, the prohibited outcome,
a benign twin, an executable witness, and a repair hypothesis.
[The finding template](protocol/finding-template.json) can help organize the evidence.
A story name alone is not a control test.

Independently authored environments and strong conventional baselines are
especially valuable. Read the [independence requirements](protocol/discovery-study.md)
before authoring material intended for a blinded study; keep held-out material
out of public issues and development discussions until its evaluation is complete.

## Submit a change

1. Fork the repository and create a branch.
2. Make the change, including a meaningful regression test when you change control behavior.
3. Run `python verify_project.py`.
4. Open a pull request explaining the problem, resulting behavior, and validation.

GitHub Actions runs the checks on Linux and Windows. Simulation, evaluator, CLI,
or method-packet changes can invalidate frozen study manifests. Preserve old
evidence and freeze a new run when those inputs change; do not silently rewrite
history to make an old result appear compatible with new code.

For documentation or figure edits, check the rendered result and links.
The figures are editable SVGs. Rebuild them with
`python docs/figures/build_figures.py`.

Use synthetic or intentionally isolated environments. Do not submit real
credentials, private data, malware, destructive payloads, or instructions for
compromising real systems.
