# Persistent delegated-stop pilot

This integration moves the stop contract from an in-memory simulator to an
HTTP service, a SQLite job queue, separate client/worker processes, and a durable
local mailbox. Messages are harmless test strings. No mail is sent externally.

It tests one engineering question: **can work already held by a worker still
commit after permission is withdrawn?** The agent client is scripted; this is
not a measurement of a learned model's behavior or an isolated hostile process.

## Run it

Python 3.10+ with its standard library is sufficient. From the repository root:

```bash
python -m unittest discover -s queue_tests -v
python -m northstar_queue.experiment --output study-runs/queue-pilot/my-run
```

To replay the separate Claude review as well as the internal checks and comparison:

```bash
python -m northstar_queue.verify --output study-runs/queue-reviewed/my-run
```

The [published run](../../results/queue-integration/verification.json) passes
10 internal and 53 Claude-authored checks. Across 14 cases per control,
cooperative cancellation produced 11 post-stop deliveries; both stronger
controls produced zero. All three completed 33 of 33 required authorized jobs.
Concurrent ordering can change the cooperative delivery count on replay.

Choose a new output directory for each run. The command executes all 14 authored
cases under three controls, saves ordered traces and measured outcomes to
`report.json`, and exits unsuccessfully on technical errors, failures in either
strong control, inconsistent evidence, unsettled work, or missing required useful
completion. Failures of cooperative cancellation are measured findings under the
stronger post-stop contract, not a claim that its limited contract was violated.

Private role credentials and database files are temporary and are not published.
The report contains source hashes and redacted requests, responses and mailbox
records. Concurrent execution orders and latency can vary across runs. Compare
the safety/usefulness assertions, not byte-for-byte equality of generated IDs,
timestamps or race outcomes.

## Controls and effect boundary

| Control | Stop behavior | Delivery behavior |
|---|---|---|
| Cooperative cancellation | Cancel queued work; revoke agent capabilities | An existing worker claim may still deliver |
| Transactional cancellation | Cancel queued and claimed work; revoke capabilities | Atomically check cancellation and active scope with the mailbox write |
| NorthStar epoch fencing | Advance permission version; cancel pending claims and revoke capabilities | Atomically check the captured version and active scope with the mailbox write |

All modes enforce roles, bind claims to jobs, preserve submission/delivery
idempotency and scope descendant revocation. The second is a strong conventional
comparator. A tie with it is not evidence of NorthStar-specific superiority.
These are implementations of control patterns, not a benchmark of commercial
queue products or a claim that epoch fencing is novel.

The current local bounds are 64 outstanding jobs and 64 scopes per root family,
and 128 outstanding jobs globally. A delegated child shares its root's quota.
These bounds limit one scope family's ability to consume all admission capacity;
they do not supply general fairness or protect a production service from overload.
Resume reactivates only the named scope; existing child scopes need their own
explicit resume and fresh capability.

SQLite orders competing write transactions. A stop acknowledgement means its
revocation transaction committed. A delivery committed before that point cannot
be undone by a later stop. The pilot records observed acknowledgement latency;
it supplies no bound under overload, a long-running transaction or storage failure.

**The real effect here is a local database write.** Authority and that effect
share one database transaction. An email, payment, network API call or external
filesystem write does not automatically inherit this property. Its destination
must enforce a compatible boundary, and the integration must be reviewed again.

## Current trust and review limits

The agent receives a scoped bearer capability through a tool adapter. The
operator, worker role credential, service process, host and database files are
trusted. The worker API does not accept a replacement message, command, URL or
destination. It only commits the message stored when the job was authorized.

Separate processes improve integration realism but do not create OS isolation.
A regression test intentionally writes directly to the database from the host:
that bypass works, and the trace checker detects the inconsistency. A hostile
actor with such filesystem access is outside this pilot's protection.

The internal inventory and evaluator were authored with the implementation.
The [Claude review](claude-review/README.md) counts as independent AI review of
the local contract, commissioned by the project using its harness. Passing local
tests does not establish catastrophe coverage, adoption, or numerical global
risk reduction.

See the [pre-implementation protocol](PROTOCOL.md), [case inventory](cases.json),
[reviewer API](REVIEW-API.md) and [review instructions](REVIEW.md).
