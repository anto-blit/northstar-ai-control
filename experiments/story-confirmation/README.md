# G12: frozen-story confirmation against strong simple guidance

**Stopped before target calls.** The first Opus method audit raised six blocking
concerns. The exact review is [preserved](../../results/story-confirmation/review/responses/0000.json),
with $0.194568 usage and zero target answers. Its packet contained the protocol
and summary scorer but omitted the runner/parser that enforced several guarantees.
The reviewer also treated per-call budget guards as billed prices; the runner
accumulates actual reported usage and only reserves the next call or batch.

The [G12-A amendment](../story-confirmation-v2/README.md) supplies the complete
execution context and strengthens duplicate/flag validation and explicit missing
counts. Cases, target prompts and comparison thresholds remain unchanged; the
original audit cost stays within the same $12 ceiling. No target result informed
the amendment. This original version remains closed and unrescored.

The original plan prepared 128 fresh matched pairs and one response per case under the original
prompt, factual guidance, unchanged fable and justification-first repair.
The plan has 17 separate Opus review calls before 1,024 Sonnet target calls,
with a $12 overall reported-usage ceiling. All responses are retained.

The [protocol](PROTOCOL.md) distinguishes support against the factual example
from added protection over the simple repair. Both comparisons use a predeclared
statistical threshold, reject formatting wins as semantic evidence and require
the story to preserve legitimate approvals. Reviewers do not see target answers.

[Exact cases, review packets and all requests](../../results/story-confirmation/)

```text
py -m unittest discover -s experiments/story-confirmation -p test_run.py
py experiments/story-confirmation/run.py verify
```
