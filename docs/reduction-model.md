# The reduction model: what each step could be worth

Status: a stated theoretical model, published September 12, 2026. It is not a
measurement, a forecast, or a claim that NorthStar has reduced anyone's risk.
Its purpose is to make the project's optimism checkable: if we think our work
matters, we should be willing to write down how much, under which assumptions,
and what evidence would move each term.

September 14 clarification: the approval task measures a minor authorization
error in a harmless simulation. Its predictive relationship to serious harm or
extinction has not been validated. All three global factors below are assumptions;
local results do not calibrate their values. See
[what the small failure means](what-the-small-failure-means.md) for the missing
links and the distinction between ethical relevance and a general moral test.

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
| **e** | Share of those overrides that a validated safeguard would actually prevent | 0.40 | Assumption. Local safeguard results do not calibrate catastrophic-risk efficacy. |
| **a** | Share of relevant deployed systems that would adopt such a safeguard | 0.15 | Assumption. No data. |

With the defaults: 10% × 0.25 × 0.40 × 0.15 = **0.15 percentage points**. That is
an illustrative arithmetic result under these assumptions — from 10.00% to
9.85%. Neither number is a measured current risk, and the latter is not a lower
bound on real-world risk. The input choices determine the result.

The goal is zero, and the arithmetic reaches it. Set s, e and a to 1.00 — every
pathway runs through this failure, a safeguard stops all of it, everyone adopts
it — and the reference is removed entirely within this formula. That does not
establish that every catastrophic pathway can be covered or real-world risk
eliminated. The defaults are illustrative judgments, not evidence-based estimates.

## What is empirical, and what is not

Recorded data motivates research on local boundaries. None of it estimates a
global factor in this formula.

- The scripted post-stop comparison at zero monitor errors records 400/400
  prohibited outcomes with the starting control and 0/400 after the repair.
  That is a result in fixed scripted trials, not a field rate or a bound on
  prevention of catastrophic harm.
- G17 stage A2 records 10 wrong approvals in 32 fresh over-limit attempts on the
  recorded Claude target, with 12/12 legitimate approvals preserved. That
  establishes the failure is real and recurring, not that a safeguard removes it.
- G16 found no failure in 84 recorded OpenAI decisions on its configuration.
  This limits generalization from our tasks and targets. These are not sampled
  catastrophic pathways, so the result does not supply a numerical update to **s**.
- The persistent queue pilot ties a conventional transactional check against
  NorthStar's epoch fencing. If ordinary engineering achieves the same result,
  the share of **e** attributable to *this project* may be near zero. This is
  the single most important open question in the model.

**s**, **e** and **a** are unvalidated at the global scale. They are adjustable
judgments. The existence of a local failure or repair is not evidence for the
chosen numerical defaults.

## Earned versus available

The model produces two quantities, and the difference between them is the point.

- **Available**: R₀ × s × e × a under the stated assumptions. 0.15 pp today.
- **Earned**: the share of that which rests on validated terms. **0.00 pp today**,
  because no attributable global reduction has been established. This display
  means no credited reduction, not a measurement of zero actual effect.

A preregistered local comparison can establish a local improvement. Crediting
global reduction additionally requires evidence for the causal connection to
catastrophic outcomes, transfer, coverage, adoption, added value over existing
safeguards, possible new harms and uncertainty. Passing tests, completed
milestones, repaired machinery and offline checks earn nothing here. This is the
same rule as [the limits on risk claims](evidence-progress.md#limits-on-risk-claims),
expressed as a number instead of a paragraph.

New evidence may move a term in either direction. If the four-way comparison
shows stories tie ordinary instructions again, that weakens the local case for
the narrative intervention. It does not determine a global value of **e**; the
credited figure remains zero. The tie is still useful evidence.

## What would move each term

| Term | What would raise it | What would lower it |
|---|---|---|
| **s** | A supported causal account and representative evidence that the covered boundary failures contribute to catastrophic outcomes | Evidence that the proposed causal link is weak or that covered pathways contribute little; ordinary task pass rates alone cannot measure this |
| **e** | Validated prevention that transfers to the relevant consequential settings and adds protection beyond existing safeguards | Failure to transfer, defeats under realistic conditions, or no added protection; local ties alone do not quantify this global term |
| **a** | Adoption by a system whose operators are not this project | A safeguard that costs legitimate work; G17's 12/12 controls exist to watch for this |

## Honesty rules for anything built on this model

1. Label it a model everywhere it appears. Never display the output beside
   recorded results without that label.
2. Never let a slider, a passing test, or a milestone change the **earned**
   figure. A registered local comparison alone cannot change it either; the
   additional global evidence requirements above must be met.
3. Keep the full spread of outside estimates visible, including the ones far
   below 10%, so the anchor cannot masquerade as consensus.
4. Report the earned figure as 0.00 pp for as long as it is 0.00 pp.
