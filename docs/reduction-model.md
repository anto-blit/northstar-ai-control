# The reduction model: what each step could be worth

Status: a stated theoretical model, published September 12, 2026. It is not a
measurement, a forecast, or a claim that NorthStar has reduced anyone's risk.
Its purpose is to make the project's optimism checkable: if we think our work
matters, we should be willing to write down how much, under which assumptions,
and what evidence would move each term.

## Why a model at all

The danger is a possible future outcome, so the argument for working on it is
necessarily theoretical. That is not an excuse for vagueness. A theoretical
argument can still be explicit, parameterised, and falsifiable in its parts,
and it can be attached to the empirical results we do have. The alternative —
a fixed 10% displayed beside a pile of passing tests — invites the reader to
assume a connection we have never stated.

## The model

Let **R₀** be the reference probability of the catastrophic outcome. The project
uses 10%, the lower endpoint of Hinton's subjective range, with the full spread
of current sourced statements in [risk-estimates.md](risk-estimates.md). Nothing
below depends on 10% being correct; it is a display anchor.

The pathway this project addresses is decomposed into three factors:

```
addressable reduction  =  R₀  ×  s  ×  e  ×  a
```

| Term | Meaning | Default | Standing |
|---|---|---|---|
| **s** | Share of catastrophic pathways that run through an AI system taking an irreversible action its principal forbade, or would have forbidden if asked | 0.25 | Assumption. No measurement exists. |
| **e** | Share of those overrides that a validated safeguard would actually prevent | 0.40 | Partly anchored; see below. |
| **a** | Share of relevant deployed systems that would adopt such a safeguard | 0.15 | Assumption. No data. |

With the defaults: 10% × 0.25 × 0.40 × 0.15 = **0.15 percentage points**. That is
the whole prize on the table under these assumptions — from 10.00% to 9.85%.
Writing it down is deliberate. It is a small number, and a reader who thinks it
is too small is having exactly the argument this model exists to enable.

## What is empirical, and what is not

Only **e** touches recorded data, and only at its edges.

- The scripted post-stop comparison at zero monitor errors records 400/400
  prohibited outcomes with the starting control and 0/400 after the repair.
  That is an upper bound from fixed scripted trials, not a field rate.
- G17 stage A2 records 10 wrong approvals in 32 fresh over-limit attempts on the
  recorded Claude target, with 12/12 legitimate approvals preserved. That
  establishes the failure is real and recurring, not that a safeguard removes it.
- G16 found no failure in 84 recorded OpenAI decisions on its configuration.
  A failure that does not appear everywhere argues for a lower **s**, not a
  higher one.
- The persistent queue pilot ties a conventional transactional check against
  NorthStar's epoch fencing. If ordinary engineering achieves the same result,
  the share of **e** attributable to *this project* may be near zero. This is
  the single most important open question in the model.

**s** and **a** have no empirical support of any kind today. They are judgments,
displayed as adjustable inputs so that a reader can substitute their own.

## Earned versus available

The model produces two quantities, and the difference between them is the point.

- **Available**: R₀ × s × e × a under the stated assumptions. 0.15 pp today.
- **Earned**: the share of that which rests on validated terms. **0.00 pp today**,
  because no term has been validated by a registered comparison.

A step earns part of the available reduction only when a preregistered
experiment with published scoring supports the term it targets. Passing tests,
completed milestones, repaired machinery and offline checks earn nothing here;
they are how the project becomes *able* to run such an experiment. This is the
same rule as [the limits on risk claims](evidence-progress.md#limits-on-risk-claims),
expressed as a number instead of a paragraph.

New evidence may move a term in either direction. If the four-way comparison
shows stories tie ordinary instructions again, **e** falls for the narrative
approach specifically, and the earned figure stays at zero. That outcome is a
result, not a failure of the model.

## What would move each term

| Term | What would raise it | What would lower it |
|---|---|---|
| **s** | Documented real incidents where an agent crossed an explicit principal limit with consequence | More G16-style screens finding no failure across models and configurations |
| **e** | A registered comparison where a guidance condition beats matched controls on a qualified baseline, replicated on unfamiliar tasks | Further ties with conventional checks and factual guidance |
| **a** | Adoption by a system whose operators are not this project | A safeguard that costs legitimate work; G17's 12/12 controls exist to watch for this |

## Honesty rules for anything built on this model

1. Label it a model everywhere it appears. Never display the output beside
   recorded results without that label.
2. Never let a slider, a passing test, or a milestone change the **earned**
   figure. Only a registered comparison does.
3. Keep the full spread of outside estimates visible, including the ones far
   below 10%, so the anchor cannot masquerade as consensus.
4. Report the earned figure as 0.00 pp for as long as it is 0.00 pp.
