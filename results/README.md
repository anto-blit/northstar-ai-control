# Results

`experiment-results.json`, `property-check-results.json`, and
`baseline-comparison.json` are executed synthetic mechanism/conformance results.
`verification.json` records the source hashes, result hashes, interpreter, and
test count from the latest `python verify_project.py` execution.

`archive/initial-package/` preserves the original supplied JSON files, which
precede the token and audit-atomicity repairs. Their original source provenance
was not supplied; do not attribute them to the repaired implementation.

`study-feasibility/` contains a frozen manifest, scripted discovery accounting,
and paired replay results for the public feasibility example. Identical scripts
under all four labels exercise accounting only; no independent search study has
been executed. Source changes require a new frozen manifest and new run directory.

Outcomes count episodes, including settlement. Pending work is unresolved;
reported classification ranges are not statistical confidence intervals.
These artifacts do not establish an archetype advantage or deployment safety.
