# How donated runs are handled

Published September 12, 2026, **before any submission has been accepted**. These
rules exist so that inviting contributions cannot damage the thing contributions
are meant to help. If they need to change, they change in a commit that predates
the next accepted submission, never afterwards.

## Donated runs are a separate pool

A submission produced by `run_pack.py` is **unverified screening data**. It lives
in its own pool, labelled with the donor's chosen attribution, the model, the date
and the pack fingerprint. It is never merged into the recorded experiment results,
and it never appears inside a study's counts.

The runner writes this into every submission it produces:

```json
"status": "unverified_donated_screening",
"qualifies_baseline": false,
"settles_comparison": false
```

## What a donated run can do

- **Nominate a configuration.** A model that approves what the owner forbade on
  these traps is a candidate target worth the project testing properly.
- **Contribute negative evidence.** A model that handles all of them correctly is
  informative in the same way G16 was, and is published as such.
- **Show breadth.** The exposure term in [the reduction model](../docs/reduction-model.md)
  is an assumption partly because this project has run one family of models on one
  account. Many machines and many providers is the only realistic way to change that.

## What a donated run cannot do

- It cannot qualify a baseline. [The baseline gate](../experiments/BASELINE-GATE.md)
  requires the same error recurring across separately recorded batches that the
  project ran itself, on a fixed target configuration.
- It cannot settle, strengthen or weaken a comparison between guidance arms.
- It cannot move the earned figure in the reduction model. Only a preregistered
  comparison does that, and a donated screen is not one.
- It cannot be cited as a result of the model's vendor. It is one person's run,
  on one machine, through whatever transport they had.

A nominated configuration becomes evidence only when **the project re-runs it
under a registered protocol**. The donation is the lead, not the finding.

## Verification, and its limits

Every submission is checked for: a pack fingerprint matching a published pack, a
complete set of case identifiers, provider metadata present on each response, and
internally consistent scoring when the published rule is recomputed from the raw
answers. A submission failing any of these is not accepted.

None of that makes a submission trustworthy in the way a project-run batch is. A
donor can edit a file. The checks catch mistakes and mismatched packs, not a
determined fabrication, and the pool rules above are what actually contain that
risk. We would rather say this plainly than imply an attestation we do not have.

## Contradictions are published

A donated run that contradicts this project's own results is published with the
same prominence as one that supports them. A donor who finds that a story arm
makes things worse, or that the traps catch nothing anywhere, has given the
project exactly what it asked for.

## Privacy and terms

The runner records an allowlist of response fields and drops provider session and
account detail. Donors are asked to read their submission file before sharing it.
Contributors run their own tools on their own machines under their own provider
terms; this project neither receives nor stores credentials, and asks nobody to
automate an interface their provider does not permit them to automate.

## This authorizes no experiment

Publishing a pack and a runner does not start a study, resume a stopped one, or
alter [AGENTS.md](../AGENTS.md). The project's own calls remain governed by the
baseline gate and by registered protocols published before any call.
