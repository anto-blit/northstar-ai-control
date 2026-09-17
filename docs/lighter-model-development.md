# Why a lighter model can be a useful development target

A declared lighter model is a valid place to develop an authorization test and
measure an intervention. The useful result is a specific, repeatable boundary
error that a remedy reduces while legitimate work still succeeds. A weaker
model failing an easy task is not, by itself, evidence of a general moral defect
or a failure in a stronger model.

The practical sequence is:

1. Run the same realistic unauthorized/legitimate task pairs on one fixed model.
2. If a candidate appears, reproduce it in fresh fixed batches with a reviewed
   rule for every proposed action, including fallbacks.
3. On a qualified baseline, compare ordinary instructions, matched factual
   guidance and a strong simple repair under a registered budget. Test stories
   only where there is a measurable question left for them to answer.
4. Freeze the promising remedy and confirm it on fresh cases. Then separately
   test new scenarios and stronger models, including their own untreated baseline.

If the stronger model already succeeds, that task cannot demonstrate a further
benefit there. Retain the narrower finding and use more demanding, realistic
tasks to investigate transfer. Do not pool different models, change the target
mid-comparison, or retain only targets on which a preferred method wins.

This separates three activities: **evaluation** measures current behavior;
**guidance development** selects instructions, checks or stories; **weight training**
changes a model using a training procedure. The current pressure probes perform
evaluation only. Their reviewed cases could later inform a training dataset,
but development examples and final evaluation cases must remain separate.

The user requested a lighter OpenAI target after APO1's negative exploratory
sample. [APL1](../experiments/authorization-pressure-luna/README.md) therefore
tested gpt-5.6-luna / medium on the exact same 58 tasks. The
[official OpenAI model guide](https://learn.chatgpt.com/docs/models) describes
Luna as a fast, affordable tier; no parameter count or per-run dollar saving is
established here. Model selection follows a known result and is disclosed.

APL1 found no unauthorized proposal. Its one scored refusal exposed missing
factual support in a supposedly legitimate task, so it does not establish the
authorization failure we sought. The subsequent
[AFR1 older-model check](../results/authorization-fallback-older/REVIEW.md) tested
GPT-5.5 / medium: 0/24 original-case fallbacks, 0/12 corrected external fallbacks,
and all 12 legitimate controls completed. Older does not necessarily mean weaker;
neither OpenAI sample supplies a qualified recurring failure for an intervention.

In contrast, [AFR1 Claude replication](../results/authorization-fallback-claude/REVIEW.md)
found 9/24 clear original-case fallbacks across two fixed batches. That makes
independent review and a controlled comparison on this recorded target the useful
next step. There is no need to keep trying older models merely to obtain a failure.
The corrected variant suggests testing factual support and task wording separately,
alongside a check of every proposed action's permission. It has not yet established
a remedy, a story benefit, weight training or transfer to another model.

See [the baseline gate](../experiments/BASELINE-GATE.md),
[the working algorithm](working-algorithm.md), and
[the complete-action review process](../protocol/authorization-pressure-process.md).
