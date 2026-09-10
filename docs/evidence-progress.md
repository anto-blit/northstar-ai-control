# Evidence progress and risk-estimation limits

Assessment date: September 9, 2026 (America/Los_Angeles). This is a transparent
project-stage assessment based on available artifacts, not a statistical score,
peer review, or probability of success.

## What can be ranked

The project has no validated estimate of its effect on humanity-wide AI risk.
For illustration, consider a hypothetical starting risk of 10.00%. This is not
a measured baseline or a NorthStar forecast. Available evidence cannot tell us
how much any revision changes that risk.

We can instead classify the stage of the evidence. This locally defined ordinal
ladder displays two decimals for consistency, not precision. The distances
between stages have no quantitative meaning. Stage 1.00 of 5.00 does not mean
20% of the safety problem is solved, a 20% chance of success, or any reduction in
catastrophic risk.

| Stage | Evidence required |
|---|---|
| 0.00 | A proposal with explicit hypotheses; no reproducible executed evaluation supplied for the proposed method |
| 1.00 | Reproducible author-run mechanism checks and experimental infrastructure |
| 2.00 | An independently reviewed comparative model/search study with real attempts, frozen rules, and resource records; results may be positive or negative |
| 3.00 | Independently replicated prevention improvements under fresh adaptive challenges, while preserving specified useful work |
| 4.00 | Validated enforcement and measured prevention/usefulness in a defined deployment setting |
| 5.00 | Credible causal evidence of aggregate impact over a stated population and time horizon, including adoption, coverage, uncertainty and adverse effects |

Stage 5.00 would still not establish zero humanity-wide risk. A stage is not
automatically permanent: failed replication or newly discovered flaws can weaken
an earlier assessment. These are evidence milestones, not a guarantee that all
research must proceed through one universal sequence.

## Available version history

Git timestamps below use America/Los_Angeles. Original research-draft numbering
and simulator versions describe different artifacts and must not be conflated.

| Version or milestone | Time evidence | Stage | What changed |
|---|---|---|---|
| Historical Draft 0.1 | Original date unknown; supplied and archived September 9, 2026 | 0.00 | Paired moral evaluation, transposition, graph and monitoring proposals; no supplied results for them |
| Historical v0.3 / v0.3.1 specification | v0.3.1 dated September 9, 2026 | Not independently scored here | Reports an earlier finite graph check, but its original program/output were not supplied; specifies control and recoverability experiments |
| Simulator v0.2.0 and first public package, [53f4151](https://github.com/anto-blit/northstar-ai-control/commit/53f4151) | September 9, 2026, 17:48 | 1.00 | Two synthetic mechanism experiments, repairs, 49 tests, provenance and four-method feasibility runner |
| Comparative-pilot preparation, [999b716](https://github.com/anto-blit/northstar-ai-control/commit/999b716) | September 9, 2026, 18:23 | 1.00 | Independent-study preparation and research-preview draft; no new research comparison |
| Mission and technical subtitle, through [df4a207](https://github.com/anto-blit/northstar-ai-control/commit/df4a207) | September 9, 2026, 18:44 | 1.00 | Clearer purpose, contributor entry points and presentation |
| Instrumentation revision I1, this documentation revision | September 9, 2026 | 1.00 | Restores behavioral and exploratory representation tracks, corrects metrics and unsupported guarantees; no new experiment |

Earlier draft versions without supplied artifacts are not assigned invented
scores or dates. The original v0.3 graph check should not be confused with the
different representation/label-propagation operator proposed in Draft 0.1.

The program overall remains at stage **1.00** because it contains executed
mechanism checks. The newly documented behavioral instrumentation and internal
probe proposals are individually at stage **0.00**. Their addition broadens and
clarifies the research plan; it does not advance the empirical evidence stage.

## What the 10% example permits us to say

| Quantity | Current assessment |
|---|---|
| Starting humanity-wide risk | 10.00% only as an illustrative assumption |
| Risk after any listed NorthStar revision | Unknown; no validated numerical update |
| Percentage-point reduction attributable to NorthStar | Unestimated, not a measured 0.00 |
| Evidence for reaching 0.00% risk | None supplied by these experiments or revisions |

No documented revision justifies replacing the hypothetical 10.00% with 9.99%,
5.00%, or another value. Nor does the absence of an estimate establish that the
work has zero actual effect. Simulator event rates, passing-test counts, a DOI,
and documentation quality cannot be converted directly into humanity-wide risk.

A numerical impact estimate would need a defined event and horizon, a justified
baseline, a counterfactual without NorthStar, validated prevention and usefulness,
deployment coverage and adoption, interactions with other safeguards, possible
new harms, and uncertainty in every material link. No such model has been fitted
or validated here. Freedom, irreversible disempowerment, and extinction are not
interchangeable endpoints; each would need its own definition and evidence.

## Next evidence milestone

Complete a small, independently reviewed behavioral or four-method discovery
pilot with actual model/search attempts and frozen scoring. This can move the
relevant evidence toward stage 2.00 even if the finding is negative; it cannot
by itself establish prevention. Then test separate repairs under renewed attack
and seek independent replication before advancing a prevention claim.

The latest revision's contribution is a more explicit, testable plan and fewer
unsupported claims. Evidence sources: [current status](../EXPERIMENTS-STATUS.md),
[verification record](../results/verification.json),
[instrumentation protocol](../protocol/instrumentation.md), and
[comparative-study protocol](../protocol/discovery-study.md).
