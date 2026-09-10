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
