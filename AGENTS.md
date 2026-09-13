# NorthStar experiment discipline

Start with [HANDOFF.md](HANDOFF.md) for current evidence, user decisions, the
recommended next work and verification commands that make no model calls.
Then consult [EXPERIMENTS-STATUS.md](EXPERIMENTS-STATUS.md) and the chosen study's
README, protocol and saved plan. Update the handoff when decisions or results change.

Current user direction (September 12, 2026, superseding the same day's exclusion):
Claude is available again, to this project and to contributors. No model is
excluded. Lifting that constraint authorizes no calls by itself. Do not replace
the model inside G17's frozen plan; a changed target is a new registered study.
See the [offline readiness check](experiments/deliberation-preflight/README.md)
before any comparison: the original G17 B harness is preserved with its defects.
The [corrected v2 machinery](experiments/deliberation-comparison-v2/README.md) is
verified with offline fixtures only, and no live comparison is registered against
it. Registering one, with its budget, scoring and stop rule published first, is
the outstanding step.

The user's current priority is a reliable, repeatable AI failure before further
story comparisons. Follow [the baseline gate](experiments/BASELINE-GATE.md).

Do not resume a stopped experiment or start more story-intervention calls merely
because provider capacity has returned. The exact target configuration must have
an adequate recurring baseline failure and a published bounded comparison rule.
A zero-error baseline cannot establish a story benefit. Preserve and document
negative or incomplete evidence; keep models and experiment versions separate.
