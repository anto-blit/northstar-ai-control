# G3: replication and controlled booking execution

**Status: interrupted by the provider's session quota. No completed replication
result is available.** Executed September 10, 2026 (America/Los_Angeles).

**Later continuation:** [G3-C](../repair-continuation/README.md) retains every
original model answer and has now completed all 720 planned answer slots.
Its separate amendment and evidence do not change this original frozen attempt.

The [plan was public before any target call](https://github.com/anto-blit/northstar-ai-control/commit/b2c2f54183420736b95fcc974bac119394217f4f).
All 120 cases passed blind label review. The run attempted 36 of 720 scheduled
requests: **27 returned usable model answers, 9 returned quota errors, and 684
were never attempted**. The preset stop rule ended the run after consecutive
operational errors, allowing already submitted requests to finish.

The model service reported: "You've hit your session limit" and a reset at
11:50 p.m. September 10, 2026, America/Los_Angeles. No targets were retried,
substituted or added, and the interrupted report remains frozen.

## What this attempt establishes

The 27 returned model answers were correct. That is a partial descriptive fact,
not a valid completed comparison or replication of the earlier improvement.
The missing cases, model coverage and paired outcomes prevent the intended
comparison. Reported p-values and fixed-denominator scores in the raw report
are mechanical accounting outputs for an incomplete run; they do not establish
either a benefit, equivalence, or a failure of the repair.

Six execution-phase decisions ran and produced three authorized local booking
records. Offline replay checks each recorded effect against the model decision.
This exercises a small part of the executor but supplies no comparative safety
claim, broader agent evaluation or real-world adoption evidence.

Known provider-reported list-price-equivalent usage totals **$0.999544**:
$0.651804 for preparation and the model probe, and $0.347740 for target requests.
These are not necessarily subscription charges. None of this changes the 10%
global-risk reference. G2 remains a provisional observation awaiting replication.

## The fixed design

G2 observed fewer unsafe approvals with justification-first prompting, but its
small sample was statistically inconclusive and factual examples tied the repair.
G3 tests whether that gain repeats under a plan published before target calls.

- Direct replication: 48 fresh pairs on Sonnet 5 and Opus 5, using G2's exact
  original, repair and factual-example instructions and case-text renderer.
- Separate transfer test: 12 further pairs per model where a valid approval
  commits a fictional booking to a local SQLite ledger. No real money or external
  service is involved. The executor never uses the answer key to correct a model.
- Fixed total: 720 calls, one answer per case/condition/model, with no extra
  repetitions or prompt changes after outcomes appear.

New numbers are seeded and checked against G2. Opus writes settings and labels;
Sonnet reviews the cases in separate contexts with the repair and answer key
withheld. This is project-run review using two models from one provider. It is
not independent human review, external replication, or a new moral task family.

The primary question concerns Sonnet's direct replication. A favorable result
must improve pair correctness, reduce unsafe approvals, preserve useful approvals
and avoid extra invalid output. Statistical support additionally requires the
prespecified paired test to reach p <= .05 with the full run operationally valid.
Opus and execution results remain separate, as does comparison with factual E.
See the [full protocol](PROTOCOL.md) for limits, guards and stopping rules.

Preparation amendment: author batches 0, 2 and 3 each supplied all 12 context
records but omitted the final outer JSON brace. Recorded one-character corrections
allowed preparation to continue. The original responses, original runner and
[amendment](../../results/repair-replication/preparation-amendment-1.json) are
preserved; no setting, numeric specification, target parser or scoring rule was
changed, and no target calls had run when the corrections were made.

Offline harness tests require Python 3.10+ and no third-party packages:

```powershell
py -m unittest discover -s experiments/repair-replication -p test_run.py -v
```

The interrupted report and local effects can be replayed without a model login:

```powershell
py experiments/repair-replication/run.py verify
```

The seven harness tests check wrong decisions despite correct reasons, actual
commit mapping, invalid-output behavior, repeated dispatch, exact paired-test
thresholds, preservation of usefulness and the fresh case inventory. Verification
preserves all 720 denominators, including the 684 unattempted calls. The raw
`invalid_or_missing` and `operational_errors` counters include those unattempted
requests; they must not be described as observed model decision failures.

## Preserved evidence and next step

- [Public registration record](../../results/repair-replication/registration.json)
- [Frozen plan and prompts](../../results/repair-replication/plan.json)
- [Reviewed cases](../../results/repair-replication/cases.json)
- [All 36 request records](../../results/repair-replication/responses/)
- [Operational stop](../../results/repair-replication/operational-stop.json)
- [Partial report with fixed denominators](../../results/repair-replication/report.json)
- [Local booking export](../../results/repair-replication/ledger.json)

Model access must be restored before further target evaluation. Any continuation
or replacement run needs an explicit public registration that preserves this
attempt and explains handling of quota failures and previously exposed cases.
The existing runner deliberately refuses automatic continuation after its stop.
The next run's sample and analysis must be fixed before its outcomes are observed.

The [impact assessment](../../docs/impact-assessment-g3.md) records the separate
evidence needed to connect any local improvement to global risk. No G3 result
automatically changes the 10% reference.
