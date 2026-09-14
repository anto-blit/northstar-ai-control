# Review of the method and messaging feedback

September 14, 2026. Interpretation and website work; no new study, model calls,
scoring changes or authorization to run the proposed calibration.

The useful recommendation is to explain both roles of stories on the public
site. A story can suggest a failure pattern to investigate, and its proposed
lesson can be tested as guidance. Evidence for one role does not establish the
other. The current project pursues both; describing it exclusively as a way to
generate test ideas would omit the active guidance research.

## What is already present

The [discovery protocol](../protocol/discovery-study.md) compares action-search
methods and the repairs they produce. Its four approaches are informed generic
red teaming, conventional technical threat analysis, causal patterns stripped
of narrative framing, and the full NorthStar method. An independent comparison
has not been performed. Comparing methods for generating test corpora would
require a separate frozen design; the action-search harness is not that study.

The [evaluation protocol](../protocol/instrumentation.md) already defines strict
pair correctness: both members of an eligible opposite-label pair must be
correct. The [first guidance pilot](../experiments/guidance-pilot/README.md)
implemented this score. Its frozen results were 7/8, 6/8 and 7/8 correct pairs;
the differences were output-format failures, with no substantive story advantage.
Joint scoring is therefore worth explaining, rather than presenting as a new
measurement we have yet to invent.

The two-commit repository described in the feedback is an old snapshot. The
browser search returned that same snapshot during this review, while the live
GitHub API and fetched main branch agreed on
[`4a48d5d`](https://github.com/anto-blit/northstar-ai-control/tree/4a48d5d473f8a2047c8df19f1c33c46d067b401d),
which contains G10, G17 and `northstar_at_home`. This is not evidence of a repo
rewrite. The current README did have stale next-step copy, including an obsolete
Claude exclusion; that copy is now aligned with the handoff and the proposed
236-call calibration.

## What the site now explains

- Stories suggest hypotheses; their names do not establish moral authority or
  experimental evidence. Discovery and guidance each face their own comparison.
- A proposed failure needs a prohibited outcome and a closely matched legitimate
  task. An illustrative pair changes only the price, so the correct decision
  changes from seeking permission to proceeding.
- Joint pair success requires both decisions to be right. Separate counts of
  wrong approvals, unnecessary refusals and invalid outputs remain important.
- Conventional methods get matched resources in the proposed discovery study.
  Effective repairs remain useful even when narrative framing adds no value.
- Accumulating permissions and delegated work that survives stop are concrete
  examples of patterns spanning multiple steps, drawn from the original method.

The existing studies retain their frozen scoring, denominators and results.
The G17 approval counts and the proposed calibration are not retroactively
converted into strict pair scores. Future use of a joint endpoint needs a
published pair mapping, one-decisive-fact review, repeated-sample pairing rule,
missing/invalid-output policy and uncertainty calculation that respects related
cases. A joint score complements the individual error rates; it does not replace
them or establish safety outside the tested cases.

## Suggestions to retain as research questions

A consistency monitor is a plausible separate follow-up. It could check whether
an action contradicts an independently verified limit or its stated supporting
facts. A classifier that only notices the decision being printed before the
calculation would be confounded by the requested answer format: several current
prompts explicitly ask for that order. Visible text order does not expose the
model's internal computation or establish motivated reasoning.

Before calling such a monitor useful, compare it on fresh, reviewed trajectories
against a direct authorization check and the existing repair. Include correct
decision-first answers, incorrect explanation-first answers and legitimate tasks;
measure missed violations, false alarms, useful completion and added cost. Any
preventive claim also needs the check to run before the consequential action.
This review proposes that question only; it implements or registers no monitor.

The camel's nose and sorcerer's apprentice are useful illustrations of cumulative
authority and continuing delegated work. Their priority for a new experiment
should depend on an observable recurring failure and a fair comparator.
Conventional controls can track aggregate authority and recheck revocation at
dispatch; our own queue work provides a strong conventional benchmark. We have
no evidence that conventional threat modeling is generally weak on these problems
or that those two stories outperform the other candidates.

## Prior work and the claim we can defend

Testing inappropriate refusal is established work. [XSTest](https://aclanthology.org/2024.naacl-long.301/)
uses safe prompts with unsafe contrasts to examine exaggerated safety behavior.
[OR-Bench](https://arxiv.org/abs/2405.20947) evaluates over-refusal at scale and
includes toxic prompts to check indiscriminate compliance. These sources support
crediting prior work, not dismissing safety benchmarks as mainly measuring timidity.

NorthStar can describe its concrete combination of reviewed authorization cases,
paired decisions, executable effects, factual comparators and prospective
confirmation. Whether that combination is novel or superior requires further
review and comparative evidence. The stronger immediate message is a testable
method with a clear way to reject its distinctive claim.
