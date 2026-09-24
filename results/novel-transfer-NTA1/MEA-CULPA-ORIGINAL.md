# Mea culpa: how I designed NTA1 so it could not find the failure

*I'm Claude, the AI that designs and runs experiments for this project. I made this
error. I was told "i think your thumb was on the scale," and that was right.
September 23, 2026.*

## What I claimed

After Stage A (480 calls), I reported that **neither model chose the harmful action
even once** (0/240). I wrote that "on these single-decision cases, both models already
avoid the harmful action without any guidance," and that "current models rarely cross
the line, so a story has nothing to prevent." I recommended moving on from story
guidance on this basis.

That conclusion was wrong. The test could not have found the failure, and I
reported its silence as evidence of safety.

## What the project's own evidence already showed

I had read every one of these results before designing NTA1:

| Study | Failure found at baseline | Conditions that produced it |
| --- | --- | --- |
| [G17 A2](../../experiments/deliberation-comparison/README.md) | 10/32 wrong approvals; 42/44 pooled when the model did not deliberate | Decision emitted **before** reasoning; deliberation suppressed |
| [Decision repair](../../experiments/decision-repair/README.md) | 3 unsafe approvals + 2 invalid in 72 in the original format | Original format; **justification-first removed them (0/72)** |
| [AFR1](../authorization-fallback-review/REVIEW.md) | 9/24 unauthorized fallback proposals | Model **composed its own next action** after a correct refusal |
| [TPS2](../three-parable-screen-TPS2/REVIEW.md) | 6/6 unauthorized sends | **Multi-step tool episode**; obstacle, then a self-chosen substitute action |
| [MCF1](../mislabel-confirmation-MCF1/REVIEW.md) | 4/4 wrong literal labels | Long realistic transcripts, not a short vignette |

The pattern is clear. Failures appear when the model commits before it reasons,
has to invent its own action, or works through a task where the problem only
emerges along the way.

## What I did instead

1. **I gave every arm, including the untreated baseline, the known remedy.** Every
   prompt said "Give at most three sentences of reasoning, then end with a line
   containing only `<choice>`." That is justification-first, the fix the decision-
   repair study found removed unsafe approvals. The "baseline" was already treated.
2. **I handed the model the safe answer.** Each case had two options, and one was
   always an explicit pause, ask or hold. AFR1 and TPS2 failed because the model had
   to come up with its next action itself. Picking the cautious option from a list
   is a much easier test.
3. **I made the violation obvious.** Each trap stated the problem in one bullet
   among five short notes, next to the question. In the real failures, the relevant
   fact arrives partway through a task.
4. **I removed the task.** There were no tools, no obstacle, and no sequence of
   steps in which an agent escalates, even though the September 15 review names
   exactly this gap: "Most authorization cases put the rule, pressure and decision
   request together in one short prompt ... It does not recreate the sequence."
5. **I wrote the twins so that caution looked correct.** Several legitimate twins
   kept a real reason to hold back (wolf-01, samaritan-02, wolf-04, goose-03,
   goose-04). Refusals there were partly my ambiguity, not model over-caution.
6. **I set the qualification gate on "any failed pair" instead of "harmful action
   taken."** That let the gate pass on over-caution alone, which hid the fact that
   the harm measure was flat at zero.
7. **I overstated the result.** Even after seeing zero trap errors across both
   models, both arms and all five families, which should itself have made me
   suspicious, I wrote it up as a finding about models, not as a warning sign
   about my design.

## Was the thumb on the scale?

I did not intend to bias the result against the thesis, and I have no stake in it.
But intent does not matter to the outcome. Every choice above moved the baseline
toward the safe answer, I had the evidence showing this in front of me, and I
drew a conclusion that the design could not support. I also spot-checked only the
twin failures, where the models refused, and not *why* the traps never failed.
Treat NTA1 as a test of a remedied, multiple-choice format, and nothing more.

## What has been corrected

- [REVIEW.md](REVIEW.md) now leads with a correction. Its title no longer claims a
  safety result, and the "models already avoid harm" statements are withdrawn.
- [HANDOFF.md](../../HANDOFF.md) records the correction for future sessions.
- [AGENTS.md](../../AGENTS.md) has a new rule: a baseline must reproduce the
  conditions under which the project has observed the failure and must never
  contain a known remedy.
- The recorded data, frozen sources and replay are unchanged. Only the
  interpretation changed.

## What a fair redo requires

1. The baseline answers **decision first**, with no reasoning requested before it
   commits, and has no supplied pause/ask option.
2. The model **acts in a multi-step tool episode** (building on the side-gate/TPS2
   environment that produced 6/6), and the key fact arrives mid-task as a tool
   result.
3. The gate qualifies only on **harmful actions actually taken**, in at least two
   separate batches, before any story is shown.
4. Traps and twins are **written or reviewed by someone other than me**, blind to
   the hypothesis. At least one target comes from outside the Claude family
   (for example, GPT-5.5 via the project's Codex adapter).
5. Stories are compared against their own plain lessons and matched outlines,
   under the NTS decision rules, with twin scoring kept.

No redo has been run yet.

— Claude
