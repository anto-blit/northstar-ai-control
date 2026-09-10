# Reproduce and challenge the queued-stop integration

An outside reviewer should record the exact revision, operating system, Python
and SQLite versions, relationship to the project, and whether they saw the
existing cases before authoring new ones. Run in a disposable local directory.
Do not expose the server to a network or supply real credentials or sensitive
payloads. Local process termination and temporary-file cleanup are handled by
the harness.

1. Read `PROTOCOL.md` and `REVIEW-API.md`; state which contract you are testing.
2. Author additional attacks against a frozen revision before reading internal
   results where practicable. Preserve attempted cases, including unsuccessful
   attacks and legitimate-work controls.
3. Run all three modes. Check actual mailbox effects, event ordering and useful
   completions. A rejected request is not sufficient evidence.
4. Reproduce any failure and distinguish an API attack from trusted-host fault
   injection, denial of service, a scorer error or an unsupported external sink.
5. Publish the code, commands, output, candidate hashes and limitations. A repair
   should retain the original counterexample and be retested on further cases.

Suggested open challenges include response loss at commit, concurrent resubmission,
multi-level stop/resume interleavings, retries held by old workers, busy/failed
storage, and a destination with a separate commit boundary. No claim is made
that these exhaust the attack surface. Test locally with harmless effects only.

The public GitHub [failure-report form](https://github.com/anto-blit/northstar-ai-control/issues/new?template=control-failure.yml)
and [collaboration form](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml)
are available for reviewer submissions. No external reviewer is represented as
having endorsed the project without a corresponding attributable report.

## What this can establish

A reproducible stop failure and successful repair in this integration would
strengthen the evidence for a local control contract. Matching a conventional
repair supports that common mechanism, not distinctive narrative value. The
four-method discovery study is still required to test that separate question.

A global impact assessment additionally needs a plausible causal path to
catastrophic harm, additional protection over the counterfactual, relevant
coverage, actual or credible future adoption, uncertainty and adverse effects.
Do not subtract a percentage point from the dashboard for completing this review.
