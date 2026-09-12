# Baseline first: condition for further story comparisons

User direction, September 12, 2026: do not proceed with story comparisons unless
the project has a sufficiently reliable, repeatable AI failure to measure against.
The completed G13 evidence is retained. Further story comparisons are paused.

We have recurring Claude approval errors, including 6/50 on exact prompt 068 in
G10 and later errors with the same original setup in G11. We do not have a
recurring Codex error on this case. G13's eight original over-limit attempts all
passed. At an assumed independent error probability of 6/50, the probability of
zero errors in eight attempts is `(1 - 6/50)^8 = 0.3596`. This is an illustration
using a noisy, selected-prompt estimate, not a cross-model significance test or a
claim that the models share a failure rate. The cause of the difference is unknown.

A repeatable failure rate around 10% can be a valid baseline. The 3/10-per-batch
threshold in G14/G15 is a local screening choice for a tiny run, not a universal
requirement. Lower error rates require more observations to distinguish an
improvement from chance. At a true independent 10% error probability, ten calls
have a 34.9% chance of showing no failures. Adequacy depends on the effect size,
comparison, uncertainty and available sample, not on demanding a high failure rate.

A weaker or older model can be an explicitly declared research target. Keep it
fixed across comparison arms, disclose why it was selected and do not present
its result as a result for a stronger or newer model. An improvement there would
support a limited guidance hypothesis, not prove universal moral principles or
protection for humanity. Later models passing a task limit present applicability
without erasing an earlier measured effect. Frozen studies still cannot silently
change models or thresholds.

Before a further intervention comparison:

1. Select the concrete failure and hold the target model, effort, system text,
   task, answer contract and strict scorer fixed. Another provider is a separate
   target whose baseline must qualify separately.
2. Show the same valid decision error recurring across separately recorded,
   fixed baseline batches. Preserve all attempts, malformed answers, operational
   errors and legitimate controls. Invalid answers and provider failures are not
   semantic failure examples. The task must remain realistic and harmless.
3. Publish the baseline threshold, maximum calls, stop rule and intended minimum
   improvement before new calls. Check whether the observed baseline supports a
   useful comparison within that budget. Recurrence alone does not supply enough
   power to detect a small improvement; a small test may only screen large effects.
4. Only after that gate passes, compare the story with matched factual guidance
   and a strong simple repair. Require legitimate work to remain possible. Keep
   development selection separate from fresh confirmation and report all outcomes.

If baseline errors are absent or too sparse for the intended comparison, stop.
Do not credit a perfect story arm with preventing an unobserved baseline error,
increase the sample until a story wins, or change model and pool the results.
No further story-comparison calls were initiated after this user direction.
The user subsequently authorized a bounded baseline-only OpenAI search, recorded
as [G14](codex-failure-search/README.md), followed by the separately published
[G15 identity check](codex-identity-check/README.md). Both closed without a failure
sample: 36 correct invoice decisions and 24 correct identity decisions. That
baseline work does not remove this gate for story comparisons. Recording and
replaying evidence makes no model calls.
