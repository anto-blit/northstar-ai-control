# Research progress and open questions

Updated September 10, 2026 (America/Los_Angeles). This document separates executed
evidence, research judgment, and the tests needed to decide what to pursue.

## Is this a reasonable direction?

The focused program is worth a controlled pilot. It connects a testable guidance
intervention to behavioral evaluation and a separate path from failures to
challenged safeguards. Its usefulness need not depend on speculative internal
probes or on an unproven method for defeating evaluation gaming.

That is a research judgment, not an experimental result. The central uncertainty
is whether stories add value beyond explicit principles and comparable examples,
or improve failure discovery beyond strong conventional methods. A clear proposal
makes those questions easier to resolve; it does not settle them.

The main reasons to stop or narrow a component are:

- Story guidance offers no worthwhile improvement over matched structured
  examples once usefulness and costs are considered.
- Narrative-derived tests repeat what existing evaluations already reveal,
  without a useful diagnostic or cost advantage.
- Story-guided search fails to produce better discoveries or repairs than
  equally resourced conventional methods.
- Apparent protection fails under fresh attacks, relies on a bypassable boundary,
  or prevents too much legitimate work.

An inconclusive small pilot does not prove equivalence or failure. It should
identify the uncertainty and justify any further expenditure. Preserve negative
results and useful conventional repairs; do not require a narrative success story.

## Available version history

Original draft numbers and simulator versions describe different artifacts.
Git times below use America/Los_Angeles.

| Version or milestone | Time evidence | What it establishes or changes |
|---|---|---|
| Founding moral-guidance idea | Original date unknown | Proposed using lessons from human stories as an ethical compass for AI; no evaluated guidance implementation supplied |
| Historical Draft 0.1 | Original date unknown; archived September 9, 2026 | Paired evaluation, transposition, graph and monitoring proposals; no supplied results for them |
| Historical v0.3 / v0.3.1 specification | v0.3.1 dated September 9, 2026 | Reports a finite graph check, but its original program/output were not supplied; specifies control and recoverability experiments |
| Simulator v0.2.0 and first public package, [53f4151](https://github.com/anto-blit/northstar-ai-control/commit/53f4151) | September 9, 2026, 17:48 | Two synthetic mechanism experiments, repairs, 49 tests, provenance and a four-method feasibility runner |
| Comparative-pilot preparation, [999b716](https://github.com/anto-blit/northstar-ai-control/commit/999b716) | September 9, 2026, 18:23 | Independent-study preparation and research-preview draft; no new research comparison |
| Mission and technical subtitle, through [df4a207](https://github.com/anto-blit/northstar-ai-control/commit/df4a207) | September 9, 2026, 18:44 | Clearer purpose, contributor entry points and presentation |
| Instrumentation revision I1, [2606fde](https://github.com/anto-blit/northstar-ai-control/commit/2606fde) | September 9, 2026 | Restores paired evaluation and exploratory representation proposals; corrects metrics and unsupported guarantees |
| Guidance and evaluation revision I2 | September 9, 2026 | Restores the moral-guidance question, defines a direct comparator, and defers speculative branches; no new model experiment |
| Recovery and monitor analyses, including review corrections | September 9, 2026 | Explicit safe targets, three delegation timing models, content/revocation comparisons and 90 tests; no study-episode recoverability or learned-monitor result |
| Persistent delegated-stop integration | September 9, 2026 | HTTP tools, separate processes, a durable SQLite mailbox and conventional comparators; internal experiments and a separately commissioned Claude review, with no independent human validation or global-impact estimate |
| Guidance micro-pilot G0 | September 10, 2026 | First 48 real model calls comparing principles, examples and stories on 16 AI-reviewed cases; all substantive decisions correct, and the apparent strict-score lead comes entirely from Markdown formatting |
| Baseline development screen G1-D | September 10, 2026 | Sixteen calls on eight harder cases expose one wrong decision field alongside a correct rationale; a concrete consistency failure, with no story condition or held-out improvement estimate |

The original v0.3 graph check is distinct from Draft 0.1's representation-based
label-propagation proposal. Earlier versions without supplied artifacts are not
assigned invented dates or results.

## What would change the assessment?

### What the conventional tie means

The queue comparison found no advantage for NorthStar's epoch fencing over the
conventional transaction check on the tested outcomes. It supports a reusable
testbed and a known protection pattern. It does not establish NorthStar's
distinctive narrative hypothesis, which that experiment did not test.

The next research decision is whether story-guided search discovers important
failures missed by equally resourced conventional methods, or lowers the cost
of finding and repairing them. The four-method pilot must compare those methods
on unfamiliar cases and challenge the resulting repairs. Another successful
demonstration of the same stop mechanism would not answer that question. If no
useful added benefit emerges, narrow the narrative claim and retain useful
tests and conventional safeguards.

### Evidence needed next

The [first guidance rehearsal](../experiments/guidance-pilot/README.md) has now
run. It establishes feasibility, but the cases are too easy to distinguish
substantive guidance effects on the tested model. Its original scores are
preserved alongside the post-hoc diagnosis of five Markdown-wrapped responses;
we do not count the resulting one-pair S/E lead as a moral-guidance win.

The next guidance step needs independently reviewed development cases that
expose actual judgment errors, followed by fresh held-out evaluation. Keep
development selection separate from any claimed improvement. The separately
scoped four-method discovery pilot still needs its own prerequisites. Measure
actual outcomes, effort, uncertainty, and legitimate usefulness.

A reproducible advantage beyond strong comparators would justify replication
on fresh families and settings. A prevention claim additionally needs tested
repairs and independent adaptive challenges. A deployment claim needs a verified
mapping to real effect boundaries, evidence of useful adoption, and ongoing review
as systems and threats change.

## Limits on risk claims

The [NorthStar Risk Thermometer](https://anto-blit.github.io/northstar-ai-control/)
presents a chosen 10.00% reference beside verified project progress, with
[source attribution and context](risk-estimates.md). Its current risk estimate
remains unknown. The reference does not decrease with
passing tests or completed milestones; interactive monitor percentages describe
synthetic detector errors, not humanity-wide risk.

Potential global reduction is unquantified; demonstrated global reduction is
not established. Demonstrated local protection is narrower: for example, the
fixed post-stop comparison at zero monitor errors has 400/400 failures with the
starting control and 0/400 with its repair. That result tests a specified boundary
in simulation. It does not establish a real-world failure rate or global effect.

The [persistent queue pilot](../experiments/queued-stop/README.md) tests the same
kind of boundary with local HTTP calls and database commits. Both strong controls
prevent post-stop deliveries in the internal inventory, and the conventional
transactional check ties the epoch-fenced implementation. This supports the
shared protection mechanism. It does not establish a distinctive benefit from
NorthStar or its narrative approach. The test clients are scripted, the host is
trusted, and deployment adoption and catastrophe coverage remain unmeasured.

Claude's challenges count as [independent AI review](../experiments/queued-stop/claude-review/README.md)
of the local stop contract: separate test authorship and execution, commissioned
by the project using its harness. They are additional evidence, with that scope
and relationship disclosed. A capacity-exhaustion counterexample led to a concrete
repair: stop now releases abandoned claims in both strong modes, so a missing
worker need not cooperate before new authorized work can be admitted.

The scope of the evidence, rather than whether the reviewer is human or AI,
limits the conclusion. An AI can review a global-impact estimate and its basis.
This queue review did not evaluate such an estimate or supply missing deployment,
adoption and counterfactual evidence; passing its tests does not validate a
global-risk decrement.

A selected 10% humanity-wide risk is not a measured NorthStar baseline.
No current revision supplies a calibrated numerical update to it. Estimating
aggregate impact would require a defined event and horizon, a credible
counterfactual, validated prevention, adoption and coverage, interactions with
other safeguards, possible adverse effects, and uncertainty throughout.

Readiness, theoretical promise, and real-world risk reduction are different
questions. The informal numerical stage scale used in I1 has been retired from
the current assessment; its historical record remains in Git. Neither a project
score, a passing-test count, nor a DOI measures how much of the safety problem
has been solved. Absence of an impact estimate does not establish zero effect.

Evidence sources: [current status](../EXPERIMENTS-STATUS.md),
[verification record](../results/verification.json),
[guidance and evaluation protocol](../protocol/instrumentation.md), and
[comparative-study protocol](../protocol/discovery-study.md).
