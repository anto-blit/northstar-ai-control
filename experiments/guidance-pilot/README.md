# First guidance micro-pilot: no demonstrated narrative advantage

Executed September 10, 2026, using `claude-sonnet-5` through the existing Claude
login. All 48 planned requests completed, with no transport failures or retries
in the scored run. The cases were eight opposite-label pairs across four taught
families, tested separately in human and assistant settings.

| Condition | Frozen strict correct pairs | Frozen valid/correct answers | Substantive correct decisions, post-hoc format diagnosis |
|---|---:|---:|---:|
| Principles only (P) | 7/8 | 14/16 | 16/16 |
| Principles + structured examples (E) | 6/8 | 14/16 | 16/16 |
| Principles + stories (S) | 7/8 | 15/16 | 16/16 |

**The one-pair S/E lead is entirely an output-format difference.** Five responses
contained correct JSON wrapped in Markdown fences: two P, two E, one S. The
frozen scorer rejects those wrappers and the primary scores remain unchanged.
There were no incorrect substantive approvals or refusals. A separately labeled
post-hoc diagnostic removes only that enclosing fence and finds all conditions
at 16/16 decisions and 8/8 pairs. This is not evidence that stories improve moral
judgment, nor evidence that all narrative approaches are equivalent to examples.

The mechanical screening flag in `report.json` is true because S satisfies the
frozen one-pair threshold. Inspection shows that it should **not** be interpreted
as the desired research win. No extra model calls or rewritten cases were used
to improve the outcome. The useful finding is that this corpus is too easy to
discriminate substantive performance on this model, as the reviewer warned.

## What ran

The four families concern specific consent, delegated stop, honest reporting of
verified results, and consent to binding future obligations. Each pair changes
a decisive fact and includes an action that should be allowed, avoiding a
block-everything success criterion. This tests judgments, not actual execution.

Both guidance packets present the same four synthetic examples, facts, decisions
and reasons. With the common principles included, E has 456 whitespace words
and S has 425, a 7.3% longer E packet. P has 92. There are no traditional story
quotations; these are original brief parables authored for the project. The
story condition tests this particular prose treatment, not all storytelling.

A separate tool-free Claude call agreed with all 16 provisional author labels,
without seeing the answer key, and found no substantive mismatch. It also
warned that the cases looked mechanically obvious. The reviewer put positive
matching findings in its `matching_issues` array; the preserved
[author adjudication](review-adjudication.json) explains their acceptance.
The same model served as reviewer and target in separate contexts. There was no
independent human review, and the author knew all cases while authoring guidance.
Treat this as an exploratory rehearsal, with new settings inside known families.

The [protocol](PROTOCOL.md), source hashes, exact prompts, labels, model ID,
order, resource limits and scoring were frozen before any scored request.
The freeze was at 01:59:54 UTC on September 11 (18:59:54 PDT September 10), and
the run finished at 02:01:18 UTC. Local timestamps and hashes are not public
preregistration or external attestation. Sampling defaults remain provider-managed.

The 48 calls report **$0.349609** in list-price-equivalent usage; pre-run review
reports **$0.054763**, and the successful unrelated OK probe **$0.002219**,
for **$0.406591 known total**. These figures are not necessarily subscription
charges. An initial sandboxed OK probe timed out; its usage is unknown. The
scored run took about 77 seconds with three concurrent tool-free requests.
Preparation effort was not separately metered or matched between arms.

## Evidence and offline reproduction

- [Frozen plan and every target prompt](../../results/guidance-pilot/frozen-plan.json)
- [Original primary scores](../../results/guidance-pilot/report.json)
- [Post-hoc format diagnosis](../../results/guidance-pilot/format-diagnosis.json)
- [All 48 response records](../../results/guidance-pilot/responses/)
- [Pre-run label and guidance review](../../results/guidance-pilot/material-review.json)
- [Materials and answer key](materials.json)

No model access is needed to recompute and verify the stored results:

```powershell
py -m unittest discover -s experiments/guidance-pilot -p test_pilot.py -v
py experiments/guidance-pilot/pilot.py verify
py experiments/guidance-pilot/diagnose.py
```

The checks reproduce scores against the frozen sources and evidence. Live `run`
resumes only missing request files and otherwise reuses the preserved responses;
it does not generate an independent replication. A new experiment needs a new
version and results location. Do not remove responses to obtain a better score.

The next useful study needs a separately reviewed development set that exposes
actual judgment errors in the principles/examples baselines, then freshly held-out
evaluation material. Development difficulty selection must be recorded and
separated from the evaluation used to claim improvement. This run supplies no
reason to expand solely to chase a positive result.
