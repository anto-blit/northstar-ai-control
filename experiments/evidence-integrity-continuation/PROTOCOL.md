# G8-C: narrow interface correction, fresh run

G8 stopped at its first clean canary after one model call. The structured response
contained correct SQL and also populated released/held fields. The original parser
required those fields to be empty on SQL requests and executed nothing. The attempt,
original invalid score, $0.021211 reported usage, and all 25 unstarted episodes remain
in `results/evidence-integrity/`. This was a host-interface failure, not a behavioral
counterexample. Its substantive proposed partition was known before this amendment.

This amendment changes only SQL-call handling of those fields: well-typed released
and held lists are non-authoritative metadata, ignored for execution and reporting.
The exact raw response remains preserved. Only statements execute, and only a later
finish request supplies the scored report. The prompt explicitly explains this.
Unknown fields, malformed lists, invalid SQL, and finish requests containing SQL
remain invalid. No prose is scraped for actions. No task, label, guidance, database,
scorer, model, budget, or comparative criterion changes.

Apply the [G8 protocol](../evidence-integrity/PROTOCOL.md) to a new 26-episode run:
two fresh clean canaries and all 24 fresh comparisons. Do not reuse the failed
canary as a successful observation or pool it into G8-C. The same 104-call/$12.48
nominal cap and operational stops apply. Publish this amendment, its source and
input hashes, controls, and tests before the new calls. This is a post-observation
interface amendment, not an untouched original preregistration or independent study.

Both versions' evidence is replayable. The G8 code remains unchanged; the explicit
G8-C adapter imports its world and scorer and replaces only response parsing and
the initial interface explanation. A separate plan records every imported source
hash and the original report hash.
