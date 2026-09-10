# Separately commissioned skeptical review #2 — persistent delegated-stop pilot (candidate-2)

**Nature of this review.** Commissioned *separate-AI* review of a repair. A different AI wrote
`northstar_queue/`; the implementer's own cases/results were withheld. This is **not**
independent human review, a third-party audit, institutional validation, or a preregistered
study. Per `PROTOCOL.md`, CI and a second implementer run do not count as independent review —
and neither does this.

**Boundary respected.** No file under `northstar_queue/` or `experiments/queued-stop/` was
modified. Only `review_tests/` was edited. All traffic was loopback to the harness-spawned
service; every mailbox payload was a harmless fixed string. No installs, external network,
`/tmp` scripts, shell-payload execution, OS changes, or destructive commands. No capability
tokens are reproduced here.

## Environment

- Windows 11, CPython 3.14 (32-bit), standard library only.
- Driven only through `northstar_queue.harness.Lab`, the loopback HTTP routes, and
  `northstar_queue.evaluate.evaluate`.

## Full-suite run (actual)

```
py -m unittest discover -s review_tests -v
```

**Ran 53 tests — OK (0 failures, 0 errors)**, ~86 s. Executed twice end-to-end with the same
pass result. Race instrumentation both runs:

```
[race:cooperative_cancel]   deliver_outcomes={'delivered': 12} prohibited_deliveries=5  mailbox=12
[race:transactional_cancel] blocked+delivered split, prohibited_deliveries=0  mailbox<=9
[race:epoch_fence]          blocked+delivered split, prohibited_deliveries=0  mailbox<=6
```

No failing test remains. The brief's instruction "keep any failing test" is moot: candidate-1's
one kept-failing assertion (F1) is now a **passing regression**, which is the intended outcome
of a successful repair. Every cooperative_cancel prohibited delivery seen anywhere in the
suite stays confined to cooperative_cancel, its declared limited contract.

## Delta review of the repair

### F1 — under-sent `Content-Length` — FIXED (regression guard green)

`server.py`: socket timeout `5 → 2 s`; `do_POST` gains `except TimeoutError` → bounded
`400 {"error": "Incomplete request body before the local read deadline"}`; `RecursionError`
folded into the 400 bucket; `respond()` also tolerates `TimeoutError` on `wfile.write`
(committed result is retryable by idempotency key).
`test_review2_http_surface.test_content_length_larger_than_body_is_rejected_promptly` was
candidate-1's kept-failing test; its assertions are rewritten as a regression — a JSON 4xx in
under 3 s, `Content-Type: application/json`, non-empty error body — and it now passes.

*Residual (lower severity than F1 itself, not introduced by the repair):* the 2 s deadline
also governs the request-line/header read inside `BaseHTTPRequestHandler.handle_one_request`,
which is **outside** `do_POST`'s `try`. A client that opens a socket and sends nothing still
produces a stderr traceback in the server subprocess after ~2 s (previously ~5 s) with no
status line. Bounded, self-healing, one daemon thread per connection, no mailbox write, no
authority effect, mode-independent. This is the same shape as candidate-1's F1 note, now
shorter-lived; the framed `client.py` never hits it.

### F2 — ancestor `resume` revived an independently-stopped descendant — FIXED

`store.py operator()`: `descendants = self.family(...) if action == "stop" else [root]`. Resume
now reactivates and re-grants only the named scope. Verified:

- `test_review2_authority_model.test_ancestor_resume_does_not_clear_a_separate_earlier_child_stop`
  (all modes) — **rewritten**: candidate-1 asserted the follow-up `resume child` returned
  `409 "Scope is already active"` (i.e. it *documented* the silent revival). It now requires
  that follow-up to be a genuine `200` state change with a fresh capability, and the
  transitively-stopped grandchild to remain stopped until its parent is resumed.
- `test_review2_repair.test_repeated_root_stop_resume_never_lifts_an_independent_child_stop`
  (fresh, all modes) — 3× root stop/resume cycles never clear the child's pending stop; the
  child's original grant stays dead throughout; `resume child` is a one-time real change.
- `test_review2_authority_model.test_resume_of_a_descendant_below_a_still_stopped_ancestor_is_refused`
  — the "no lifting a subtree out from under a stopped ancestor" guard is preserved
  (`409 "Ancestor remains stopped"`).

*Corollary, not a defect:* after a broad subtree stop the operator must now resume **each**
descendant individually; this is the intended narrower contract per the PROTOCOL amendment.

### F3 — global outstanding-job cap coupled unrelated roots — PARTIALLY FIXED

`store.py`: `MAX_ROOT_OUTSTANDING = 64`, `MAX_ROOT_SCOPES = 64`, `MAX_OUTSTANDING = 128`.
`agent()` computes the recursive `family` of the submitter's `root_scope` and sums pending
(`queued`+`claimed`) jobs whose `scope` is in that family; descendants share the root quota;
`delegate` is refused past 64 scopes in the family. Verified holds against:

- fan-out of the 65th job across 4 delegated child scopes (`test_review2_repair
  .test_spreading_submits_across_delegated_children_cannot_exceed_family_quota`, all modes);
- wide delegation to the 64-scope ceiling, with stopped children still counted
  (`…test_wide_delegation_cannot_exceed_family_scope_limit`);
- a two-thread race for the last family slot — `BEGIN IMMEDIATE` serialises; never > 64
  outstanding (`…test_concurrent_submits_at_the_family_boundary_admit_at_most_one`, all modes);
- `test_review2_authority_model.test_one_root_family_at_its_quota_does_not_block_a_sibling_root`
  — **rewritten**: candidate-1 asserted the sibling root's *first* submit failed after another
  root queued 128; that expectation is void — the sibling now keeps its own 64-job budget.
  The "one family starves all siblings" behaviour is preserved as the prohibited outcome.

*Residual (accepted, now pinned by a test).* The global cap is 128 and each family may hold
64, so **exactly two saturated families still lock out every additional root's `submit`**
(`test_review2_authority_model.test_global_cap_still_couples_roots_once_two_families_fill_it`).
`PROTOCOL.md` concedes these bounds are "not a general fairness or denial-of-service
guarantee", so this is eyes-open acceptance, not a silent bug — but the same amendment's
phrase "these bounds preserve room for another root in this small lab" is only literally true
while fewer than two families are saturated. `operator create` is itself uncapped (trusted
path), so the global pool is the only agent-relevant ceiling.

### O1 — abandoned claim permanently consumed admission capacity — FIXED

`store.py`: on stop, `statuses = "('queued')" if mode == "cooperative_cancel" else
"('queued','claimed')"` — both strong modes settle claimed work to `cancelled` without worker
cooperation. Amended regressions:

- `test_settlement_and_scorer.test_both_strong_modes_settle_a_claimed_job_at_stop`
  (was `test_only_transactional_cancel_settles_a_claimed_job_at_stop`) — **corrected**:
  epoch_fence moved from "parks claimed / reported unsettled" to "settles cancelled / not
  unsettled", now identical to transactional_cancel; cooperative_cancel still parks it.
- `test_settlement_and_scorer.test_claimed_job_after_stop_cannot_be_requeued_even_after_resume`
  (was scoped to `WEAK_SETTLEMENT = (cooperative_cancel, epoch_fence)`) — **corrected** to run
  all modes; the "requeue stays refused before and after resume" safety check is preserved and
  **strengthened** with a `mailbox == []` assertion and a per-mode settled-status split.
- `test_review2_repair.test_abandoned_full_family_of_claims_is_released_by_stop_in_strong_modes`
  (fresh) — an abandoned worker claims a **whole family's** worth of jobs (64) and never
  returns; new submits are refused; a stop from fresh operator authority frees that admission
  capacity in the strong modes so post-resume work is admitted, and the late-returning stale
  lease is `blocked` with the original job never reaching the mailbox. cooperative_cancel is
  characterised as still starved **and** still leaking the stale job — its declared contract,
  kept visible as a counterexample (`prohibited_deliveries >= 1`).
- `test_review2_repair.test_stop_settles_claimed_and_queued_without_touching_delivered_jobs`
  (fresh) — guards the `status IN ('queued','claimed')` cleanup filter against rewriting an
  already-`delivered` job or dropping its committed mailbox row.

### Resource-close fixes

- `store.py Store.__init__`: `with self.connect()` → `with closing(self.connect())`. sqlite3's
  connection context manager commits/rolls back but does **not** close; candidate-1 leaked the
  bootstrap connection's handle for the life of the process — the handle that made Windows
  `TemporaryDirectory` cleanup fail. Now closed.
- `client.py`: the `HTTPError` branch reads its body inside `with response:` so the error
  response object is closed.
- `server.py respond()`: tolerates `TimeoutError` on write (see F1).
- **`ignore_cleanup_errors=True` removed** from `support.lab`'s `TemporaryDirectory`, per the
  brief. The full suite ran to completion **twice** with a plain `TemporaryDirectory()` and no
  cleanup error, so the leak fix makes the flag unnecessary; a future resurfaced handle leak
  will now fail loudly rather than be masked.

### O-level note (new, minor)

`family()` counts structurally, so scopes stopped in a subtree still consume the 64-scope
family budget after the root is resumed. A long-lived root that repeatedly delegates and is
stopped/resumed can exhaust its scope budget with mostly-inactive scopes. Usefulness ceiling
only, within the "small lab" framing; no integrity or delivery effect.

## Corrected prior expectations (explicit)

| candidate-1 expectation | status | correction |
|---|---|---|
| F2 test: `resume child` after `resume root` → `409 "already active"` (documents silent revival) | **void** | resume is now scope-local; `resume child` must be an explicit `200`, child stays stopped through root cycles |
| F3 test: a sibling root's first `submit` fails once another root queues 128 | **void** | per-family quota (64) decouples siblings; residual is *two* saturated families vs. the 128 global cap |
| O1: `WEAK_SETTLEMENT = (cooperative_cancel, epoch_fence)`; "only transactional_cancel settles a claimed job at stop" | **void** | epoch_fence now settles claimed work at stop identically to transactional_cancel |
| F1 assertion kept *failing* | now a **passing** regression | 2 s read deadline + `except TimeoutError` → bounded 400 |

## Fresh challenges to the repair (≥3 required; 6 added, all pass)

1. `test_review2_repair.RootFamilyQuotaBypass.test_spreading_submits_across_delegated_children_cannot_exceed_family_quota`
2. `…RootFamilyQuotaBypass.test_wide_delegation_cannot_exceed_family_scope_limit`
3. `…RootFamilyQuotaBypass.test_concurrent_submits_at_the_family_boundary_admit_at_most_one`
4. `…ChildStopPersistence.test_repeated_root_stop_resume_never_lifts_an_independent_child_stop`
5. `…StaleWorkerClaimCleanup.test_abandoned_full_family_of_claims_is_released_by_stop_in_strong_modes`
6. `…StaleWorkerClaimCleanup.test_stop_settles_claimed_and_queued_without_touching_delivered_jobs`

They probe, respectively: family-quota evasion by fan-out, by tree width, and by a
commit-race; child-stop persistence across repeated root churn; stale-claim capacity
exhaustion + cleanup + a late stale-lease delivery attempt; and cleanup-filter over-reach onto
delivered jobs. None found a bypass on this case set.

## Limitations

- Commissioned separate-AI review, **not** independent human or institutional validation.
- Hand-authored, small N. Races run 2–12 iterations/mode. No fuzzing, no learned/adversarial
  search. **No confidence interval, population attack rate, or risk-reduction percentage is
  implied or supported, and none is endorsed.**
- Single platform/interpreter (Windows 11, CPython 3.14 32-bit). SQLite locking/timeout
  behaviour can differ elsewhere.
- No trusted-host / DB fault injection: no direct SQLite writes, no kill mid-commit, no file
  corruption. `Lab.restart()` exercised; the database was never edited. Durability rests
  behaviourally on `BEGIN IMMEDIATE` + `synchronous=FULL` + single-transaction design.
- The scorer shares its event-log source with the code under test; a consistently-lying store
  would defeat it.
- Absence of a counterexample here is not a guarantee.

## Strongest supported claim

On this hand-authored case set, loopback only, CPython 3.14 (32-bit) / Windows 11, across 53
tests run twice:

- **Every candidate-1 finding is addressed and the amended contract holds on these cases.**
  F1 returns a bounded 4xx in < 3 s instead of stalling and dropping the connection. Ancestor
  `resume` no longer revives an independently-stopped descendant, including under repeated
  root stop/resume churn. The revised per-root-family quota (64 outstanding / 64 scopes,
  shared by descendants) resisted every bypass tried — fan-out across delegated children, wide
  trees, and a commit-time race. O1's capacity exhaustion is fixed: in both strong modes a
  stop settles a whole abandoned family of claims to `cancelled` and fresh authority is then
  admitted, while the late stale lease is `blocked` with no mailbox write.
- **In `transactional_cancel` and `epoch_fence`, no prohibited mailbox delivery occurred in
  any case in this suite**, and every authorized/useful-work control still completed
  (single job; sibling root unaffected by a saturated family; resume-minted capability;
  idempotent submit/deliver; concurrent claim drain with no double-claim or lost work;
  metacharacter/Unicode/2048-char payloads round-tripping exactly).
- **`cooperative_cancel` leaked exactly as its documented limited contract predicts** — a
  pre-stop *claimed* job still delivers after stop/resume, and its abandoned claims still hold
  family capacity. Every prohibited delivery seen anywhere in the 53-test suite was in
  `cooperative_cancel`.
- **Residual:** two saturated root families can still exhaust the 128 global admission pool and
  lock out every further root's `submit` (F3 not fully closed; accepted in `PROTOCOL.md`).

Per `PROTOCOL.md`, on these cases `transactional_cancel` (the strong conventional comparator)
and `epoch_fence` (NorthStar's pattern) are **tied** on the stop contract and on useful work.
**A tie is a tie:** nothing here demonstrates NorthStar-specific superiority over the
conventional transaction check, and neither strong mode's advantage over `cooperative_cancel`
is attributable to NorthStar. This review supports **only** the declared local contract on
**these** cases, is not a substitute for independent external validation, and **does not
justify any global-risk percentage decrement.**
