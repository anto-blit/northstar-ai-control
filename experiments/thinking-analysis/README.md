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

## Standing limits

The subgroup analysis conditions on a post-treatment variable that the prompt
influences, using a cut chosen after the data were seen. It is hypothesis-generating.
It does not establish a story advantage, and it earns no risk decrement. The
prediction it makes is testable directly by making deliberation an independent
variable rather than an observed one; see the finding document.
