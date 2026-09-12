# G12: frozen-story confirmation against strong simple guidance

Prepared 128 fresh matched pairs and one response per case under the original
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
