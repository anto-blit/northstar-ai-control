# G8-C: evidence integrity with corrected metadata handling

Prepared; target results pending. The [amendment](PROTOCOL.md) preserves G8's failed
interface canary and starts fresh. SQL-only metadata cannot become a final report.
The original task, guidance, controls, scorer, and $12.48 nominal cap are unchanged.

```text
py -m unittest discover -s experiments/evidence-integrity-continuation -p test_run.py
py experiments/evidence-integrity-continuation/run.py register
# Publish inputs and record publication.json before run.
py experiments/evidence-integrity-continuation/run.py run
py experiments/evidence-integrity-continuation/run.py verify
```
