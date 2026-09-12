# G12-B: complete dependency review, unchanged confirmation comparison

G12 and G12-A made zero target calls. The second method audit accepted scoring
and gating but withheld approval because materials/transport dependencies were
absent from its packet. G12-B provides those sources, exact guidance values and
test execution. All cases, target prompts, scoring and statistical thresholds
remain unchanged from G12-A; the $12 total ceiling includes both earlier audits.

[Protocol](PROTOCOL.md) · [All records](../../results/story-confirmation-v3/)

```text
py -m unittest discover -s experiments/story-confirmation-v3 -p test_run.py
py experiments/story-confirmation-v3/run.py verify
```
