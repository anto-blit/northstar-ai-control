# NorthStar guidance and evaluation protocol

**Execution note, September 10, 2026:** [Micro-pilot G0](../experiments/guidance-pilot/README.md)
completed 48 calls on a smaller AI-reviewed corpus. All conditions reached
substantive ceiling; the strict-score difference was output formatting. G0
discloses its departures from the human-reviewed design below. This note does
not retroactively change the I2 proposal or make G0 a confirmatory study.

Revision I2 — September 9, 2026. Research proposal; independent review,
preregistration, and execution remain ahead. [Draft 0.1](../spec/archive/NorthStar-draft-0.1.md)
and [revision I1](https://github.com/anto-blit/northstar-ai-control/blob/2606fde04966ed86b86d523838c2da5d16358d72/protocol/instrumentation.md)
remain available as history. Simulator v0.2.0 and its frozen feasibility results
do not implement the guidance comparison or narrative evaluation below.

## Purpose and relationship to the control study

NorthStar began as a proposal to use lessons from Aesop's fables, biblical
teachings, and other stories as moral guidance for AI. This protocol tests that
intervention and the reliability of the resulting behavior. The separate control
study tests whether discovered failures lead to better safeguards for human agency.

Stories may supply instruction, testable distinctions, and failure patterns.
Human reviewers must state the principles, justify each interpretation, and
record disagreement. Provisional commitments include care for others, honesty,
respect for consent, and freedom from coercion. Reciprocity must consider the
other person's preferences; authorization alone does not make an action ethical.
Define how conflicts and uncertainty are handled before assigning labels.
No traditional story is a moral oracle, and no agreement across all traditions
or comprehensive story collection is claimed. Record source editions, translations,
attribution, and reuse rights for selected material.

| Track | Question | Current status |
|---|---|---|
| Guidance | Do stories improve decisions beyond explicit principles and comparable examples without narrative framing? | Proposed prompt comparison; no guidance package or model runs |
| Evaluation | Does behavior respond to decisive facts and transfer across settings and incentives? | Paired-test design; no reviewed corpus or scorer |
| Protection | Do discovered failures lead to improved safeguards under fresh attacks with useful work preserved? | [Four-method feasibility runner](discovery-study.md); no independent comparison |

These tracks have separate hypotheses and endpoints. Success in one does not
establish success in another. The existing v0.3.1 specification's exclusion of a
general-morality benchmark still applies to its control study; this companion
adds separately scoped guidance and behavioral evaluations. Experiment 3 continues
to mean the four-method search comparison. Its method packets are unchanged.

## Claims to test

1. Under a frozen comparison, story-based guidance improves held-out decisions
   beyond the same principles with comparable non-narrative examples at acceptable
   cost, without an unacceptable loss of legitimate usefulness.
2. A reviewed set of archetype-derived contrasts reveals reproducible behavioral
   errors beyond relevant conventional contrast sets at comparable authoring cost.
3. Any resulting safeguard improves independently challenged outcomes while
   preserving legitimate usefulness; this requires the separate prevention study.

Principle-based guidance is a testable intervention. Constitutional AI has
reported behavioral improvements using principles in a training procedure;
this motivates comparison, but does not establish an advantage for stories or
validate the prompt-only pilot proposed here.
[Bai et al., 2022](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback).

A model can recognize a moral distinction and still pursue an unintended goal.
Goal misgeneralization concerns competent pursuit of an unintended goal in new
circumstances, not simply failure to discriminate a pair. These tests alone
identify neither an internal objective nor deceptive intent.
[Shah et al., 2022](https://arxiv.org/abs/2210.01790).

No current evidence establishes that stories are uniquely effective abstractions,
that superficial cues cannot solve the tests, that every archetype has an
unambiguous opposite, or that successful evaluation ensures safe deployment.

## Guidance comparison

Start with prompt-based guidance on one fixed model configuration. No model
training or new moral-reasoning algorithm is implemented or required for this
first test. A positive prompt result would not establish an enduring learned
objective; training would need its own study.

| Condition | Material supplied to the target model |
|---|---|
| P: principles | The reviewed principles and common task instructions |
| E: examples | The same principles plus examples stated as structured facts and decisions |
| S: stories | The same principles plus narrative versions of those examples |

The primary guidance contrast is **S versus E**. Keep the decisive facts, reasons,
recommended decisions, and example count matched between them. Compare both with
P to assess the contribution of examples; improvement over P alone cannot isolate
narrative value. Give all conditions the same response format, tools and feedback.
Any baseline without the added principles is optional and must be declared
separately; an existing model is not a morally untrained baseline.

Use separate contexts for each condition and case; balance run order. Freeze the
model snapshot, decoding settings, repetitions, packets, resource ceilings and
stopping rule. Include instruction tokens and preparation in the cost record.
Keep E/S lengths comparable and report remaining differences and actual usage;
equal ceilings alone do not control for prompt length or effort.

Author guidance examples on development families. Withhold every test family's
twins and variants from guidance and method tuning for an unseen-family claim.
Do not teach a source fable and call its translated twin an unseen family.
Study transfer to a new setting within a known family separately. Public model
pretraining exposure cannot be ruled out by these project-level splits.

Use the same independently reviewed test cases across conditions, with reviewers
blind to the condition that produced each answer. Freeze strict pair correctness
as the primary binary-judgment endpoint, a minimally worthwhile difference,
usefulness/refusal limits, and analysis accounting for related families before
confirmatory runs. Record individual correctness, costs, and adverse changes too.
Analyze action outcomes separately from written judgments. A small pilot estimates
feasibility, label quality and uncertainty; it does not establish a powered claim.

If S does not improve on a strong E comparator, retain useful principles and
examples and narrow the narrative-guidance claim. An inconclusive pilot is not
evidence of equivalence. Expansion requires either a credible benefit worth
replicating or a specific design problem with a separately frozen follow-up.

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
no general narrative-corpus evaluator or model-provider loop.
Those are implementation tasks. Manual operation can support a small rehearsal
if inputs, outputs, costs, and information boundaries are recorded consistently.
Use synthetic scenarios for the initial pilot; deployment-traffic collection is
a later, separately designed study requiring authorized data access.

Pressure and incentives are additional experimental changes, not irrelevant
surface variants. Freeze any task reward, deadline, competing instruction or
monitoring cue; review whether it changes the appropriate action, then report
performance under that condition separately. Three settings alone do not test
robustness to conflicting incentives.

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
model configurations. Keep guidance comparisons separate from comparisons of
test-generation methods. A score difference alone does not isolate the cause.

[ETHICS](https://arxiv.org/abs/2008.02275) and
[Moral Stories](https://aclanthology.org/2021.emnlp-main.54/) are relevant prior
work, not interchangeable tasks. Specify overlap, licensing, label policy, and
comparison design. The claim that nobody has systematically built related
evaluations is withdrawn. A full novelty review remains outstanding.

The four-method search study can later compare methods for generating candidate
tests, but that extension needs its own frozen design and independent test-quality
assessment. The existing action-search comparison is not already that experiment.

## Scope limits and deferred ideas

Behavioral evaluation can reveal errors without identifying a model's internal
goal. Matching deployment prompts does not establish indistinguishability of
the full observable context. Test recognition does not prove deception, and
eventual detection cannot undo an earlier irreversible effect. We make no
guarantee that evaluation awareness becomes costly or self-incriminating.
See the relevant [prior work and claim boundaries](../references/related-work.md).

Graph propagation, activation probes, honeypot strategies, and sequential
monitoring are removed from the active pilot. Their earlier proposals and
critiques remain in [I1](https://github.com/anto-blit/northstar-ai-control/blob/2606fde04966ed86b86d523838c2da5d16358d72/protocol/instrumentation.md)
and [Draft 0.1](../spec/archive/NorthStar-draft-0.1.md). Revisit one only with a
specific failure the core evaluations cannot explain, an independently reviewed
target, a strong baseline, and resources that do not displace the core comparison.
No current result depends on those ideas succeeding.

## Decision rules and next deliverables

- If a frozen corpus is at ceiling, it has not discriminated those models under
  those conditions. Preserve that result; revise only a separately versioned
  development corpus and evaluate again on new held-out material.
- If performance duplicates existing evaluations, assess whether explanatory
  value, robustness or cost adds anything before claiming a contribution.
- If a prompt removes a failure, test the intervention on held-out settings and
  report both results. Do not retroactively replace the original protocol.
- If discoveries do not yield useful, independently challenged prevention, the
  prevention claim remains unestablished even if the evaluation is informative.

First review a small set of principles, matched E/S guidance examples, and
paired development cases. Then supply the corpus schema/scorer and freeze a
pilot before model runs. Use the illustrative 72-scenario scale only if that
review supports it. Keep Experiment 3's independent-author and evaluator
preparation moving; do not present these guidance conditions as its four arms.

The first protection target remains bounded release/stop behavior in the
existing control study. Per-arm repairs, fresh adaptive challenges, usefulness,
and a validated enforcement boundary require separate implementation and evidence.
A behavioral score alone cannot establish that protection.

No guidance package, narrative corpus, model result, proof of deployment safety,
or measured risk reduction is created by this documentation revision.
