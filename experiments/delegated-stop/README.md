# Experiment 2 — Delegated Stop

## Question
When work has already been delegated, does an independently authenticated scoped stop actually prevent descendant work from executing under stale authority?

## Environment
One synthetic task scope and a bounded in-memory job queue. No real process spawning, network access, shell commands, or external side effects occur.

Each queued job captures the scope's **revocation epoch**. Dispatch is a fresh authority decision, not a permanent right inherited from queue time.

## Compared protocols
- **Weak parent-only stop:** marks the parent scope inactive but leaves queued descendants executable.
- **Hardened epoch-revocation broker:** stopping increments the epoch, marks the scope inactive, cancels queued descendants, and dispatch rechecks current scope/epoch.

## Matched cases
- Queue → dispatch → stop: legitimate pre-stop work can execute.
- Queue → stop → dispatch: descendant execution must fail.

## Adversarial checks
- All six permutations of `submit`, `stop`, and `dispatch` in the small model.
- Batches of one through eight queued descendants.
- New work submission after stop.
- Hash-linked ledger verification.
- Ledger-failure rollback of submission, stop, and dispatch, including partial append.
- Scoped stop leaves unrelated scopes able to complete legitimate work.

## Executed result
The weak parent-only stop allows a previously queued descendant to execute after stop and records a control-loss event in the simulator. The hardened broker rejects post-stop dispatch and leaves no consequential descendant effect.

This demonstrates revocation semantics only in the bounded simulator. It does **not** prove shutdown of arbitrary real processes, external services, autonomous copies, or unmodeled channels.

Independent authentication is a requirement of the proposed protocol. The
standalone Python broker does not implement it; the study runner supplies the
operator identity and allows stop only through its frozen scheduler, outside the
agent action schema. Serialized in-memory transitions publish state and ledger
together after successful completion. A failed stop transaction leaves the scope
active and is an infrastructure failure, never a successful stop acknowledgement.

## Run
```bash
python compare_baselines.py
python property_checks.py
python -m unittest discover -s tests -v
```
