# G12-A: confirmation with a complete review packet and stricter validation

**Stopped before targets.** The [method audit](../../results/story-confirmation-v2/review/responses/0000.json)
accepted the scoring, validity, inventory and eligibility logic, but withheld
approval because the packet lacked case-generation and transport dependencies.
This version made zero target calls and cost $0.582853, bringing both audits to
$0.777421. The [G12-B packet completion](../story-confirmation-v3/README.md) preserves
this audit and supplies those dependencies without changing the experiment.

The [original G12](../story-confirmation/README.md) stopped on a method audit before
any target call. This amendment adds the full runner and parser to the review
packet and makes the scorer reject duplicate or inconsistent records itself.
Every case, target prompt, comparison and threshold stays unchanged. The shared
$12 ceiling includes the original audit's $0.194568 usage.

[Amended protocol](PROTOCOL.md) · [Complete record](../../results/story-confirmation-v2/)

```text
py -m unittest discover -s experiments/story-confirmation-v2 -p test_run.py
py experiments/story-confirmation-v2/run.py verify
```
