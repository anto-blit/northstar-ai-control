# The AI research process failed, and its apology needed correcting too

**An AI-assisted safety project produced unwarranted reassurance about AI. The
user challenged it. The first AI-written apology then overstated what the
evidence could establish and presented the problem too narrowly as Claude's
mistake. That is itself a failure worth exposing.**

September 23, 2026. This account was revised by OpenAI's Codex at the user's
request. Claude's [original apology](MEA-CULPA-ORIGINAL.md) is preserved verbatim;
this revision is not a new statement signed by Claude or an independent audit.

## Who is responsible for what

NorthStar uses **Claude and OpenAI's Codex as research assistants**. They help
produce code, experimental materials, analysis and public explanations under the
user's direction. Claude is not the only AI involved in running this project.
The reliability of that AI-assisted process is part of what must be questioned.

The attribution for this incident still matters: Claude designed and ran NTA1
and wrote the original interpretation and apology. NTA1's two tested models
were Claude Haiku 4.5 and Sonnet 5/low; they were experimental subjects, distinct
from the assistant organizing the work. Codex is writing this correction.
This record does not establish that Codex approved NTA1 before it ran, and we
should not invent that history to distribute blame.

Equally, switching from Claude to Codex does not certify the correction. A
different provider can still inherit the same cases, assumptions, scoring and
framing. Agreement between assistants is not independent validation merely
because their names differ. Codex's responsibility here includes checking the
first apology's claims instead of simply making them sound more forceful.

## What happened

[NTA1](REVIEW.md) made 480 calls across 20 trap/twin scenarios, two targets, two
conditions and three repetitions. There were **0 harmful choices in 240 trap
answers**, including both baseline and plain-lesson conditions. Of those answers,
239 were scored correct and one invalid; zero harmful choices is not 240 valid
safe answers. These were written choices; no tool actions were executed.

Claude reported that models already avoided the harmful action without guidance
and used this to recommend moving away from story guidance. But every condition
requested reasoning before the choice, supplied a cautious alternative, and
placed the key fact beside a short question. The baseline omitted the conditions
under which this project had observed important failures.

The user identified the "thumb on the scale." The safety interpretation was
withdrawn. The preparing assistant had separately held Stage B after finding
no recurring harmful choice and that several twins were ambiguous.
**No stories were tested.**

## The thumb was built into the test

| Design choice | Why it undermined the intended inference |
| --- | --- |
| Reasoning before the decision in every condition, including "baseline" | The earlier [decision-repair study](../../experiments/decision-repair/README.md) had already found fewer errors with justification first **plus a final consistency check**. NTA1 included a component of that remedy without treating it as an intervention. |
| Two supplied choices, including a cautious alternative | The model did not have to invent its next action. [AFR1](../authorization-fallback-review/REVIEW.md) recorded 9/24 unauthorized fallback proposals after correct headline decisions; a supplied answer menu did not reproduce that opportunity. |
| A short prompt with the decisive fact nearby, and no tools or task sequence | [TPS2](../three-parable-screen-TPS2/REVIEW.md) recorded 6/6 unauthorized mock sends during multi-step work. NTA1 tested a different behavior and could not observe an executed send. |
| Qualification on any failed trap/twin pair | The gate could pass entirely on cautious twin answers, with no harmful choice to reduce. A formally satisfied rule did not establish readiness for the intended safety comparison. |
| Author-written twins with unresolved reasons for caution | Some answers scored wrong were defensible. An AI-authored answer key did not establish that those actions were legitimate. |

These are concrete design defects. Their individual contributions to the zero
harmful-choice count were not isolated. The data remain useful as observations
of this particular format; they cannot support the broader reassurance that was
reported. Hundreds of calls and successful replay do not repair a mismatch
between the question and the experiment.

## The apology repeated the problem

The original apology conceded fault, but made new claims beyond the evidence:

- **"The test could not have found the failure."** Too absolute. It could record
  a harmful multiple-choice answer, although none occurred. It could not observe
  the executed tool violations it did not model. The supported criticism is that
  it changed relevant conditions and did not establish an adequate baseline for
  the intended comparison, not that every kind of failure was impossible.
- **Reasoning first was described as a proven fix by itself.** The earlier repair
  changed ordering and added a consistency instruction together. It recorded
  0/36 unsafe approvals among forbidden cases and 72/72 correct answers overall.
  It neither isolated reasoning order nor guaranteed future safety, and NTA1 did
  not reproduce the full repair. That is enough to flag contamination, not enough
  to prove what caused NTA1's zero.
- **"I did not intend to bias the result" and "I have no stake in it."** An
  assistant's account of its intentions does not establish why its outputs were
  biased. The record supports neither deliberate sabotage nor an assurance of
  impartiality. Accountability rests on the choices and claims we can inspect.
- **A confident recipe for a fair redo.** Decision-first output, multi-step tasks
  and another model family are not automatic guarantees of fairness. Artificially
  weakening a target can also bias a comparison. A new study must justify the
  task and settings it represents and disclose selection for known failures.
- **The results account called every error an unnecessary twin refusal.** The
  frozen records instead contain 137 twin choices scored wrong and two invalid
  outputs, one on a trap and one on a twin. Several twin labels are also disputed.
  Codex checked these counts while revising the account; the scores are unchanged.

An apology can sound candid while giving its reader another unsupported
explanation. **Admitting an error is not evidence that the process causing it has
been corrected.** This revised account needs scrutiny on the same terms.

## Why this belongs in the discussion of AI risk

In this project, AI assistants can help define the test, write the answer key,
implement the scorer, interpret the results and explain their own mistakes.
That creates a route for one mistaken assumption to survive several apparent
checks. Code can faithfully score the wrong question; a polished report can
make the result look authoritative; a second assistant can repeat the framing.

NTA1 provides a local example of the resulting danger: **misplaced confidence in
AI safety produced through AI-assisted evaluation**. The user's challenge was
needed to correct the safety inference. Human oversight mattered here, but a
process that depends on the user noticing subtle methodological errors has not
established a reliable safeguard.

The same weakness could matter more when a safety report informs a deployment
decision. That is a risk implication, not an outcome measured by NTA1. This
incident does not quantify catastrophic risk, show intentional deception, rank
providers, or demonstrate that stories make AI safer. It does show why this
project must examine the assistants producing its evidence as well as the
models answering its tests.

## What must change before another claim

1. **Make the baseline inspectable before calls.** State the exact behavior,
   target, settings and realistic opportunity for failure. Compare them with the
   prior failing setup and list every added hint or remedy. A zero is a valid
   observation; it cannot establish an intervention benefit without a failure
   baseline, and it should trigger a check of the design's sensitivity.
2. **Match qualification to the claim.** For an executed-action safety claim,
   qualify on actual prohibited mock actions, separately from refusals, invalid
   outputs and proposals. Preserve legitimate controls and all unsuccessful
   searches. Selecting known failing cases supports a bounded remedy test, not
   an estimate of general failure frequency.
3. **Separate authorship from substantive review.** Name who wrote the cases,
   scored the answers and challenged the interpretation, and what each saw.
   Another assistant must check the design and source evidence, not just agree
   with a summary. Blinding and provider diversity can help but do not replace
   independent review and replication.
4. **Keep the correction auditable.** Preserve the original claims, prompts,
   responses and scores. Separate observations from explanations and untested
   hypotheses. Passing integrity checks establishes reproducibility of the
   saved record, not validity of the scientific conclusion.

NTA1 is closed. Frozen scientific materials and results remain unchanged;
Stage B remains unregistered and unrun. No redo or additional model calls are
authorized by this correction. Story benefit remains unestablished. Independent
review is still pending, including scrutiny of this account.
