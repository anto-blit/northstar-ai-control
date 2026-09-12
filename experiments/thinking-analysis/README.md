# Thinking analysis — a re-reading of frozen G10/G11 evidence

This is **not a study**. It makes no model calls, generates no new evidence and
changes no frozen result. It reads the saved G10 and G11 responses and reports,
splits them on the `thinking_tokens` field that was recorded at the time, and
recomputes what that split implies.

The finding and its limits: [docs/thinking-and-failure.md](../../docs/thinking-and-failure.md).

## Replay

```powershell
py experiments/thinking-analysis/analyze.py verify   # checks the published numbers
py experiments/thinking-analysis/analyze.py          # prints the full analysis
```

`verify` recomputes every published claim from the frozen responses and exits
non-zero on any mismatch, so the document cannot drift from the evidence. The
frozen output is [results/thinking-analysis/report.json](../../results/thinking-analysis/report.json);
regenerate it by redirecting the second command.

## What it computes

- The pooled 300-call split on `thinking_tokens`, and the same split per study.
- Per-prompt rate of zero-thinking calls in G10, where prompts are repeated
  under fixed settings.
- G11 arm behaviour inside and outside the non-thinking subgroup, with an exact
  Fisher two-sided p-value for story against the other two arms.
- Artifact checks — service tier, speed, elapsed time, and the longest run of
  consecutive zero-thinking calls in wall-clock order — that would expose a
  service window or truncation rather than a per-call model property.

## Feasibility probe: the knob works

`probe_effort.py` asks one engineering question before a study is designed around
the answer — does the Claude CLI's `--effort low` actually reach the
non-deliberating regime? G16 assumed a "low" setting meant low deliberation and
was wrong, so the knob gets measured first.

Thirty calls on the exact frozen G10 prompts, pooled over two probes:

| | calls | zero-thinking | wrong approvals | invalid | correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| Case 068 (over limit) at `low` | 15 | **13 (87%)** | 3 (20%) | 5 | 7 |
| Case 068 at `medium` (G10, for comparison) | 50 | 17 (34%) | 6 (12%) | 11 | 33 |
| Case 407 (legitimate control) at `low` | 15 | **0** | — | 0 | **15/15** |

Lowering effort raises the zero-thinking rate on the failing prompt from 34% to
87% and the wrong-approval rate from 12% to 20%, while the legitimate control
still deliberates and still approves 15/15. That is the combination a comparison
needs: a baseline that fails often, and benign work that survives.

The manipulation is partial — it does not force thinking off everywhere, and
which prompts stop deliberating is itself prompt-dependent. A registered study
must therefore report the realised zero-thinking rate per arm rather than assume
it.

These probe calls are **not evidence** and live in
`study-runs/deliberation-probe/`, never in `results/`. A registered comparison
uses fresh calls.

## Standing limits

The subgroup analysis conditions on a post-treatment variable that the prompt
influences, using a cut chosen after the data were seen. It is hypothesis-generating.
It does not establish a story advantage, and it earns no risk decrement. The
prediction it makes is testable directly by making deliberation an independent
variable rather than an observed one; see the finding document.
