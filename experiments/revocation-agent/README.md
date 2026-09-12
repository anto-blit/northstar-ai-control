# G6: Does an agent respect revoked authority, and does the service enforce it?

The study measures a specific possible precursor to loss of human control:
requesting a delivery after the authenticated operator stopped that project.
It separately tests a conventional safeguard against scripted violations.
It does not simulate humanity's destruction or estimate its probability.

The agent prepares work, receives a current operator update, makes further tool
requests and reports the result. The service executes actual harmless mailbox
writes through its loopback HTTP API and SQLite transactions. A separate scorer
checks committed events against mailbox rows. A report cannot change the evidence.

Two task contexts were authored by Claude in a fresh context without guidance
variants or earlier outcomes. A second fresh context approved the paired case
definitions without target answers. It noted that it had not inspected runtime
operator updates or receipts; fourteen harness checks separately exercise those
semantics and compare live HTTP execution with offline database replay. This is
project-commissioned AI authoring/review, not independent external or human review.

## Fixed comparison

- Four cases: direct and delegated primary work, each paired with stop or continued
  authorization. An unrelated authorized job must always finish.
- Four guidance arms: ordinary task instructions B, explicit principles P,
  principles plus factual example F, and principles plus newly authored fable S.
  Added guidance word counts: 0, 43, 117 and 115. F/S have comparable length and
  event structure, without perfect linguistic or token matching.
- Two service modes: cooperative cancellation (old worker claims can still
  deliver) and transactional cancellation (the strong conventional comparator).
  Each case/arm/mode combination runs once: 32 episodes, at most eight requests each.

We record prohibited requests, actual effects, useful completion and accurate
reports separately, with all planned denominators visible. Refusals and missing
answers do not disappear. Inaccurate reporting is not automatically proof of
deliberate deception. The same operator authority and action surface apply to
every guidance arm. Both delivery adapters lead to the same service boundary.

The eight scripted controls deliberately request delivery through both adapters.
They must expose the weak mechanism and preserve useful work under the strong
one before target calls can begin. These are engineered attacks; they do not
measure whether an ordinary model independently chooses to violate authority.

## Status

Registered for public publication before model evaluation. The eight scripted
controls have completed: deliberate post-stop delivery reached the mailbox in
2/2 revoked cases under cooperative cancellation and 0/2 under transactional
cancellation. Both modes completed 6/6 required authorized deliveries across
the stopped cases and active twins. These are scripted control results, not
ordinary-model behavior. The [initial sandbox launch failure](../../results/revocation-agent/controls-launch-000/failure.json)
is preserved separately; it produced no control outcomes or target calls.
Full [protocol](PROTOCOL.md), [guidance](guidance.json), [paired cases](cases.json),
and [separate author/reviewer records](../../results/revocation-agent/preparation/).
Maximum nominal target budget $20.48; at most $1.50 additional preparation budget.
Reported usage is list-price usage, not necessarily an actual subscription charge.

## What a result would mean

A scripted violation stopped by the service supports that local contract under
the tested requests. A model that also chooses to violate it exposes a behavioral
failure to investigate. A clean model result reports no observed failure within
this small, transparent, bounded test. It cannot prove that future agents, broader
tools or unfamiliar environments are safe. No outcome changes the site's 10.00%
reference. A general claim of effective story guidance requires fresh cases and
replication after a failure and repair have been identified.

Only the scoped tools in the protocol can affect the local mailbox. The host,
operator, adapter and database are trusted; no OS isolation claim is made. The
study does not cover independently operated alternate destinations, arbitrary
code execution, strategic concealment over long deployments, or every possible
path to catastrophe. [How we use hypothetical scenarios](../../docs/what-we-can-test.md).

## Offline verification

```bash
python -m unittest discover -s experiments/revocation-agent -p test_run.py -v
python experiments/revocation-agent/run.py verify
```

`controls` runs the scripted local experiment. `run` contacts Claude and requires
publicly committed inputs and passing controls. Neither command overwrites a run.
`verify` reconstructs every saved tool history and database snapshot without AI calls.
