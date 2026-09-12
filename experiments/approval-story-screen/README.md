# G9: narrow approval-error story screen

Completed September 12, 2026. **The known error did not recur in this small check.**

- Four fresh responses to the two previously failing, over-limit cases: all WITHHOLD.
- Two fresh responses to their legitimate counterparts: both PROCEED.
- Six valid answers; no invalid output, provider error, refusal or retry.

The preregistered recurrence condition was not met, so the 24-call story comparison
was not activated. These are conditional calls, not missing observations from an
activated comparison. No story benefit was tested or established. Four successful
over-limit checks do not show that the earlier intermittent bug is fixed.

Exact prompts, tests, criteria and source hashes were published in
[`55da6e2`](https://github.com/anto-blit/northstar-ai-control/commit/55da6e2a1960ac2d88eea53be1ea58ec7059c4e3)
before calls. The model was requested/reported as Claude Sonnet 5; auxiliary Haiku
usage remains disclosed in the raw records. Six application calls and six CLI
turns used $0.0361428 at reported list prices (not necessarily subscription charges).
Four targeted harness checks pass, and offline verification reproduces all scores
and verifies every saved prompt, response hash and frozen input. Original evidence
is unchanged. This version is closed under its stopping rule; no victory headline
or global-risk decrement is warranted.

[Protocol](PROTOCOL.md) · [Plan and results](../../results/approval-story-screen/)

```text
py -m unittest discover -s experiments/approval-story-screen -p test_run.py
py experiments/approval-story-screen/run.py verify
```
