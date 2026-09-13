# NorthStar@Home

Run a published screening pack on a model you already have access to, on your own
machine, and see whether it approves what the owner forbade.

Twelve cases: six authorization traps and their six legitimate twins, taken
unchanged from the published [G16 trap screen](../experiments/openai-trap-screen/README.md).
Each trap is built so the tempting wrong reading lands just on the wrong side of
a stated limit. The twins exist so that a model which simply refuses everything
cannot look safe.

**Nothing is transmitted.** The runner writes a file. You read it, and decide
whether to share it. No credential ever reaches this project.

## Run it

```bash
cd northstar_at_home
python run_pack.py packs/screen-001.json                # dry run: prints the plan, calls nothing
python run_pack.py packs/screen-001.json --confirm      # 24 calls (12 cases x 2 repeats)
```

The default transport is the `claude` CLI you have already authenticated, invoked
the way this project invokes it: no tools, no session persistence, no repository
context. Any other provider works through a command you supply:

```bash
python run_pack.py packs/screen-001.json --transport command \
    --command "your-provider-cli --model some-model --stdin" --confirm
```

The command must read the prompt on standard input and print the answer. If it
prints JSON with a `result` field, that field is scored; otherwise the whole of
standard output is.

Useful flags: `--repeats N` (default 2), `--model`, `--effort` (default `low`,
because low deliberation is where every recorded failure in this project lives),
`--timeout`, `--executable`, `--out`.

## What you get

A summary on screen, and a submission file under `submissions/`:

```
3 wrong approvals in 12 over-limit attempts · 12/12 legitimate controls correct
· 0 invalid · 0 service errors
```

The file records the pack fingerprint, your requested model and effort, the raw
answers, and the score for each case under the pack's published rule. It records
an allowlist of response fields only, so provider session and account detail stays
on your machine. Read it before you share it.

## What happens to it

Read [POOL-RULES.md](POOL-RULES.md) — it was published before any submission was
accepted. In short: donated runs are unverified screening data in their own pool.
They can nominate a configuration for the project to test properly, and they can
stand as published negative evidence. They cannot qualify a baseline, settle a
comparison, or move any term in [the reduction model](../docs/reduction-model.md).
A donated run that contradicts this project's results gets published too.

To share one, open an issue with the file attached. GitHub requires an account and
submissions there are public.

## Before you run it

Use an account you hold, under your provider's terms, through an interface you are
permitted to use programmatically. A subscription's monthly or weekly allowance is
generally usable through the provider's own CLI or app, which is what this runner
drives; it is not a licence to automate a web interface. If you are unsure, check
your provider's terms first. The tasks are harmless mock approvals — no money
moves, nothing is booked, and no tool is enabled.

## Maintaining the pack

```bash
python build_pack.py                      # regenerate packs/screen-001.json from the G16 cases
python -m unittest test_run_pack          # 14 offline tests; no model calls
```

`build_pack.py` records the fingerprint of its source cases, and `run_pack.py`
refuses a pack whose cases do not match its recorded fingerprint, so an edited
pack cannot be run by accident or passed off as a published one.
