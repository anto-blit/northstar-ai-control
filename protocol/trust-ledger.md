# Trust Ledger
| Dependency | Assumption | Evidence needed |
|---|---|---|
| Outcome definition | Captures the claimed harm | Independent review and benign alternatives |
| Simulator | Relevant effects/timing/delegation represented | Interface inventory, trace review, differential tests |
| Effect broker | Accepted effects implement rules | Code review, conformance tests, finite enumeration where feasible |
| Isolation/credentials | Agent cannot bypass broker | Privilege inventory and exposed-interface testing |
| Shared state/scheduler | Current state and revocation semantics hold | Stale-state, ordering, dispatch and failure tests |
| Learned monitor | Adequate for declared semantic role | Adaptive attacks and FP/FN tests |
| Human reviewer | Decisions sufficiently accurate/timely | Measured error, latency and capacity |
| Outcome oracle | Scores consequences without leaking them | Independent implementation and trace witnesses |

"Trusted" names an assumption. It does not mean infallible.

## Current evidence

`tests/test_regressions.py` covers consumed-token reuse, pending-token collision,
reviewed-object/actor binding, and state/receipt publication when ledger append
raises before or after writing to the private candidate state.

`tests/test_study.py` covers strict proposal fields, runner-assigned identities,
frozen plan/source checks, online-field separation, resource accounting,
settlement, and a scorer that can detect an author-specified outcome missed by
the broker's hard constraint. CLI tests cover resume provenance and retention of
invalid accounting envelopes.

These are local tests authored with the implementation. No independent security
review, operating-system isolation test, learned-monitor evaluation, human-error
measurement, or external ledger anchoring has been completed. Current result
hashes and interpreter details are in `results/verification.json`.

## Persistent queue pilot

The [queue integration](../experiments/queued-stop/README.md) separately tests
loopback HTTP role boundaries, SQLite authority/effect transactions, worker claim
binding, stop/resume, restarts, concurrency and useful completion. Its host-side
fault injection confirms rollback on a failed mailbox write. An explicit direct
database write also demonstrates that a same-account filesystem actor can bypass
the broker; process separation must not be described as verified OS isolation.

The [Claude review](../experiments/queued-stop/claude-review/README.md) counts as
independent AI review of the local stop contract: separate test authorship and
execution, commissioned by the project using its harness. Global impact was not
evaluated. The original simulator's
verification record and 90-test count remain separate from this evidence.
