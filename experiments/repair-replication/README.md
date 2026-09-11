# G3: replication and controlled booking execution

Status: all 120 cases passed pre-run label review. The 720-call target plan is
frozen for public registration; no target result yet.

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

After the completed run is published, all scores and local effects can be
replayed without a model login:

```powershell
py experiments/repair-replication/run.py verify
```

The [impact assessment](../../docs/impact-assessment-g3.md) records the separate
evidence needed to connect any local improvement to global risk. No G3 result
automatically changes the 10% reference.
