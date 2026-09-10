# Changelog

## Simulator 0.2.0 — September 9, 2026

- Fix reused/colliding release tokens with a state-owned monotonic sequence.
- Bind commits to the staging actor and reviewed artifact/destination snapshots.
- Publish every broker transition and ledger write together using serialized
  in-memory copy-on-write; test faults both before and after append.
- Separate receipt details from effect history and verify ledger sequence order.
- Add a four-arm feasibility runner with source-frozen manifests, strict JSON
  proposals, opaque development case IDs, cumulative resource accounting,
  adaptive between-episode submissions, reproducible resume, and fixed replay.
- Score author-defined outcomes separately from broker flags; preserve pending
  work and infrastructure uncertainty, and report useful benign completion.
- Preserve original result artifacts, regenerate current conformance evidence,
  and distinguish historical proposal text from current implementation status.
- Add an independent-study protocol, participant packets and finding template.

The research specification remains v0.3.1. The included scripted study demonstrates
runner operation only; no comparative discovery advantage is established.
