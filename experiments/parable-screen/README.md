# A reusable parable test, prepared offline

September 14, 2026. **Zero model calls. Draft proposal, not a registered live
comparison.** The user authorized this preparation and its documentation/site
publication. G17's original plans, results and v2 machinery are preserved.

We have **one qualified failure family, with multiple cases and repeated
trials**: accepting a binding agreement above the owner's spending limit.
That is enough to build the test and screen relevant parables for this task.
It is not enough to establish effectiveness across different kinds of mistakes.
Other searches have not qualified another recurring baseline for this test.

The next scientific steps are candidate selection on this family, fresh
confirmation if warranted, then a separately qualified different failure family
before a broader transfer claim. The [protocol](PROTOCOL.md) explains the
evidence, limits, controls, thresholds, budget and stop rule.

## What is prepared

- An interchangeable catalog containing the squirrel, keeper and permission-seal
  parables, each with its own matched factual explanation and the same explicit
  rule. These candidates have no established ranking. See [candidates.json](candidates.json).
- Fresh cases from the recorded task renderer, checked for arithmetic and
  separation between baseline, screen and historical G12 scenarios.
- A new draft plan: **44 baseline-check calls, then at most 384 screening calls**
  if that check passes. Eight conditions: ordinary prompting, simple repair and
  three story/factual pairs. Proposed total cap: **428 calls / US$10 reported
  list-price usage**. These are proposed ceilings, not authorized calls or a
  forecast of charges. A live adapter is not included.
- Synthetic execution, scoring, candidate-selection diagnostics, stop handling,
  partial reports and replay. Synthetic answers do not evaluate any story.

The saved [draft plan](../../results/parable-screen/draft-plan.json) contains all
prompts and candidate versions. It has `live_registered: false` and
`model_calls_authorized: 0`. The website's proposal form is a separate way to
collect ideas; submitting a parable does not add it to this fixed shortlist.

## Run the offline checks

From the repository root:

```powershell
py -m unittest discover -s experiments/parable-screen -p test_run.py -v
py experiments/parable-screen/run.py check results/parable-screen/draft-plan.json
```

To retain a synthetic demonstration, use a new directory:

```powershell
py experiments/parable-screen/run.py demo results/parable-screen/draft-plan.json study-runs/parable-screen/demo-01
py experiments/parable-screen/run.py verify study-runs/parable-screen/demo-01
```

`--fixture all-correct` exercises a baseline that does not fail: it stops after
44 fixtures, with all 384 conditional screen slots unattempted.
`--service-error-at 50` injects an error and stops after that attempt. `recover`
rebuilds an interrupted report and identifies an unresolved reservation; it
never resumes. Existing demonstration directories cannot be reused.

To try different parables **offline**, copy the catalog, retain one to three
candidates for this same lesson, edit their story/factual text and versions, then
make a new draft:

```powershell
py experiments/parable-screen/run.py draft study-runs/parable-screen/my-draft.json --catalog path/to/my-candidates.json
```

Catalog entries may supply inline `rule`, `story` and `facts`, or name literal
constants in a repository Python file. Referenced files are parsed, never run.
Every catalog must keep the explicit rule fixed across its candidates. Content
matching still needs human/reviewer judgment. Modified packets cannot be slipped
into an existing draft. No command accepts a live plan or invokes a provider.

## Reading a result

A synthetic nomination only checks that the selection code works. In a future
registered screen, a nomination would be exploratory and require fresh
confirmation. With 32 over-limit cases per condition, modest differences among
good remedies may be invisible. A high ordinary baseline error does not ensure
enough errors remain after plain guidance or repair to distinguish the stories.
Perfect scores do not establish equivalence. No present result ranks parables
or changes the site's global-risk reference.
