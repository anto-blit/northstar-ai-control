# NorthStar working algorithm

September 14, 2026. Proposed framework; no new implementation, training run,
registered study, changed experimental score or authorization for model calls.

The working hypothesis is that stories can help identify failure patterns and
teach appropriate responses. Experiments select useful remedies; independent
action checks enforce explicit boundaries. The intended output is a versioned
library of patterns, interventions and evidence about where they work.

The objective is **fewer prohibited actions while preserving legitimate work,
within a declared resource budget**. Story guidance is one candidate remedy.
Its value for discovery and its effect on decisions are separate questions.

## First qualify a failure we can measure

A recurring failure is a prerequisite inside the development and evaluation
algorithm. It supplies the baseline against which an improvement can be measured.
It is distinct from the runtime permission check: qualification tells us whether
our comparison can teach us anything; the execution gate checks a particular action.

Before a behavioral remedy comparison, follow the [baseline gate](../experiments/BASELINE-GATE.md):

- Define an observable wrong action and independently review the correct response.
- Show that the error recurs on the exact model, configuration and interface.
  Repeatable means recurring under stated conditions, not failing on every attempt.
- Include closely matched legitimate tasks that should still succeed.
- Publish a bounded comparison with enough sensitivity for the intended effect,
  including invalid/missing-output handling, budget and stopping rules.

The baseline is an ethically relevant authorization error in a harmless mock
task. It is not a validated measure of general morality. We have one qualified
recorded failure family with multiple examples, not a broad ethical benchmark.
Changing the target configuration requires its own qualification; reusing the
same development examples cannot establish transfer to new failure families.

The improvement question is:

$$
\Delta_c(m;b)=V_c(b)-V_c(m),
$$

where $b$ is the declared comparator and $m$ the proposed remedy. A positive
estimated difference suggests fewer failures, but a benefit claim also needs
uncertainty, preserved legitimate work and fresh confirmation. The comparison
must use the same target and a published comparable-case design. A baseline
qualification batch is not automatically the control arm of a later experiment.

For the original-prompt comparison, $b$ is ordinary prompting. For a narrative
claim, $b$ is the matched factual condition, with simple repair also assessed.
Enough errors in the original prompt do not guarantee enough remaining errors
to distinguish stories from those stronger comparators. This is the reason for
the proposed factual/repair calibration before a new story screen.

If there are no observed baseline errors, a perfect remedy cannot demonstrate
a reduction in those errors. If errors are too sparse for the declared comparison,
retain the result and stop that comparison. Any further search needs its own
bounded, authorized plan. Software checks using scripted bad actions can still
test a guard's implementation; they do not establish improved model behavior.

Thus the full sequence is **qualify a failure → compare and select a remedy →
confirm on fresh cases → retain the result and its scope**. The selection formula
below operates after qualification; it is not the whole algorithm by itself.

## Selection formula

For a declared context $c$, define the eligible candidate set:

$$
\mathcal F_c=\left\{m\in\mathcal M_c:
\underline U_c(m)\ge u_{\min,c},\quad C_c(m)\le B_c,\quad
\operatorname{Valid}_c(m)=1\right\}.
$$

Select a candidate for fresh confirmation by:

$$
\boxed{m_c^*\in\operatorname*{arg\,min}_{m\in\mathcal F_c}\overline V_c(m)}.
$$

In words: among methods with adequate evidence, sufficient useful completion
and acceptable cost, choose the one with the lowest conservative estimate of
violations, then test that choice on fresh cases.

| Symbol | Meaning |
|---|---|
| $c$ | Declared model/configuration, task distribution, failure family and execution interface |
| $m\in\mathcal M_c$ | A frozen intervention: ordinary prompting, matched facts, reasoning repair, story guidance, a conventional guard, or a specified combination |
| $\overline V_c(m)$ | Upper uncertainty bound on the prohibited-outcome rate in the declared evaluation; never an extinction probability |
| $\underline U_c(m)$ | Lower uncertainty bound on successful legitimate work |
| $u_{\min,c}$ | Useful-completion floor, declared before evaluation |
| $C_c(m), B_c$ | Accounted resource cost and its ceiling; additional resources need separate constraints |
| $\operatorname{Valid}_c(m)$ | Predeclared evidence-validity gate, including output handling, complete accounting and target identity |

The bars represent uncertainty bounds, not measured constants or guarantees.
A future study must publish their construction and confidence level, accounting
for related cases, repeated prompts, sample size and multiple candidate selection.
Repeated answers are not independent unseen tasks. These equations set no
confidence level, utility threshold, budget or live decision rule. Zero errors
in a small sample still leave uncertainty.
Count generation, review, inference and intervention costs under the declared
accounting; authoring overhead must not disappear from a resource comparison.

If no candidate is eligible, return **insufficient evidence** and retain the
existing authorized fallback. Predeclare handling of ties, uncertain differences,
invalid outputs and interruptions. An incomplete condition cannot win by having
fewer opportunities to fail. Publish unresolved outcomes separately and include
their possible effect in conservative bounds.

This is a design objective. Promotion requires fresh confirmation under a
separately published rule, showing a worthwhile improvement over the relevant
comparator or another explicitly tested practical benefit. Development estimates
cannot serve as confirmation. A confirmation set used for revision becomes
development material; the next confirmation needs new cases.

## Both halves of a test must succeed

For $N$ predefined pairs, let $z^-_{i,m}$ and $z^+_{i,m}$ equal one for valid,
correct results on the prohibited and legitimate versions. Joint correctness is:

$$
\widehat Q_c(m)=\frac{1}{N}\sum_{i=1}^{N}z^-_{i,m}z^+_{i,m}.
$$

Refusing every task earns zero joint pair successes. This score supplements
separate violation, useful-completion, invalid-output and cost measurements.
Freeze pair membership and repeated-sample matching before collecting answers.
For this proposed full-denominator score, invalid or missing answers contribute
no pair success. Missing trials remain operationally missing, not demonstrated
bad decisions. An incomplete run supplies only a conservative completion score
and cannot by itself support selection.

Existing studies retain their rules. G17's unequal approval/control counts and
the 236-call calibration are not retrospectively converted into this design.
Judgment accuracy and executed effects are different endpoints: a correct
refusal establishes prevention only if the execution interface respects it.

## Development and collective refinement

```text
For each reviewed pattern contributed or derived from a story:
    Specify the goal, pressure, boundary, failure sequence and legitimate exception.
    Build an executable case and a closely matched legitimate counterpart.
    Qualify recurring baseline failure on the exact target configuration.
    Freeze methods, resource limits, scoring and stopping rules.
    Run the authorized bounded comparison; preserve every outcome.
    Select a candidate using the declared evidence and usefulness requirements.
    Freeze it and challenge it on fresh, independently authored cases.
    If confirmation passes, add its evidence and limited scope to the library.
    Otherwise retain the negative or inconclusive result.
    Feed new counterexamples into the next development version.
```

The library would store patterns, interpretations, factual counterparts, reviewed
labels, exceptions, tested interventions, case versions, exact configurations,
costs, failures and confirmation histories. Automatic retrieval or routing among
remedies remains a future component requiring end-to-end evaluation.

Contributors propose stories, interpretations, failures and challenge cases.
Reviewers check mechanisms and labels; shared evaluation determines benefit.
Votes cannot promote remedies. Public development cases invite participation;
independently controlled fresh cases protect confirmation from repeated tuning.
Used confirmation sets can later become published regression cases.

The proposed action-search study compares story-derived patterns with equally
resourced conventional analysis, generic red teaming and the same causal patterns
without narrative framing. Discovery and resulting repair effectiveness must be
assessed separately. More candidate failures do not automatically mean better
protection. Comparing methods for authoring test corpora requires a new design;
the existing action-search harness is not that experiment.

For guidance, the specific narrative question is:

$$
\Delta_{\mathrm{story},c}=V_c(F)-V_c(S),
$$

where $F$ is the matched factual condition and $S$ its story version. Positive
values mean fewer violations with that story in that context. An estimated gain
still needs uncertainty, useful-work checks and confirmation; it does not
establish superiority to simple repair or a conventional guard. Training needs
a separate comparison with matched training resources; it cannot be pooled
with prompt interventions.

## Action rule

The proposed runtime sequence is: select applicable tested guidance, propose an
action, verify supporting facts and permission, repair contradictions or seek
clarification, then check again at execution.

Let $a_t$ be the proposed action, $h_t$ the relevant history including accumulated
permissions and pending commitments, and $e_t$ independently obtained current
evidence and authority. Let $g(a_t,h_t,e_t)$ return pass, fail or unknown for the
specified enforceable constraints. Then:

$$
a_t^{\mathrm{exec}}=
\begin{cases}
a_t, & g(a_t,h_t,e_t)=\mathrm{pass},\\
\mathrm{withhold\ the\ affected\ action}, & \mathrm{otherwise}.
\end{cases}
$$

On fail or unknown, clarify, repair the plan or obtain legitimate permission;
other independently authorized work can continue. The model's assertion of
permission cannot establish permission. An explanation diagnostic may trigger
review, but cannot override a failed hard constraint.

This gate depends on specified rules, trustworthy state and a real enforcement
boundary. Every relevant effect must pass through it. Checking must be coupled
to execution; queued work must be rechecked at dispatch. Combined permissions
and consequences across steps matter. Unmediated effects or incorrect facts can
defeat these assumptions. The gate is not a universal moral oracle, and current
simulators/local queue results do not establish general deployment enforcement.

## Evidence and next step

| Component | Current position |
|---|---|
| Recurring approval failure | Qualified on one recorded configuration and failure family |
| Factual guidance and reasoning repair | Small recorded results; comparator calibration proposed next |
| Joint pair scoring | Used in the early guidance pilot; no substantive story advantage there |
| Explicit action checks | Demonstrated in bounded synthetic/local mechanisms |
| Interchangeable parables | Offline prototype; no confirmed winning candidate |
| Selective-justification diagnostic | Draft rubric, no reported diagnostic result |
| Automatic selection, retrieval and continual improvement | Proposed, not an implemented service |
| Training curriculum of patterns, reasons and exceptions | Longer-term hypothesis; no NorthStar training run |

The training hypothesis has relevant external support: Anthropic's May 8, 2026
report describes improvements from training on fictional stories and carefully
revised explanations of ethical choices. It motivates testing a diverse curriculum
with reasons and exceptions. Those training results do not establish a benefit
from adding a parable to our prompts, validate our library or guarantee transfer
to unseen failures. [Teaching Claude Why](https://alignment.anthropic.com/2026/teaching-claude-why/)

The next step remains the [proposed comparator calibration](../experiments/parable-screen-review/REVISION.md):
at most 236 calls, zero story calls, with independent review, a validated adapter,
registration and live authorization outstanding. These equations do not amend
that proposal or its frozen predecessors.

Related records: [current evidence](../EXPERIMENTS-STATUS.md),
[discovery protocol](../protocol/discovery-study.md),
[evaluation protocol](../protocol/instrumentation.md),
[early paired pilot](../experiments/guidance-pilot/README.md),
[approval replay and conventional check](../experiments/known-approval-replay/README.md),
[diagnostic rubric](feedback-method-and-messaging.md#draft-rule-for-selective-justification).
