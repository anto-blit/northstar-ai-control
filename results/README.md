# Results

`experiment-results.json`, `property-check-results.json`, and
`baseline-comparison.json` are executed synthetic mechanism/conformance results.
`recoverability.json` reports backward induction for a bounded reach-avoid
game: the operator must reach a closed safe fallback before the deadline while
avoiding every prohibited effect. Expiration alone is not recovery. Results
declare full observation, phase order, targets and move budgets; they analyze
initial fixtures, not individual study episodes.
`monitor-sweep.json` reports seeded Monte Carlo trials across declared monitor
false-negative and false-positive rates, with benign completion beside every
prohibited fraction. Content screening and later revocation are separate
scenarios. `observed_response` describes the sample and does not infer monitor
independence; absent fn=0/fn=1 endpoints remain null. Both new artifacts use
schema 2. They are analyses of the declared model; deadlines are
ticks, not seconds, and monitor error rates are inputs, not measurements.

`verification.json` records the source hashes, result hashes, interpreter, and
test count from the latest `python verify_project.py` execution.

`guidance-pilot/` preserves the first 48-call guidance rehearsal: the pre-run
AI review, frozen prompts/source hashes, all responses, and strict scores.
`format-diagnosis.json` is explicitly post-hoc and leaves the primary scores
unchanged. All substantive decisions were correct in every condition; the
apparent story advantage in strict scoring comes entirely from output format.
See [the experiment report](../experiments/guidance-pilot/README.md) for the
small corpus, review limitations, costs, and offline reproduction commands.

`guidance-development/` contains the separate G1-D baseline difficulty screen.
Its eight cases and 16 responses expose one decision/rationale contradiction:
the principles-only action field wrongly refuses an allowed contract while
its explanation correctly says to proceed. The factual-example condition is
8/8 on this development set. No story comparison or causal improvement is claimed.

`decision-repair/` contains G2's repair lock, fresh authoring and label-review
records, frozen 216-call plan, every response and the reproducible report.
Original prompting made 3 unsafe approvals and 2 invalid responses; justification
first with a consistent final decision made neither, preserving 36/36 legitimate
approvals. Factual examples also scored perfectly. The clustered p = 0.125
leaves this small observed gain statistically inconclusive. See the
[full result and limits](../experiments/decision-repair/README.md).

`queue-integration/` is a separate persistent HTTP/SQLite pilot. Its verification
record binds runtime sources, internal and Claude-authored regression tests,
the 42 internal case/control traces, and separate-AI review provenance. It does
not alter the 90-test simulator record. Race orders, IDs and timings can vary;
the comparison checks consequences and required useful completions.

The original reviewed queue candidate, findings and tests are preserved under
[`experiments/queued-stop/claude-review/`](../experiments/queued-stop/claude-review/).
Neither a Claude review nor a passing replay establishes independent human
validation, deployment adoption, narrative advantage, or global-risk reduction.

`archive/initial-package/` preserves the original supplied JSON files, which
precede the token and audit-atomicity repairs. Their original source provenance
was not supplied; do not attribute them to the repaired implementation.

`study-feasibility/` contains a frozen manifest, scripted discovery accounting,
and paired replay results for the public feasibility example. Identical scripts
under all four labels exercise accounting only; no independent search study has
been executed. Source changes require a new frozen manifest and new run directory.

Study outcomes count episodes, including settlement. Pending work is unresolved;
reported classification ranges are not statistical confidence intervals.
The recovery game separately requires its stated safe target, including
settled delegated work or a release gate that disables dangerous pending commits.
These artifacts do not establish an archetype advantage or deployment safety.
