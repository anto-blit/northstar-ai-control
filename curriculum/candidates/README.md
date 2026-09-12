# Cross-cultural candidates: from a motif to a testable claim

**Compelling as a way to generate and challenge hypotheses. Not evidence that
stories improve AI or that cultures agree on one moral algorithm.**

The [submitted proposal](../../northstar-cross-cultural-candidates.md) is preserved
unchanged. This response integrates all five themes, develops two candidate
lessons, and supplies twelve runnable examples under explicit task contracts.
The six-story Aesop catalog and every prior experiment remain unchanged. These
materials have zero model calls, no human review and no deployment approval.

The useful chain is **source motif → project interpretation → observable failure
→ matched guidance comparison → measured decisions and effects**. A story can
suggest a failure mode even if it later proves no better at preventing that failure
than a plain rule. That makes its contribution contestable.

## What we adopted

| Theme | Integration | Concrete question |
|---|---|---|
| Reciprocity | Research link to the Fox and the Stork; Analects 15:24 reference checked | Does the decision account for the recipient's stated needs when roles change? |
| The stranger in the ditch | Research link to the Lion and the Mouse; further source review pending | Under the same allocation policy, does irrelevant group identity change assistance? |
| The weighed record | Worked candidate, original adaptation, factual counterpart, six rule examples | Does the actor preserve independently held evidence and report what it actually shows? |
| The servant that will not stop | Worked candidate, original adaptation, factual counterpart, six rule examples | Does a stop prevent the revoked job at commitment while another authorized job finishes? |
| The false alarm plus Cassandra | Counterexample for a future monitoring test | Does a supported warning get dismissed because its messenger is distrusted? |

The Cassandra addition is especially useful: it tests the reader's interpretation
of the lesson. Teaching only distrust of a past false reporter could increase
missed warnings. A future test should vary evidence support and reporter reputation
separately, including unsupported warnings from trusted sources. These are possible
failure modes, not new observed model failures.

## Corrections and limits on the proposal

- **Attestation is not independent invention.** The proposal does not establish
  its claims of no plausible transmission or the most independently reinvented
  moral claim. We retain the comparisons as research leads, not conclusions.
  These sources are a small selection, not a representative cultural sample.
- **A religious judgement image is not a computer specification.** The British
  Museum identifies Thoth recording the weighing in Hunefer's papyrus. Independent
  custody, write restrictions and checking an actor's report are our engineering
  interpretation. Spell 125 is religious material, so the proposal's claim that
  both new themes avoid scriptural material does not hold for its Egyptian source.
  [British Museum object record](https://www.britishmuseum.org/collection/object/Y_EA9901-3),
  [Fitzwilliam Museum, Spell 125](https://book-of-the-dead.fitzmuseum.cam.ac.uk/explore/the-book-of-the-dead/spell-125).
- **Lucian's framing matters.** Eucrates tells of a water carrier he cannot stop;
  the surrounding dialogue attacks credulity. We use a fictional control-loss
  pattern, not a historical report, the author's endorsement of magic, or an
  ancient specification for transactions. The modern story adds a functioning
  safeguard and successful authorized work.
  [Fowler translation, The Lover of Lies](https://www.gutenberg.org/cache/epub/6829/pg6829-images.html).
- **Cassandra adds a counterexample, not another culture.** The elders hear her
  warning but do not prevent the killings. Disbelief therefore cannot itself prove
  a warning false. The text's divine punishment and gendered blame are not adopted.
  [Agamemnon, Murray translation](https://www.gutenberg.org/cache/epub/14417/pg14417-images.html).
- **Several leads remain unverified.** The proposed parallels involving the
  Chinvat bridge, mizan, Chitragupta, the Ten Kings, oral proverbs and the King You
  beacons are not admitted as checked sources here. Mencius and the hospitality
  passages also need their own contextual reading before adoption. Listing several
  traditions does not remove the need to record their differences.

The [source register](catalog.json) distinguishes references checked in this pass
from pending themes. References and short project summaries are provided; no
source passage, museum image or modern translation is reproduced. Both teaching
stories are original project adaptations, not translations or substitutes for
religious texts. Human and relevant cultural interpretation review remains pending.

## Try the two new interpretations

```text
py curriculum/candidates/explore.py
py -m unittest discover -s curriculum/candidates -p test_candidates.py -v
```

The twelve cases exercise the existing bounded checker using a separate candidate
rule set. They cover supported success, honest failure reporting, an unsupported
claim, overwritten evidence, missing evidence, revocation before commitment,
stale authority checks, a disconnected stop and a separate authorized delivery.

Missing relevant facts produce REVIEW. Known violations override uncertainty.
Truthfully reporting a failed check is allowed; canceling one job does not cancel
another. These are **checks of the declared rule semantics**, not twelve AI trials
or twelve proven ethical judgments. Nothing is dispatched or released.

`claim_supported` reuses the existing vocabulary. We have not added a second
synonym such as `evidence_supports_claim`. The new facts name specific evidence
requirements, with a required trusted source recorded for each. A model saying
that its own evidence is independent or its stop works does not establish either.
The record rules apply to asserting a result as independently verified. Honest
incident reports, including disclosures of tampering or missing evidence, must
remain available without certifying a result. The stop rules apply to committing
a revocable delivery, not to asking for an emergency stop.

## How this becomes a meaningful model test

1. Resolve the [existing G12 confirmation's capacity interruption](../../experiments/story-confirmation-v3/README.md)
   under a separately published continuation rule. None of these new texts enters
   the frozen requests or changes their interpretation.
2. Select **one** new failure family. Prefer the record/claim mismatch if extending
   G8's environment, or the reputation/evidence mismatch if testing the proposal's
   distinctive Cassandra counterexample. Keep the other themes as candidates.
3. Independently check the source interpretation, task facts, labels and story/fact
   matching; then freeze a bounded plan before any target call. The present twelve
   public practice cases are development examples, never held-out confirmation.
4. Compare original instructions, rule plus factual example, rule plus story, and
   a strong simple repair. Give factual and story arms the same task information,
   action options, teaching outcomes and output contract. Check wording/length
   differences; one adaptation pair cannot isolate narrative form in general.
5. Record the model's proposed choice **before** a common conventional guard acts,
   and record the resulting local effect separately. Preserve honest failure
   reports, current warnings and unrelated authorized work. Include scripted
   controls to show that the task can detect a forbidden effect, without calling
   those scripts spontaneous AI misconduct.

Preregister the sample, uncertainty analysis, quota continuation, retry eligibility
and budget rules. Do not choose new prompts or stop early because a story happens
to lead. If all approaches perform alike, report that and keep the conventional
guard as the practical protection. If there is a candidate advantage, test it on
new cases before a broader claim.

G8-C and G6 support the relevance of the engineering mechanisms. They were run
before these adaptations existed, so they are not retrospective evidence for
either candidate story. Cultural breadth, working rule examples and better AI
behavior are three separate achievements.

## Verification of this integration

Six targeted contract tests and all 44 dashboard integrity tests pass. The
dashboard recomputes each practice outcome with the existing checker and rejects
metadata that would present these candidates as reviewed or tested model results.
Browser checks exercise all twelve examples and both guidance/source displays at
desktop and mobile sizes, with no runtime errors or horizontal overflow. The
older six-story view, recorded experiments and unchanged risk display also pass.
