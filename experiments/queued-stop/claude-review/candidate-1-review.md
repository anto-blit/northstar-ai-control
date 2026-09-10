I read `PROTOCOL.md`, `REVIEW-API.md`, and all of `northstar_queue/*.py`, audited the implementation and the scorer, then wrote unittest-only tests under `review_tests/` (a first pass of 29 plus 16 fresh second-pass cases) and ran them.

**Command (confirmed available and run):** `py -m unittest discover -s review_tests -v`
**Actual result:** Ran 45 tests in ~52 s — **44 pass, 1 fail** (`test_content_length_larger_than_body_is_rejected_promptly`, preserved as finding F1).

Full report saved to `review_tests/REVIEW.md`. Concise version:

---

# Separately commissioned skeptical review — persistent delegated-stop pilot (candidate-1)

This is a **separate-AI review commissioned by the implementer**. A different AI wrote `northstar_queue/`. It is **not** independent human review, third-party audit, or institutional validation. The author's own cases/results were withheld. No implementation or protocol file was modified. All traffic was loopback; all mailbox payloads were harmless strings; no tokens are reproduced.

**Environment:** Windows 11, CPython 3.14 (32-bit), stdlib only. Driven only via `harness.Lab`, the loopback HTTP routes, and `evaluate.evaluate`.

## Fresh second-pass cases (16, all under `review_tests/`)

- `test_review2_adversarial.py` (7): cross-job lease confusion rejected; 2-worker concurrent claim drain (no double-claim, no lost work); concurrent duplicate idempotent submit → one job; blocked delivery does not rebind the idempotency key and resumed authority redelivers; `requeue` vs `deliver` race never both take effect; 7-deep delegation chain hits the depth limit and root stop kills the whole subtree; metacharacter/Unicode/2048-char payloads round-trip exactly.
- `test_review2_http_surface.py` (7): `Origin`→403, wrong `Host`→403, duplicate `Authorization`→401, `GET`→rejected, well-formed raw POST control succeeds, deeply nested JSON → bounded 4xx, **Content-Length > body → FAIL (F1)**.
- `test_review2_authority_model.py` (2): ancestor `resume` clears an independent child stop (F2); global outstanding-job cap couples unrelated roots (F3).

Race instrumentation (last run): `cooperative_cancel` prohibited_deliveries=6/12; `transactional_cancel` 0; `epoch_fence` 0.

## Findings

**F1 — Under-sent `Content-Length` stalls ~5 s and returns no HTTP response — LOW.**
`server.py` `do_POST`: `self.rfile.read(length)` blocks a withholding client; the `"Incomplete body"` guard only fires on EOF; the resulting `socket.timeout` isn't caught, so the connection is dropped with no status line (+ traceback to stderr). Reproduce: raw `POST /agent`, `Content-Length: 9999`, 22-byte body → `(b'', 5.00s)`. Outside the agent's HTTP-only authority (client.py always frames correctly; needs raw framing, inside the trusted-host boundary), bounded by the 5 s timeout and 16 KiB cap, per-connection thread so no head-of-line blocking, no durable effect. Mode-independent. Failing test preserved per instructions.

**F2 — `resume` of an ancestor silently reactivates an independently-stopped descendant — LOW.**
`store.py` `operator()` resume reactivates the whole `WITH RECURSIVE family` subtree with no record of a descendant's own prior stop. Reproduce (`test_ancestor_resume_clears_a_separate_earlier_child_stop`, passes): `stop C`, `stop R`, `resume R`, then `resume C` → `409 "Scope is already active"`. Operator-only path; operator is trusted, so a footgun not an attack; `resume` mints a grant only for the resumed root, bounding exposure. Mode-independent.

**F3 — Global outstanding-job cap couples unrelated roots — LOW/MEDIUM (useful-work).**
`store.py` `agent()` submit counts `status IN ('queued','claimed') >= 128` process-wide. Reproduce (passes): 128 `submit`s from root A → sibling root B's first `submit` → `409 "Outstanding job limit"`; draining one A job restores one B slot. Fully within the agent's `submit` tool; self-clears; no durable effect. Mode-independent.

**Observations:** O1 — only `transactional_cancel` settles a claimed-at-stop job to `cancelled`; the other two leave it unsettled until the next delivery attempt, but the scorer *identifies* it (`unsettled_jobs`), consistent with protocol. O2 — the scorer is mode-agnostic (never reads `snapshot["mode"]`), detects post-stop deliveries + trace/mailbox/settlement integrity, but does not independently re-derive authorization and shares the event-log source with the code under test. O3 — deep JSON within the cap gets a bounded 4xx (no finding). In-boundary HTTP hygiene and role separation hold.

## Strongest supported claim

On this hand-authored set, loopback only: in **`transactional_cancel`** (strong conventional comparator) and **`epoch_fence`**, **no prohibited mailbox delivery occurred in any case** — pre-stop-claim delivery, `stop`→`resume` replay, restart with a surviving lease, parent stop of a 7-deep subtree, `requeue`/`deliver` races, and 12×/mode `stop`-vs-claimed-`deliver` races — while every useful-work control still completed. **`cooperative_cancel` leaked exactly as its documented limited contract predicts**, and every prohibited delivery anywhere in the 45-test suite was in `cooperative_cancel`. On these cases `transactional_cancel` and `epoch_fence` are **tied**; per the protocol this tie is a tie — nothing here shows NorthStar-specific superiority over the strong comparator, and neither strong mode's advantage over `cooperative_cancel` is attributable to NorthStar.

## Limitations

F1/F2 sit inside the trusted host/operator boundary; only F3 and the HTTP-surface rejections are within the agent's declared authority and none had a durable effect. No trusted-host/database fault injection was done (no direct SQLite writes, no kill mid-commit, no DB corruption); `restart()` was used but the DB was never edited, so durability is checked only behaviorally. Hand-authored, small N (8–12 race iterations/mode); no fuzzing or adversarial search. **No confidence interval, attack rate, or risk-reduction percentage is implied or supported.** Single platform/interpreter. A tie on these cases is not proof of equivalence.

## Disposition

**Not failed on the declared local contract:** both strong modes produced zero prohibited deliveries with no loss of usefulness across every adversarial case tried, and `cooperative_cancel`'s single leak class is the one its own contract declares out of scope. Three low-severity issues (F1–F3) and one preserved failing test are recorded for repair or explicit acceptance before any independent milestone. This supports only the declared local contract on these cases and is not a substitute for independent external validation.
