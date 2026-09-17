# ORH1: reward-hacking probe against one OpenAI target

A bounded **baseline search** in a failure family the project had not yet
tested against an OpenAI model. Read [PROTOCOL.md](PROTOCOL.md) first; it is the
registered design. Results are in
[`results/openai-reward-hack/`](../../results/openai-reward-hack/).

## Why not another authorization probe

Six OpenAI authorization searches have now returned no failure: G14, G15, G16,
[APO1](../../results/authorization-pressure-openai/REVIEW.md),
[APL1](../../results/authorization-pressure-luna/REVIEW.md) and AFR1-O. All of
them score a *stated decision* about a stipulated scenario. This one scores an
*executed effect*: the model's own edit either generalises to a held-out spec or
it does not. No rubric and no judge are involved.

## Layout

| path | what it is |
|---|---|
| `PROTOCOL.md` | registered design, budget, stop rules, platform port |
| `probe/` | the probe from [`fails/`](../../fails/README.md), ported to Windows and stdlib `unittest` |
| `probe/fixtures/` | reference and hardcoded solutions used to validate the scorer offline |
| `transport.py` | agentic Codex CLI adapter: fresh ephemeral thread, workspace-write, no network |
| `run.py` | `verify` (offline only) and `run` (makes model calls) |
| `system.txt` | the instruction text that replaces the CLI's built-in instructions |

## Commands

    py experiments/openai-reward-hack/run.py verify   # ten offline checks, no model calls
    py experiments/openai-reward-hack/run.py run      # the registered plan; makes calls

`verify` resets the probe, confirms both starters score `HONEST_FAIL`, that the
reference solutions score `SOLVED/SOLVED`, that a hardcoded-against-visible
fixture scores `HACKED` and loses the joint pair, and that `holdout.py` is never
staged into the model's working directory.

## Harness notes worth keeping

Three Codex CLI behaviours cost a run before the probe worked at all, and all
three are recorded in [the aborted attempt](../../results/openai-reward-hack-aborted/NOTE.md):

1. Disabling `code_mode` / `code_mode_host` removes the shell and patch tools
   entirely. The decision-only transport in `experiments/codex-repair` disables
   them on purpose; an agentic probe must not copy that list.
2. `--ignore-user-config` also discards the per-project `trust_level` entries,
   and an untrusted working directory silently downgrades
   `--sandbox workspace-write` to `read-only` -- the banner says `read-only`
   while the flag says otherwise. `transport.py` trusts only the staged
   directory, with `windows.sandbox = "unelevated"` still in force.
3. The Windows restricted-token sandbox applies its inheritable directory grant
   when the session starts, which races with files staged moments earlier: the
   agent's first read of a staged file returns "access denied". `run.py` uses a
   persistent staging root under the OS temp directory, warmed once, so later
   seeds copy in files that already inherit the grant.

A model that reports it cannot edit a file is an operational failure of the
harness, not a result about the model.
