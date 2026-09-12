# Results

`story-continuation/` preserves G5-C's public amendment, sixty new provider
responses, thirty new local ledgers and a combined replayable report. All thirty
new episodes completed correctly. Combined D 11/12 useful/correct completions
(one original refusal), F/S 12/12. S/F has twelve jointly valid ties; S/D has
eleven ties and one excluded pair. No observed story advantage. The original
G5 records below stay immutable. See [results and limits](../experiments/story-continuation/README.md).

`story-distillation/` contains G5's public plan, compiled provisional rule set,
12 provider-call records, six episode ledgers and an operational stop report.
Five episodes completed correctly; one was interrupted by a provider safety
error labeled `[bio]`, and 30 were not started. There is no behavioral advantage
finding. The frozen S/D fixed-slot counter includes the missing D answer and
must not be interpreted as a moral win; see the
[complete accounting and limits](../experiments/story-distillation/README.md).
The associated [six-story catalog](../curriculum/README.md) and interactive
rule checker are engineering artifacts with human review pending.

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

`repair-replication/` preserves the publicly registered G3 follow-up and its quota
interruption. All 120 cases passed review; 27 of 720 planned calls returned model
answers, 9 returned quota errors and 684 were not attempted. The fixed-denominator
report includes all missing requests without treating them as observed wrong
decisions. Three harmless authorized booking effects replay offline. No completed
replication claim follows. See the [attempt report](../experiments/repair-replication/README.md).

`repair-continuation/` preserves G3-C's public operational amendment, readiness
probes, 696 attempts, execution traces, both checkpoints and the preserved
534-answer partial report. Its final report selects 720 model answers: 27
originals and 693 continuation answers. Twelve historical quota rejections
remain separate. Sonnet's original format has two unsafe direct approvals and
one invalid booking response; repair and factual examples tie without observed
errors. Opus scores perfectly. The completed Sonnet gain remains inconclusive
(paired p = 0.5). All 72 unique authorized bookings replay; no unsafe booking
occurred in any condition. See the
[complete results and every observed failure](../experiments/repair-continuation/README.md).

`codex-repair/` contains G4's public 288-call plan, three unscored preparation
probes, registration, every target response and completed report. Requested
GPT-6 Astra scored 96/96 with each of original prompting, repair and factual
examples: zero unsafe/invalid answers and all legitimate approvals preserved.
The 288 target thread hashes are distinct; no operational failure or tool action
occurred. Scores and usage replay offline. Dollar charges are not exposed by
the CLI. This is a ceiling result with no observed repair advantage, reported
separately from Claude. See the [full result](../experiments/codex-repair/README.md).

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
