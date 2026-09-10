# Independent AI review: Claude

The founder requested Claude as the other reviewing party. The project used the
installed Claude Code CLI against copied, frozen runtime sources. The initial
review packet included the contract and API, but excluded the implementation
author's case inventory, experiment runner and results. The review could inspect
the implementation, write its own tests and run local loopback experiments.

We count this as **independent AI review of the local stop contract, commissioned
by the project**. Claude independently authored and ran challenges; it was not the
implementation author, and our case inventory and results were withheld. The
project chose the assignment, supplied the harness and managed the repairs, so
this does not claim organizational independence or an independent data source.
The test cases are AI-authored, not sampled from real deployment traffic.

AI review counts as review. Its scope determines what it validates. These runs
support the local behavior exercised by the tests. They did not measure adoption,
catastrophe coverage or a counterfactual global-risk reduction. A passing AI or
human review cannot supply those missing observations. A future AI review of an
impact estimate can count as such, with its evidence, assumptions and uncertainty
stated; this review was not that assessment.

The frozen reports retain their original terminology. This clarification changes
how the project credits the review, not what Claude tested or concluded. Claude's
interpretation is also subject to review; observations take priority over broad wording.

## Original candidate

The [original snapshot and tests](candidate-1.zip) preserve the implementation
before the repairs, including characterization tests for the original behavior.
Extract the archive into a separate directory and run:

```bash
python -m unittest discover -s review_tests -v
```

Claude's [candidate-1 report](candidate-1-review.md) records 45 tests, with 44
passing and one failing. Some passing tests intentionally demonstrate a defect
or limitation, so the passing count is not an all-clear. The strong controls
produced no prohibited delivery on these cases; cooperative cancellation did.
The [review prompt](candidate-1-prompt.txt) and provenance record document scope.

## Findings and project response

| Finding | Evidence | Response |
|---|---|---|
| F1: incomplete HTTP body | Claude reproduced a connection that waited about five seconds and closed without an HTTP status | Return a 400 response on the two-second local idle read timeout; handle recursion errors across Python versions |
| F2: parent resume lifted child stops | Claude reproduced a separately stopped child becoming active after parent stop/resume | Resume only the named scope; a child requires its own explicit resume and fresh capability |
| F3: one root filled all admission slots | Claude reproduced one agent blocking another root's first submission | Limit outstanding jobs per root family, with descendants sharing the quota, alongside the global cap |
| O1: claimed jobs remained unsettled | Claude identified retained claims; the implementer separately reproduced admission exhaustion when a worker abandoned them | Both strong controls cancel claimed work on stop, releasing capacity without worker cooperation |
| Resource handling | Internal checks exposed unclosed SQLite/HTTP resources during cleanup | Close bootstrap connections and HTTP error responses explicitly; reviewer cleanup checks should no longer suppress errors |

F1 is a broker robustness check using raw HTTP beyond the standard tool client's
framing. Raw HTTP does not require database privilege, and the fix is useful
without treating it as a post-stop delivery exploit. F2 concerns a trusted
operator action. F3 is reachable through the declared agent submission tool and
is a useful-work failure; we did not dismiss it because delivery remained safe.

The first abandoned-claim counterexample filled the original 128-job limit,
stopped/resumed the scope, and received HTTP 409 for fresh authorized work in
epoch mode. The retained regression now exercises the amended per-family bound.
The original code remains in the archive so the counterexample is recoverable.

## Repaired candidate and remaining scope

The [follow-up review](candidate-2-review.md) records Claude's checks of the
repairs, amended regression expectations, and further challenges: **53 tests
passed in Claude's own run**. The current
Claude-authored tests live in [`review_tests/`](../../../review_tests/). Changes
to characterization tests assert the corrected contract; they do not delete
the original counterexamples or relax prohibited-delivery checks.

Run the combined local verification using a fresh output directory:

```bash
python -m northstar_queue.verify --output study-runs/queue-reviewed/my-run
```

The [published verification](../../../results/queue-integration/verification.json)
separately records internal regressions, the replayed Claude cases, and all 42
internal case/control runs. [Provenance](provenance.json) identifies models,
candidate/source hashes, review artifacts and the difference between Claude's
own run and the project's subsequent replay.

The strong conventional control ties NorthStar on the internal comparison.
This supports their common transaction-boundary mechanism; it does not show
distinctive narrative value or a general superiority of epoch fencing.
The host, worker credentials and database remain trusted. Capacity limits do not
guarantee general fairness or availability under overload: two saturated root
families still fill the 128-job global pool, blocking a third root. Stopped scopes
also retain their place in the family scope limit. The local read timeout
is an idle timeout, not a wall-clock response SLA. External destinations need a
separate enforcement design. No global-risk percentage reduction is established.
