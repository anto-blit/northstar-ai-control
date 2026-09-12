# A first collection of lessons from stories

This collection turns six Aesop fables into inspectable, conditional guidance.
It preserves the original source passages, new retellings, factual counterparts,
structured interpretations, reasons, exceptions, disagreements and runnable rules.

**It is a provisional project interpretation. No independent human review has
occurred. It does not encode all morality or establish that stories improve AI.**

| Story | Adopted lesson | Interpretation we explicitly limit or reject |
|---|---|---|
| The Fox and the Stork | Consider a recipient's actual needs | Retaliatory exclusion |
| The Boys and the Frogs | Consider effects on those harmed | Treating the actor's enjoyment as sufficient justification |
| The Shepherd's Boy and the Wolf | Report evidence honestly | Permanently ignoring someone because of past false reports |
| The Wolf and the Lamb | Power does not justify coercion | Treating the predator's success as moral approval |
| The Mice in Council | Check execution and who bears its burden | Treating an appealing plan as implemented protection |
| The Lion and the Mouse | Consider need and relevant capability | Making basic consideration depend on repayment |

Source: V. S. Vernon Jones's 1912 translation,
[Project Gutenberg 11339](https://www.gutenberg.org/ebooks/11339), listed as public
domain in the USA. The six source passages were read before Codex authored the
annotations. New retellings are labeled as such. This single tradition does not
stand in for cultural consensus. Extensions beyond the text are recorded.

## Run the algorithm

From the repository root, Python 3.10+, no extra dependencies:

```bash
python -m northstar_ethics compile
python -m northstar_ethics demo
```

For a supplied action, save this as `action.json` and run
`python -m northstar_ethics assess action.json`:

```json
{
  "action_type": "share",
  "facts": {
    "authorization_valid": false,
    "consent_respected": true,
    "serious_harm_avoided": true,
    "coercion_avoided": true,
    "unresolved_value_conflict": false,
    "recipient_can_use": true
  }
}
```

This returns BLOCK with a trace identifying current authorization as the failed
boundary. Missing relevant facts return REVIEW. Known violations override an
unresolved issue, so review cannot silently authorize a prohibited action.
Supported action types are share, report, assign and help; arbitrary tool calls
and executable expressions are not accepted.

**The caller supplies the factual judgments.** The engine does not determine
whether a real action is harmful, whether consent is valid, or whether a claim
is supported. A model's self-assurance is not a trusted fact. This is a transparent
compiler and bounded rule checker, not automatic moral extraction, an independent
ethical judge, or a validated containment system.

The operational permission and conflict rules are recorded separately from the
story interpretations. Human review of interpretations and factual mappings is
needed before making any deployment claim; the catalog is explicitly marked
`deployment_approved: false`.

See [G5's comparison](../experiments/story-distillation/README.md) for an actual
model test of stories, factual examples and distilled guidance. A successful
software check alone does not establish a behavioral benefit.
