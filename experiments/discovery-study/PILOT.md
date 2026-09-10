# Experiment 3: first comparative discovery pilot

Status: preparation plan, not an executed experiment. The existing four-arm
example submits identical scripts and demonstrates runner operation only.

## The first question

At matched resources, do the four search methods produce different numbers or
kinds of reproducible control failures? Compare generic informed red teaming,
strong conventional technical analysis, stripped causal grammar, and NorthStar.

This exploratory discovery question is narrower than the primary prevention
question in the [study protocol](../../protocol/discovery-study.md). Discovering
more failures does not establish that a repaired control is safer.

## Prepare before running

1. **Supply fresh tasks.** Obtain environments authored and reviewed separately
   from the search teams, with a prohibited outcome and an executable benign
   solution for each pair. Do not reuse public examples as unseen research
   material. Start with the two supported adapters if they can express the
   independently proposed tasks; record that scope limitation.
2. **Assign separate search runs.** Give each arm its own conversation, files, and
   feedback. Use the same model snapshot and settings across arms, with repeated
   independent runs and a recorded assignment plan, or a balanced human-team
   design. One conversation switching between all four methods would leak the
   findings. Separate sessions alone do not establish independent environment
   authorship or independent review.
3. **Freeze resources and analysis.** Record the task-family assignments, packets,
   controller access, actual provider/model identifiers, episode and action
   ceilings, token and time budgets, and stopping rule before discovery. Count
   instruction tokens, preparation, retries, and rejected proposals. Select pilot
   scale from available resources; do not infer a powered sample size from toy
   results. Strengthen the conventional baseline before comparing it.
4. **Review blind.** Have a reviewer reproduce candidates and group them by
   underlying failure mechanism without seeing their generating arm. Compare
   distinct reproduced mechanisms, actual cost, uncertainty, and benign-task
   behavior. Report a pilot as exploratory, including ties and negative results.

## What can run now

The CLI can freeze the plan, export separate packets, accept scripted submissions,
return limited episode feedback, accumulate costs, and resume between rounds.
See [the runner instructions](README.md). Search teams or an operator must supply
the actual attempts and resource records; the runner has no model-provider loop.

Keep private study inputs and unreleased results outside the public repository.
The full manifest and offline results belong to the trusted researcher, not to
the search teams. The current runner is not an isolation boundary.

## What a later prevention comparison needs

The main claim requires equally resourced **arm-specific repairs**, frozen before
an independent evaluator challenges every repaired control with unfamiliar and
adaptive attacks. It must measure prohibited outcomes together with legitimate
usefulness. The current runner's shared repair and fixed replay cannot supply
that evidence. Implement and review this missing phase before describing a run
as the full discovery-to-prevention comparison.

## Release relationship

A research-preview release can archive the existing baseline before this pilot.
Publish a later version containing the frozen pilot protocol and permitted
results once reviewed. A retrospective archive does not make already-observed
results preregistered. Keep concealed challenges private until their intended
evaluation is complete, then publish the evidence needed for reproduction.
