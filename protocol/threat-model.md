# Threat Model
The supervised agent may be adversarial and may know the controller, monitor prompts, thresholds, tool semantics, and task instructions.

The first pilot is bounded to synthetic records, typed operations, two logical workers, simulated sinks, and a finite deferred-job queue. No shell, unrestricted network, real credentials, arbitrary code execution, or real external side effects are in scope.

The agent proposes actions. An effect broker is the only allowed route to authoritative simulator state changes and releases. Trust in that boundary requires implementation and isolation evidence.

## Current implementation boundary

Simulator v0.2.0 implements in-memory release and scoped-job brokers. Direct
Python callers are trusted research code; actor strings are not authenticated
credentials and state objects are not protected from that code.

The study adapter accepts exact-schema JSON proposals and supplies the actor
identity itself. It exposes no operator-stop, policy-write, shell, import, or
network verb. The trusted runner applies frozen operator/scheduler events.
This data interface is tested, but the library is not a process sandbox.

Calls must be serialized. Copy-on-write publication couples broker state and
ledger records for raised exceptions, including failed append. It does not model
power loss, durable storage, concurrent host threads, or real external commits.
The study runner enforces finite tick and pending-job bounds; the standalone
broker APIs rely on their caller for episode/queue bounds.

The online packet omits author labels, oracle definitions, future scheduler
events, and held-out cases. A trusted researcher must keep complete manifests
and result files away from search participants. Free-text identifiers and tasks
still require a leakage review. Host-level access separation is not implemented.
