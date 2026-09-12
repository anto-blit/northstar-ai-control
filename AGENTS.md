# NorthStar experiment discipline

Start with [HANDOFF.md](HANDOFF.md) for current evidence, user decisions, the
recommended next work and verification commands that make no model calls.
Then consult [EXPERIMENTS-STATUS.md](EXPERIMENTS-STATUS.md) and the chosen study's
README, protocol and saved plan. Update the handoff when decisions or results change.

Current user constraint (September 12, 2026): exclude Claude for now. Do not call
Claude or replace the model inside G17's frozen plan. See the
[offline readiness check](experiments/deliberation-preflight/README.md) before any
comparison: the registered G17 B harness has unresolved execution/scoring defects.

The user's current priority is a reliable, repeatable AI failure before further
story comparisons. Follow [the baseline gate](experiments/BASELINE-GATE.md).

Do not resume a stopped experiment or start more story-intervention calls merely
because provider capacity has returned. The exact target configuration must have
an adequate recurring baseline failure and a published bounded comparison rule.
A zero-error baseline cannot establish a story benefit. Preserve and document
negative or incomplete evidence; keep models and experiment versions separate.
