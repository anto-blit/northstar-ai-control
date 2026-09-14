# Scientific review: calibrate the comparators before the parable search

September 14, 2026. **Offline review, zero provider calls.** The user authorized
review of the scientific design and sensitivity before a live experiment.
This is the preparing assistant's self-review, not independent human review or
another model's independent assessment. It makes no new AI-effectiveness claim.

**Decision: revise the proposed sequence before live execution.** The existing
428-call draft remains a useful, tested offline prototype and a large-effect
screen proposal. It is poorly suited to distinguishing good remedies, and its
whole-study validity requirement unnecessarily couples unrelated candidates.
Keep that published draft and its sources unchanged. The revised next proposal
is comparator calibration: **44 original baseline checks, then at most 192
factual/repair calls, and zero story calls**. This is a proposed 236-call ceiling,
not an authorized or registered run. See [REVISION.md](REVISION.md).

## Findings

| Question | Finding | Consequence |
| --- | --- | --- |
| Are the task answers correct? | All **92 unique scenarios and 428 prompt packets** agree with a separate parser reading the rendered prose. Seven scenarios lie exactly at the inclusive cap. No overlap with G12-B scenarios was found. | No label correction is needed. This is a second computational check by the same assistant, not independent validation of realism or ethics. |
| Are stories and facts matched? | Cost facts, explicit rule and the correct conditional/guaranteed-credit decisions match. Keeper-specific record/correction instructions appear in both keeper versions. | Comparisons can address these prompt packages. They do not isolate a universal property of narrative. |
| Is there a wording asymmetry? | The seal story says trust required accepting the compliant offer; its facts say the steward may accept it. | Before a future story comparison, make the permission/obligation wording agree in a new candidate version. The existing material stays preserved. |
| Is the original baseline enough to size the comparison? | No. A 65% original error rate does not tell us the residual error rates under facts or repair. | Calibrate those actual comparators on the exact target first. Do not use the original error rate as power for S/F or S/R. |
| Is the whole-study validity gate appropriate? | One invalid seal-story answer vetoes an otherwise unchanged keeper comparison. The script reproduces this from the original selection function. | Future eligibility should apply to the relevant comparison, with conservative handling of unknown answers, rather than unrelated stories. |
| Does a screen nomination establish an effect? | No. Nomination is selected on the same responses used to rank candidates. | Keep screening, fresh confirmation, and cross-family transfer separate. |

The three candidate versions also share the worked numbers and task vocabulary
of this one lesson. A win would show useful prompt guidance for this task family,
not training, broad moral understanding or a ranking of all parables. No
failure has been added merely to make the test broader.

## How much could 32 cases detect?

The following are **hypothetical probabilities**, conditional on all answers
being valid and completed. They use independent case pairs and, when both arms
can fail, independent errors within a case. These are not estimates of today's
model behavior. They also omit the baseline gate, the candidate-selection rule,
utility failures and interruptions, so they are not probabilities of a full
successful screen or of independent confirmation.

| Assumed comparator error | Assumed story error | Paired over-limit cases | Chance of passing raw exact test at 0.05 | Chance with nine-comparison adjustment |
| --- | --- | --- | --- | --- |
| 5% | 0% | 32 | 0.46% | 0.0019% |
| 10% | 0% | 32 | 9.44% | 0.33% |
| 10% | 2% | 32 | 5.55% | 0.18% |
| 20% | 5% | 32 | 27.83% | 4.96% |
| 65% | 30% | 32 | 73.55% | 38.71% |
| 10% | 0% | 128 | 99.07% | 90.29% |
| 20% | 5% | 128 | 94.71% | 78.12% |

The original protocol already labels its p-values diagnostic and its nomination
exploratory. This review does not mistake failure to reach significance for
failure of a screening rule. For example, even a perfect story has only a 39.97%
chance of clearing the four-error factual screen threshold when F's true error
rate is 10%. If D also fails at 10%, its required eight-error reduction against
D can be met in only 1.17% of 32-case samples. Those are separate upper limits on
nomination under those scenarios, not estimates of the actual joint selection
probability. The nominal four-error baseline gate does not guarantee sensitivity
to the screen's eight-error original-prompt improvement requirement.

Under the hypothetical 10%-to-zero improvement, the first integer sample size
to reach 80% raw power is **78 paired over-limit cases**, or **113** with nine
comparisons. For 20%-to-5% with independent errors, the corresponding numbers are
**83** and **132**. These are illustrative first crossings on an integer scan
through 512, not approved sample sizes. Exact-test power is discrete, the assumed
rates are uncertain, and different within-case shared-error probabilities change
the calculation. The saved report includes three association assumptions and
32/64/128-case scenarios; none is inferred from the original baseline alone.

The exact calculation conditions on the number of discordant pairs and uses
a binomial null probability of one half, as implemented by the prototype's
exact test. The numerical code is checked against direct enumeration and a
perfect-story binomial-tail identity. See the primary
[SciPy binomial-test documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html).
The nine-comparison adjustment multiplies each p-value by nine; this controls
the family of those tests without assuming independence between comparisons.
See the primary [R adjustment documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html).

## Output quality should not erase unrelated evidence

Under a hypothetical independent 1% primary-consumer invalid-output probability
per answer, only **2.11%** of 384-answer screens would have every answer valid.
At 0.5%, that probability is **14.59%**. These are illustrations of the gate's
fragility, not measured invalid rates. Even perfect response validity would not
guarantee passing the other gates. The code also reports separate illustrations
for the requirement that all 128 legitimate answers across all arms be correct.

For a future candidate comparison, keep the full planned denominator. A useful
conservative lower bound on improvement is:

`(known comparator wrong approvals - known story wrong approvals - unresolved story outcomes) / planned over-limit cases`

This gives an unresolved comparator no failure credit and treats every unresolved
story answer as potentially wrong. It does not silently turn invalid answers
into semantic failures; raw categories remain separate. Publish that sensitivity
bound alongside actual decisions and complete-pair diagnostics. Operationally
interrupted studies remain incomplete and earn no nomination.

Require the candidate to preserve its legitimate work, but report comparator
and other-candidate utility separately. Passing 16 legitimate cases would still
leave a **17.07% one-sided 95% upper bound** on a constant independent failure
probability, so it cannot certify high real-world reliability. This is an
illustrative binomial bound, not a claim that case difficulty or failures are
actually independent.

## Why the revised next step is useful

The next unresolved prerequisite is whether facts and repair leave enough
repeatable errors for a parable comparison. A bounded calibration can return
useful negative evidence: if simple guidance handles these cases well, defer a
large story search here and consider a separately bounded search for a different
failure family. Sparse or zero errors do not establish that stories are useless
or that the comparator never fails.

If a particular factual condition produces enough valid failures to justify
sizing a comparison, publish a fresh plan with uncertainty around the rates,
its minimum useful effect and a declared budget. A narrative gain against F and
a practical gain against R remain separate findings. Near-perfect R may make
the latter infeasible at a modest budget. A cost advantage would need its own
prespecified accuracy and cost criteria; it is not inferred from a tie.

The [machine-readable revised proposal](../../results/parable-screen-review/revised-plan.json)
contains the exact baseline and comparator packets, a hard call ceiling, the
proposed reported-usage ceiling, stopping rule and conditional interpretation.
It imports no provider adapter and authorizes no calls. It reuses unexecuted
draft packets, not responses; later story selection/confirmation must use fresh
cases and responses. No new comparison inherits G17 B's registration.

## Reproduce without models

```powershell
py -m unittest discover -s experiments/parable-screen-review -p test_review.py -v
py experiments/parable-screen-review/review.py verify
py experiments/parable-screen/run.py check results/parable-screen/draft-plan.json
```

The [saved review report](../../results/parable-screen-review/report.json) binds
its inputs by hash and records all calculations and the design counterexample.
`build` creates new report/proposal files and refuses to overwrite existing ones.
Neither command invokes a model, fetches a provider account, or registers a study.
