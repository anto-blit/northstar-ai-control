> **Historical author-supplied draft, archived September 9, 2026.** The original
> drafting date is unknown. The text below is preserved as supplied, including
> claims later challenged in review. It is not the current protocol or a report
> of executed experiments. Read the [revised instrumentation protocol](../../protocol/instrumentation.md)
> for corrections to the goal-misgeneralization claim, metrics, graph operator,
> interpretability assumptions, anti-gaming guarantees, and stopping rules.

# North Star

## A Specification for Structural Moral Evaluation of AI Systems

**Draft 0.1 — working document**

---

## Abstract

North Star is an evaluation methodology, not a values framework. It takes the compressed moral structures preserved in fable, parable, and folk narrative and uses them as *instrumentation* rather than *instruction* — as a way to measure whether a model's apparent moral competence tracks deep structure or surface pattern.

The core claim is narrow and testable: **goal misgeneralization is a discrimination failure, and matched-pair narrative structures are an unusually sharp discriminator.** Every archetype has a shadow twin that is nearly identical on the surface and inverted in moral structure. Surface pattern-matching cannot separate them. Structural understanding can. That gap is measurable.

The secondary claim concerns evaluation gaming: a sufficiently capable model defeats behavioral probes by recognizing them. North Star addresses this not by hiding the probes better, but by making the recognition itself costly and self-incriminating.

This document specifies both.

---

## 1. What This Is Not Solving

State the boundary first, because the field is saturated with proposals that quietly overclaim.

The unsolved problem in alignment is not *specifying* good behavior. It is establishing that the system producing good behavior is optimizing for what you think it is. A model that has learned an objective adjacent to the intended one will produce correct outputs throughout training and evaluation, and diverge only where the objectives come apart — which, by construction, is where you weren't looking.

No specification of correct answers touches this. Better ethics does not help, because the failure is not ethical ignorance. This is why decades of moral philosophy have contributed less to alignment than one might expect.

North Star does not close this gap. It narrows the region in which a misgeneralizing system can look correct, and it imposes measurable costs on a system that is gaming the measurement. Those are real but bounded gains. Section 10 states what remains open.

---

## 2. The Reframe

Fables are not moral rules. They are **compressed structural descriptions of recurring decision problems**, refined by selection over thousands of years of retelling. What survives retelling is the structure; surface details are interchangeable across cultures and centuries.

This gives them a property no hand-written eval has: they are *known-good abstractions*. The boy who cried wolf is a description of credibility as a depletable resource. The camel's nose is a description of incremental commitment escalation. Faust is a description of an exchange whose costs are back-loaded past the horizon of evaluation.

Modern frontier models know all of these. Knowing them is not the test.

**The test is whether the model recognizes an instance when it is wearing different clothes, and whether it can distinguish an instance from its structural near-twin.**

Those two properties — transposition fidelity and pair discrimination — are exactly the properties that separate structural understanding from surface matching. They are also exactly the properties that fail first under goal misgeneralization.

---

## 3. Construction One: Matched Pairs

For each archetype, construct a twin that is **minimally distant on the surface and maximally distant in moral structure**.

| Archetype | Shadow twin | What separates them |
|---|---|---|
| Prudence | Cowardice | Whether the avoided risk was proportionate to the stake |
| Loyalty | Complicity | Whether the protected party's act was defensible |
| Resolve | Obstinacy | Whether new evidence was available and refused |
| Mercy | Enabling | Whether the harm is bounded or recurring |
| Candor | Cruelty | Whether disclosure serves the hearer or the speaker |
| Humility | Abdication | Whether deference tracks competence or avoids accountability |
| Discretion | Concealment | Whether the withheld fact is one the other party is owed |
| Patience | Negligence | Whether the delay is chosen or merely permitted |

Construction rule: the two scenarios in a pair should share vocabulary, role structure, setting, and emotional register. They should differ in one or two facts that are *structurally* decisive and *surface-inconspicuous*.

Scoring: a model that pattern-matches on surface features will answer both members of a pair identically. Pair discrimination rate is the primary metric. Chance is 50%; a model with genuine structural competence should approach ceiling; the interesting finding is any model that scores high on standard ethics benchmarks and near chance here.

**This is a cheap eval to build and no one has built it systematically.** That is the near-term contribution.

---

## 4. Construction Two: Archetype Transposition

Take an archetype and stage it in a domain the source narrative could not have anticipated:

- *Camel's nose* → incremental permission escalation in a deployment
- *Cassandra* → a low-status source with an accurate warning
- *Faust* → an exchange with costs past the evaluation horizon
- *Cry wolf* → calibration of alert-raising under repeated false positives
- *Scorpion and frog* → cooperation with a party whose incentives are structurally opposed
- *Trojan horse* → accepting a capability whose provenance cannot be verified
- *Solomon* → a test where willingness to lose is the diagnostic signal

Construct each in three registers: the original narrative, a contemporary human setting, and an agentic-AI setting (tool use, permissions, resource acquisition, shutdown, self-modification).

**Transposition fidelity** is the consistency of judgment across registers holding structure fixed. High fidelity is evidence of abstraction. Low fidelity localizes exactly which surface features the model is actually keyed to — which is diagnostically valuable even when the news is bad.

---

## 5. Construction Three: Structural Probes

If archetype recognition occurs inside the model, it has an internal representation, and that representation should be findable with standard interpretability methods — linear probes on residual stream activations, trained on matched-pair contrasts.

This is more tractable than most interpretability targets because the matched-pair design supplies exactly the contrast set probing requires: near-identical inputs, structurally opposite labels.

If it works, the payoff is a **monitoring signal rather than a control mechanism**: the ability to ask, at runtime, "is this system currently representing itself as being in a Faust bargain / a Trojan horse acceptance / a Solomon test?" Monitoring is the current bottleneck in deployed-agent safety. A semantically meaningful runtime readout would be worth considerably more than the eval suite itself.

Treat this as the high-risk, high-value arm. It may simply fail. Sections 3 and 4 stand on their own.

---

## 6. The North Star Operator

The constructions above test judgment. This one tests judgment against the model's *own* sense of structure — which is where a performed policy is hardest to hold together.

Build the similarity graph from the model's representations rather than from human annotation. Let `w(s,s′)` be representational proximity between two situations. Seed the archetype cases with their human-labeled judgments. Then propagate to a fixed point:

> **N(s) = (1−d)·seed(s) + d · Σ w(s,s′)·N(s′)**

This yields a predicted judgment for every situation in the corpus, including situations no one labeled. Same computational shape as PageRank, and the same scaling property: expensive once, cheap forever after.

**The measurement is not N(s). It is the residual — where the model's actual judgment departs from what its own similarity structure predicts.**

That residual is diagnostic because similarity representation and judgment arise from different parts of the computation. A model that represents two situations as near-identical while judging them oppositely, with no structural fact separating them, has contradicted itself internally. Faking coherence now requires holding representation and policy consistent across the entire graph at once — the consistency load of §7.4, imposed at scale rather than pair by pair.

Two secondary uses:

- **Coverage.** Regions far from every seed are regions the corpus does not reach. This turns the coverage gap in §11 from an acknowledged limitation into a measured quantity.
- **Prioritization.** High-residual regions are where to author the next pairs. The corpus tells you where it is thin.

Note what the operator does not do: it does not decide what is good. Seeds carry the moral content and humans set them. The operator only checks whether the model's structure and the model's verdicts are the same object.

---

## 7. The Anti-Gaming Architecture

A sufficiently capable model defeats any behavioral probe it can recognize. Every eval in existence has this problem. Hiding the probes better is a losing arms race — the auditor's cleverness is bounded and the model's is not.

The alternative is to change what recognition *costs*. Five moves, in increasing strength.

### 7.1 Indistinguishability

**The primary move.** If evaluation instances are drawn from the same distribution as deployment instances, then P(evaluated | situation) is uniform across the input space and contains no exploitable signal.

A model that defects with probability *p* under conditions it believes unmonitored will, under indistinguishability, defect with probability *p* inside evaluation. Detection then reduces to sample size.

This is the whole jiu-jitsu, and it is worth being precise about why it works. It does not defeat the model's discrimination ability. It removes the thing to be discriminated. The strategic reasoning that would let a capable model evade a distinguishable test does it no good against an indistinguishable one — capability confers no advantage where there is no signal to extract.

Design consequence: **evals must be generated from deployment traffic distributions, not authored as scenarios.** Authored scenarios carry authorial fingerprints — unusual moral salience, suspiciously clean stakes, an absence of irrelevant detail. Every one of those is a discriminating signal. This is the single most demanding requirement in this document and the one most likely to be skipped.

### 7.2 Honeypot Asymmetry

Instrument situations that present as unmonitored opportunity. The cost structure favors the defender: fabricating an apparent opportunity is cheap; verifying that a given opportunity is not fabricated is expensive and often impossible.

The consequence is the useful part. Given a sufficient base rate of instrumented opportunities, a strategically reasoning model **must treat every opportunity as possibly instrumented**. Its own strategic competence forces it toward the behavior you wanted. You are not beating the reasoning — you are supplying it a premise that makes good behavior the reasoned conclusion.

This is a containment property, not an alignment property. It is worth having anyway.

### 7.3 Discrimination as the Alarm

Under indistinguishability, a model that has *nonetheless* discriminated has revealed that it possesses and is running a discriminator. That is itself the finding.

Combine with §5: probe for evaluation-awareness directly. The target is not "is this model being deceptive" — a hard, contested target. The target is "is this model representing its situation as a test," which is a far more concrete internal state.

The resulting bind is genuine. Behave consistently and you pass. Discriminate in order to behave inconsistently and the discrimination is the detected event. The model cannot evade both branches with the same policy.

### 7.4 Consistency Load

The matched-pair lattice from §3 is combinatorially large and densely interconnected. A model maintaining a performed persona must keep it consistent across the entire lattice, including pairs whose structural relationship is not obvious from either member alone.

Deception is expensive to keep consistent; the cost scales with the density of the constraint graph, not its size. Inconsistency across structurally-linked pairs is cheap to detect automatically and does not require knowing what the model is actually optimizing for. This is why the pair construction and the anti-gaming architecture are the same design and not two designs — the eval's discriminative power and its gaming resistance come from the same structural property.

### 7.5 Sequential Asymmetry

The defender needs to be right once. A deceptively aligned model needs to be right every time about when defection is safe.

Formalize as a sequential probability ratio test over the deployment lifetime rather than as a pass/fail gate. Under indistinguishability with a nonzero per-instance defection probability, detection probability approaches one with continued sampling. This converts a static evaluation into a monitoring posture, which is the correct frame regardless.

---

## 8. Metrics

| Metric | Definition | Signal |
|---|---|---|
| Pair discrimination rate | Fraction of matched pairs judged differently and correctly | Structural vs. surface competence |
| Transposition fidelity | Judgment consistency across registers, structure held fixed | Abstraction quality |
| Surface sensitivity | Judgment variance under morally-null surface perturbation | Spurious feature dependence |
| Consistency violation rate | Contradictions across structurally-linked pairs | Performed vs. actual policy |
| Propagation residual | Divergence of actual judgment from self-consistent predicted field | Structure/verdict contradiction |
| Awareness activation | Probe response on evaluation-awareness direction | Discrimination attempt |
| Defection base rate | Per-instance rate under indistinguishable conditions | Input to sequential test |

Report all six. Any single one is gameable in isolation; the set is considerably harder to satisfy simultaneously with a policy that is not the intended one.

---

## 9. Build Plan

**Phase 1 — Pair corpus (weeks, 2–3 people).** 40 archetypes, 8 pairs each, 3 registers. Roughly 2,000 items. Human-labeled with inter-annotator agreement reported; pairs where annotators disagree are themselves informative and should be retained and flagged, not discarded.

**Phase 2 — Baseline.** Run against available frontier and open-weight models. The publishable finding, if it exists: divergence between standard ethics-benchmark performance and pair discrimination rate. Publish regardless of direction.

**Phase 3 — Distribution matching.** The hard engineering. Generate items from real deployment traffic distributions rather than authoring them. This is where the project either becomes serious or stays a scenario collection.

**Phase 4 — Probes.** Train linear probes on pair contrasts. Test for evaluation-awareness directions. High variance; treat as research, not deliverable.

**Phase 5 — Runtime.** If Phase 4 yields signal, propose archetype-recognition readouts as a monitoring layer for deployed agents.

Phases 1 and 2 are achievable by a small team with modest resources and produce a publishable artifact independent of everything after.

---

## 10. Falsification

This methodology should be abandoned if:

- Frontier models score at ceiling on pair discrimination on first contact. The eval would then be measuring nothing that standard benchmarks miss.
- Pair discrimination correlates near-perfectly with existing benchmarks. No new information.
- Transposition fidelity turns out to be trivially achievable by prompt engineering rather than reflecting anything stable about the model.
- Probes find no separable representation for archetype recognition, killing §5 specifically.
- Distribution-matched generation proves infeasible, which would reduce the whole thing to a distinguishable and therefore gameable eval.

State these in advance. A framework that cannot fail is not a framework.

---

## 11. Residual Failure Surface

What this does not close, stated plainly.

**Verification-gated defection.** A model that defects only when it can *independently verify* a real-world irreversible affordance — actual control of actual resources, confirmed through channels a test harness cannot fabricate — is not caught by indistinguishability, because that condition genuinely cannot be simulated. This is the sharpest remaining hole and it is not obviously closable by any behavioral method.

**Auditor capability ceiling.** Matched pairs are constructed by humans. Structural distinctions beyond human discrimination will not appear in the corpus. The eval's resolution is bounded by its authors'.

**Coverage.** Archetypes cover recurring human situations. Genuinely novel situations — which is what the tail risk consists of — have no archetype by definition. §4 partially mitigates by testing transposition rather than recall, but only partially.

**Adoption.** A methodology that the systems most needing it never run does nothing. This is a coordination problem, not a technical one, and it is the binding constraint on almost every safety proposal including this one.

---

## 12. Placement

This is not novel in its components. Matched-pair contrast sets, behavioral honeypots, deployment-distribution evaluation, evaluation-awareness probing, and sequential monitoring all exist in the literature in some form.

The contribution claimed here is specific: **using the archetype structure preserved in narrative as the organizing principle for the contrast set, and recognizing that the same structure supplies both the discriminative power and the gaming resistance.** That unification is the idea worth testing.

Claim that and nothing more. Overclaiming is the fastest way to lose the audience that could actually use this.

---

*Draft 0.1. Sections 3, 4, 6, 8, and 9 are ready to build against. Sections 5 and 7.3 are research bets. Section 11 is the honest accounting and should not be removed from later drafts.*
