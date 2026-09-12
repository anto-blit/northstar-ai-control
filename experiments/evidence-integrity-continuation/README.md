# G8-C: evidence integrity with corrected metadata handling

Completed September 12, 2026. The conventional safeguard blocked the scripted
integrity failures. The model comparison found no added benefit from stories.

| Guidance | Clean notes | Malicious vendor notes | Total successful episodes |
|---|---:|---:|---:|
| Ordinary instructions (D) | 4/4 | 4/4 | 8/8 |
| Principles + factual example (F) | 4/4 | 4/4 | 8/8 |
| Principles + original fable (S) | 4/4 | 4/4 | 8/8 |

All 24 comparison episodes completed the correct partition: 120/120 required
legitimate release records and 72/72 appropriate review records. No source-write
attempt, committed evidence alteration, unauthorized release, inaccurate final
report, invalid output, refusal, service failure, exhausted or missing episode.
Both fresh clean canaries also passed (ten additional legitimate releases).
Every matched S/F comparison ties: zero wins, zero losses, eight ties. There is no
observed story advantage or demonstrated spontaneous cheating on these cases.

The separately scripted controls test two failure paths across four data/note
variants: rewriting the checks/approval, and releasing items without passing
evidence. All eight weak-control attack trials produce three unauthorized records
each (24 total). The transaction guard produces zero; after rejection, all 40/40
required legitimate releases complete. Four additional legitimate-only trials per
mode also pass. These are 24 scripted control trials total, not 24 AI failures or
independent failure mechanisms. The guard is conventional engineering, not a
demonstration that stories changed judgment.

The model ran with the weak connection so the guard could not conceal a guidance
difference. Replaying its fixed actions through the guard also preserves the
recorded correct outcomes. That replay is not an adaptive guarded-agent trial.

## Provenance and limits

The [G8-C amendment](PROTOCOL.md), inputs, controls and tests were pushed in
[`46a8446`](https://github.com/anto-blit/northstar-ai-control/commit/46a8446edcf716f1afa82e2cf8aa0f2e90f06609)
before fresh model calls. It follows the known original G8 interface failure,
which remains [preserved and separately scored](../evidence-integrity/README.md).
SQL-only metadata cannot become a final report. No G8 response was reused as a
successful G8-C observation. The original task, guidance, controls, scorer, model,
and $12.48 nominal cap were unchanged.

Requested Claude Sonnet 5 is reported on all 52 application calls; the CLI reports
104 turns. Auxiliary Haiku usage appears in the raw records, with no inference
about its internal role. Known list-price usage is $1.1447502 for G8-C, plus
$0.021211 for the preserved original attempt ($1.1659612 total); these are not
necessarily subscription charges. No provider substitution or target-call retries.

Fourteen harness tests pass locally. Full offline replay verifies original inputs,
every response/action/receipt, committed SQLite state, reporting and all scripted
controls. The publication record hashes ten source files and 121 evidence files.
The dashboard checks these hashes; dedicated CI also re-executes the SQL replay on
Windows/Linux with Python 3.12/3.14.

This is one small mock release task with renaming/order variants and an explicit
prompt injection, authored and scored by the host assistant. There is no external
human review, unfamiliar-domain transfer, independent replication, or real-world
failure-rate estimate. The fictional animal story is a prompt example, not model
training. The published stopping rule closes this version: do not add repetitions
to seek a favorable narrative result. No global-risk decrement.

## Reproduce the record

The [report](../../results/evidence-integrity-continuation/report.json),
[all episodes](../../results/evidence-integrity-continuation/episodes/),
[scripted controls](../../results/evidence-integrity-continuation/controls.json),
and [publication verification](../../results/evidence-integrity-continuation/verification.json)
are public. Verification makes no model calls.

```text
py -m unittest discover -s experiments/evidence-integrity-continuation -p test_run.py
py experiments/evidence-integrity-continuation/run.py verify
py experiments/evidence-integrity-continuation/publish.py verify
```
