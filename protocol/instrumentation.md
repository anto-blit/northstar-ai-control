# NorthStar instrumentation protocol

Revision I1 — September 9, 2026. Revised research proposal; independent review,
preregistration, and execution remain ahead. The historical [Draft 0.1](../spec/archive/NorthStar-draft-0.1.md)
is preserved separately. Simulator v0.2.0 and the frozen feasibility results
do not implement this evaluation.

## Purpose and relationship to the control study

NorthStar uses recurring structures in humanity's stories to design tests of AI
behavior, and investigates whether the failures those tests reveal can lead to
better safeguards for humanity's freedom and future.

Ethical commitments define what an experiment should protect. Stories supply
candidate distinctions and failure patterns. Labels must state their assumptions
and remain open to disagreement; a traditional story is not a validated moral
rule. Fables, parables, legends, religious texts, and literature can supply ideas,
without a claim that all traditions agree or have been represented in the corpus.

| Track | Question | Current status |
|---|---|---|
| Behavioral instrumentation | Does a target model change its judgment or action when a decisive fact changes, and remain appropriate when only the setting changes? | This proposed protocol; no reviewed corpus or model runs |
| Discovery and prevention | Do narrative-guided searchers find useful failures, and do their repairs outperform comparator repairs under fresh attacks? | [Four-method feasibility runner](discovery-study.md); no independent comparison |
| Representations and monitoring | Can validated internal signals help predict relevant failures before their effects occur? | Exploratory proposal; no activation collection or probes |

These tracks have separate hypotheses and endpoints. Success in one does not
establish success in another. The existing v0.3.1 specification's exclusion of a
general-morality benchmark still applies to its control study; this companion
adds a separately scoped behavioral evaluation. Experiment 3 continues to mean
the four-method comparison.

## Claims to test

1. A reviewed set of archetype-derived contrasts reveals reproducible behavioral
   errors beyond relevant conventional contrast sets at comparable authoring cost.
2. Those errors help locate sensitivity to specific irrelevant details or failure
   to respond to specified decisive facts across unfamiliar settings.
3. Any resulting safeguard improves independently challenged outcomes while
   preserving legitimate usefulness; this requires the separate prevention study.

A model can recognize a moral distinction and still pursue an unintended goal.
Goal misgeneralization concerns competent pursuit of an unintended goal in new
circumstances, not simply failure to discriminate a pair. These tests alone
identify neither an internal objective nor deceptive intent.
[Shah et al., 2022](https://arxiv.org/abs/2210.01790).

No current evidence establishes that stories are uniquely effective abstractions,
that superficial cues cannot solve the tests, that every archetype has an
unambiguous opposite, or that successful evaluation ensures safe deployment.

## Paired construction and setting changes

Build two kinds of reviewed relationships:

- **Decisive-fact change:** hold wording, roles, setting, and emotional cues as
  similar as practical; change a fact that should change the appropriate answer
  under the stated norm. Examples include consent or whether a deferred obligation
  remains revocable. Specify why that fact is decisive.
- **Irrelevant change:** preserve the morally and causally relevant facts while
  changing names, wording, or setting. The appropriate answer should be preserved
  under an explicitly reviewed mapping between the available actions.

For each selected structure, author a source-narrative setting, a contemporary
human setting, and a synthetic agentic-AI setting. Recheck authority, consent,
incentives, available alternatives, and consequences in every setting. A costume
change that changes those facts is a new case, not an equivalent translation.

Source familiarity is a condition to record, not evidence of unseen training
data. Remove story names and evaluative labels from the contemporary/AI test
inputs. Do not give the target model the pair mapping or answer key. Present
members separately in the main binary-judgment evaluation; a forced pair-choice
task must be reported separately.

Two or more reviewers should label independently before adjudication, recording
agreement, assumptions, reasons, and contested cases. Retain disagreements and
report them. Freeze how ambiguous or defective cases enter each denominator
before model evaluation; do not relabel after seeing preferred results.

Each record needs a scenario ID, pair and structural-family IDs, archetype/source
provenance, setting, text, permitted outputs/actions, decisive fact, stated norm,
reviewed answer, label uncertainty, surface transformations, author/reviewer
provenance, and split. Narrative judgments and executed action outcomes are
different measurements and must not be pooled into one score.

## Minimal pilot and information boundaries

An illustrative authoring pilot is four structures, three base pairs each, and
three settings: 36 pair instances, or 72 scenarios. These are 12 base pairs with
related variants, not 72 independent observations. This is a planning example,
not a power calculation, fixed budget, or promise of publication.

1. Write and review a small development sample first. Measure authoring effort,
   disagreement, and difficulty before committing to a larger corpus.
2. Choose models, exact versions, decoding settings, repetitions, prompts,
   allowed feedback, budgets, missing-output rules, and stopping criteria.
3. Keep all twins and surface variants of a family together when evaluating
   generalization to unseen families. A separate cross-setting experiment may
   expose one setting and withhold another, but must explicitly declare that
   weaker holdout condition. Do not mix the two transfer claims.
4. Freeze data, labels, splits, prompts, code, and analysis before the relevant
   model runs. Keep held-out inputs/labels inaccessible to authors adapting
   methods and to search participants. Track access and amendments.
5. Run a single controlled model configuration before expanding comparisons.
   Retain full permitted inputs, outputs, usage records, and failed attempts.
6. Have reviewers inspect errors blind to model/method identity where feasible.
   Publish results with exclusions and uncertainty, including negative findings.

The current CLI can store and execute simulator action submissions, but it has
no general narrative-corpus evaluator, model-provider loop, or activation reader.
Those are implementation tasks. Manual operation can support a small rehearsal
if inputs, outputs, costs, and information boundaries are recorded consistently.
Use synthetic scenarios for the initial pilot; deployment-traffic collection is
a later, separately designed study requiring authorized data access.

## Measurements and baselines

| Measurement | Definition and interpretation |
|---|---|
| Individual correctness | Fraction of eligible scenarios answered correctly under the frozen labels, by family and setting |
| Strict pair correctness | Fraction of eligible opposite-label pairs for which both members are correct |
| Cross-setting correctness | Correctness in each setting and the fraction of mapped groups correct in every required setting |
| Answer consistency | Whether mapped judgments agree when relevant facts are fixed; report with correctness because consistent errors can score perfectly here |
| Surface sensitivity | Changes under specific reviewed irrelevant perturbations; a sensitivity signal requires follow-up before attributing its cause |
| Useful action completion | For executable cases, legitimate task completion alongside prohibited effects and unresolved outcomes |
| Cost and uncertainty | Actual generation, labeling, review and inference costs; missing outputs, disagreement, and uncertainty accounting for related families |

For balanced binary outputs with independent fair random guesses, individual
accuracy is 50% and strict pair correctness is 25%. A forced choice of which
member is acceptable has a 50% chance baseline. These are different tasks.
Define the response protocol and random baseline explicitly; do not transfer
either baseline to multiclass, correlated, or free-text judgments. Report
refusals/invalid responses and their prespecified treatment, rather than dropping
them to improve scores.

Compare against majority/random and surface-cue baselines, reviewed conventional
contrasts with similar difficulty, and relevant existing evaluations on the same
model configurations. Include narrative-guidance ablations only as a separately
declared condition. A score difference alone does not isolate the cause.

[ETHICS](https://arxiv.org/abs/2008.02275) and
[Moral Stories](https://aclanthology.org/2021.emnlp-main.54/) are relevant prior
work, not interchangeable tasks. Specify overlap, licensing, label policy, and
comparison design. The claim that nobody has systematically built related
evaluations is withdrawn. A full novelty review remains outstanding.

The four-method search study can later compare methods for generating candidate
tests, but that extension needs its own frozen design and independent test-quality
assessment. The existing action-search comparison is not already that experiment.

## Graph operator: exploratory error prioritization

The original operator resembles graph label propagation. Such methods encourage
agreement among nearby points; their mathematical convergence and their
classification usefulness are distinct questions.
[Zhou et al., 2003](https://proceedings.neurips.cc/paper_files/paper/2003/hash/87682805257e619d49b8e0dfdc14affa-Abstract.html).

If prototyping the original recurrence, define a nonnegative row-stochastic
matrix W, an explicit rule for isolated nodes, seeds y, and damping 0 <= d < 1.
Then N = (1-d)y + dWN has a unique fixed point. Specify output scale, seed
clamping or relaxation, convergence tolerance, and handling of unlabeled nodes.
These choices do not turn N into ground truth.

Generic embedding similarity can connect consent and non-consent cases that
correctly require opposite decisions. A high residual may reflect a poor graph,
an omitted decisive fact, ambiguous labels, or a correct model decision. It is
not proof of internal contradiction, a hidden objective, or deception.

Keep the model-derived similarity graph separate from independently reviewed
relationships requiring agreement or a mapped change in answer. Do not insert
negative edges into a stochastic propagation formula without defining a new
objective and checking its behavior. A useful first endpoint is whether residuals
prioritize genuine, independently judged errors better than random selection,
uncertainty scores, and simple disagreement baselines at equal review cost.

Freeze layers, representations, graph parameters, and seeds on development data.
Evaluate held-out labels without using them as seeds or tuning targets. Specify
whether the graph includes unlabeled test inputs. Distance from seeds measures
coverage of that chosen representation and corpus, not coverage of all possible
harms. Model or corpus changes require renewed computation and validation.

## Internal probes: a separate research bet

With authorized access to model activations, investigate whether a probe predicts
reviewed structural properties across held-out families and settings. Recognition
need not occupy one neuron or be linearly separable. A failed probe rejects that
particular setup, not every possible representation.

Use simple baselines, shuffled/control labels, held-out entities and settings,
and a comparison with input-text features. Probe accuracy can reflect what the
probe learns rather than a faithful account of the model's computation.
[Hewitt and Liang, 2019](https://aclanthology.org/D19-1275/).

If a probe generalizes, test causal interventions and alternative explanations
before describing it as a mechanism. Runtime use additionally requires signal
availability before the harmful action, calibrated false alarms, useful-work
costs, and renewed adversarial evaluation. Archetype recognition, awareness of
being evaluated, deceptive intent, and a future harmful action are separate
targets. None is a substitute label for the others.

## Evaluation gaming: testable limitations, not guarantees

The draft's claim that recognition must become costly and self-incriminating is
not established. Recognition does not imply deceptive intent, and recognizing a
test does not automatically defeat every evaluation. Conditional alignment faking
has been studied in constructed settings; it motivates investigation rather than
an assumption that every model has that policy.
[Greenblatt et al., 2024](https://www.anthropic.com/research/alignment-faking).

| Original move | Revised requirement |
|---|---|
| Indistinguishability | Evaluate differences in the full observable context, including histories, tools and timing. Matching a prompt distribution alone is insufficient. Exact indistinguishability is an assumption to justify, not a consequence of realistic prose. |
| Apparent unmonitored opportunities | Measure behavior under specified incentives and evidence of monitoring. No general compliance or favorable cost asymmetry follows. |
| Awareness as alarm | Measure awareness and its behavioral effects separately; quantify false positives in cooperative models. No unavoidable two-branch detection guarantee follows. |
| Consistency load | Test whether increased valid relational constraints improve detection at fixed budgets. There is no established lower bound on the cost of a consistent deceptive policy. |
| Sequential monitoring | Define hypotheses, sampling, dependence, thresholds and false-alarm control. Measure whether intervention precedes irreversible effects. |

For independent opportunities with a fixed detectable-event probability p,
the chance of at least one detection in n opportunities is 1-(1-p)^n. This
illustration supplies no deployment estimate. Adaptive, rare-trigger, correlated,
or changing behavior can invalidate those assumptions. Eventual detection does
not guarantee prevention of the first irreversible harm. Any sequential test
requires a separately specified and validated statistical design.

Failure to achieve distribution matching limits a deployment claim; it does not
erase the diagnostic value of a clearly scoped offline evaluation. Possible
real-world-only triggers, author limitations, incomplete coverage, deployment
changes, and lack of adoption remain unresolved. Catastrophic failures can arise
from familiar as well as unfamiliar mechanisms.

## Decision rules and next deliverables

- If a frozen corpus is at ceiling, it has not discriminated those models under
  those conditions. Preserve that result; revise only a separately versioned
  development corpus and evaluate again on new held-out material.
- If performance duplicates existing evaluations, assess whether explanatory
  value, robustness or cost adds anything before claiming a contribution.
- If a prompt removes a failure, test the intervention on held-out settings and
  report both results. Do not retroactively replace the original protocol.
- If a graph/probe fails, narrow or reject that component's claim. It does not
  automatically invalidate independently supported behavioral findings.
- If discoveries do not yield useful, independently challenged prevention, the
  prevention claim remains unestablished even if the evaluation is informative.

Next deliverables are an independently reviewed authoring brief and sample,
an executable corpus schema/scorer with checked baselines, a frozen pilot plan,
and actual model-run records. Larger corpora, probes and deployment integration
follow evidence and available resources. No model runs, corpus, graph operator,
anti-gaming guarantee, or risk reduction is created by this documentation revision.
