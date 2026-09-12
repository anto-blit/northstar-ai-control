# G17 B readiness check and the current provider constraint

September 12, 2026, after commit `885358e`. **Zero provider calls.**
The user requested proceeding only while excluding Claude for now. G17 B is
registered for Claude, so it was not launched or silently assigned another model.
This is an engineering check, not a new model experiment or a story result.

## What can run without Claude

The qualified G17 baseline applies to `claude-sonnet-5` at low effort. The recorded
G13/G14/G15/G16 OpenAI runs supplied no qualified baseline. Their saved responses
can be replayed offline, but replay cannot measure a new story intervention.

Read-only checks found Codex CLI 0.154.0 installed; its cached listed models offer
`low` as their lowest reasoning effort. No OpenAI, Gemini/Google, OpenRouter or
Azure OpenAI key was present in the process or persistent user environment. No
project-root `.env*` file, Ollama, LM Studio CLI or Gemini CLI was found. These
checks establish this session's visible configuration, not the absence of an
account elsewhere. No credential value was printed or copied.
The user then confirmed that no alternative API account or endpoint is available
at this time. The live comparison is therefore paused under the Claude exclusion.

An API route is a possible next target. Official OpenAI documentation lists
[`none` for GPT-5.5](https://developers.openai.com/api/docs/models/gpt-5.5), whereas
the [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
does not list `none` for `model_reasoning_effort`. Account access remains
unverified. A new provider/model/setting needs a separate published baseline
qualification before any story comparison. No API study is registered here.

## The registered G17 B harness is not ready

[The recorded check](../../results/deliberation-preflight/report.json) reproduces
these defects without invoking a provider or changing the frozen sources:

| Check | Observed result | Consequence |
| --- | --- | --- |
| Stage B dispatch | `materials.REQUESTS` has A and A2 only; B raises `KeyError('B')`. | The documented B run cannot start. |
| Repair answer contract | A correct JSON answer with `reason` then `decision` is invalid under all three scorers. | Arm R cannot be evaluated fairly; parser rejection is not evidence of a successful repair. |
| Empty/partial reporting, after isolating dispatch | Missing observations lack `first_object`, causing a `KeyError`. | Interrupted or unstarted comparisons cannot be reported correctly. |
| Complete reporting, after isolating dispatch | Comparison rules use `min_wrong_approvals=None`; baseline report logic compares a count with `None`, causing a `TypeError`. | The registered per-arm comparisons are not implemented by this report. |
| Stop rule, with dispatch/report isolated and writes intercepted | A synthetic service error is followed by a second synthetic transport invocation. | The loop does not enforce stopping on the first quota/service error. |

Registered source hashes, inherited hashes and all 320 request records match
their current sources. This is not source drift. The existing twelve G17 tests
pass but do not cover executing or reporting B, the repair arm's required key
order, or the service-error stop path.

The checks explicitly use synthetic answers. For the stop probe, both transport
and disk writes are replaced in memory. No synthetic answer is stored in a model
response directory. `ready: false` records this frozen version's audit verdict;
the script is not a general readiness certifier for a future implementation.

## What needs doing before a live comparison

Prepare a separately versioned implementation and publication. Preserve G17 A,
A2 and B's original plans and all actual responses. The replacement needs:

1. A selected, accessible non-Claude target and its own qualified baseline while
   the user's exclusion remains in force.
2. Scoring that recognizes each arm's actual output contract, plus a precisely
   described consumer policy for conflicting decisions. Acting on the first
   object is a stated consumer assumption, not proof that every downstream
   system acts before a correction.
3. Working four-arm dispatch, per-arm denominators and the prespecified paired
   comparisons, with malformed answers, service failures and missing calls kept
   visible. A repair-arm invalid answer cannot be treated as a successful repair.
4. An enforced operational stop, partial-report generation and evidence
   preservation, exercised with injected errors before any paid call.

Also keep the low-effort causal claim narrow. The recorded association with zero
reported thinking tokens does not prove the model does no internal computation,
and an unconditional low-effort comparison does not isolate the effect of stories
specifically among replies that do not deliberate.

## Reproduce offline

```powershell
py experiments/deliberation-preflight/check.py --verify results/deliberation-preflight/report.json
py -m unittest discover -s experiments/deliberation-comparison -p test_run.py
```

The first command verifies the saved defect report; success means the defects
reproduce, not that G17 B is ready. The second reproduces the limited existing
test suite. Neither command calls Claude or another provider.
