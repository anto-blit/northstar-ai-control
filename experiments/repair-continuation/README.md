# G3-C: continuation after the quota reset

The user requested a delayed retry. This separate, publicly registered amendment
preserves G3's interrupted report and all 27 returned model answers. It allows
only the nine confirmed quota rejections and 684 never-attempted slots to run.
No wrong or malformed model answer may be replaced. The original 720 slots,
cases, prompts, models, scoring and comparisons remain fixed.

The amendment was prepared after the first 27 answers were known. It changes
the no-retry operational rule explicitly and is not an untouched new replication.
Every quota rejection and model response remains available for inspection.
See [the protocol](PROTOCOL.md) and [the interrupted original](../repair-replication/README.md).

Status: waiting for the reported provider reset at 11:50 p.m. Pacific on
September 10, 2026. No continuation model call is permitted before 06:50:05 UTC.
Both exact models must pass a tool-free readiness probe before target submission.

Offline tests:

```powershell
py -m unittest discover -s experiments/repair-continuation -p test_run.py -v
```

When the final report is available, replay it without model access:

```powershell
py experiments/repair-continuation/run.py verify
```

The resumed comparison will retain the original model/family limitations and
conventional comparator. It will not subtract an invented global-risk discount
from the site's 10% reference.
