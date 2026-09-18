# Digital Waitlist — Tasks

Ordered by dependency, grouped into phases. Each phase is a vertical slice
that leaves the app in a runnable state. Tasks marked **[P]** have no
dependency on other tasks in the same phase and can be done in either order
or in parallel.

Per the spec's testing directive, only the call state-transition (T5.1) and
the concurrent-call behavior around it (T5.2) get an automated test. Every
other task — models, repositories, services, endpoints, seed, scaffold,
frontend — is verified by running the app, noted explicitly per task rather
than left implied.

## Phase 0 — Scaffold

- [x] **T0.1** [P] Scaffold the backend with `/juliopy`, overriding its
  defaults: SQLite instead of Postgres, no Dockerfile/docker-compose.
  Files: `backend/` (generated).
  Depends on: none.
  Check: `make dev` (or scaffold's equivalent) starts the API locally;
  `GET /health` returns `200`. No test — this is the scaffold itself.
  Done: `uv run uvicorn app.main:app` served `/health` and `/ready` at 200.
- [x] **T0.2** [P] Scaffold the frontend with Vite's `react-ts` template.
  Files: `frontend/` (generated).
  Depends on: none.
  Check: `npm run dev` serves the default page locally. No test — scaffold.
  Done: `npm run dev` served the default page at 200.

## Phase 1 — Data model & seed

- [x] **T1.1** Define `Restaurant` and `WaitlistEntry` SQLAlchemy models,
  with `WaitlistEntry.state` as an enum (`waiting`, `called`, plus
  `seated`/`cancelled`/`no_show` reserved but unused) and a unique
  `status_token` column.
  Files: `backend/app/models.py`, `backend/app/db.py`.
  Depends on: T0.1.
  Check: manual — create the tables locally, insert one row of each via a
  script or shell, read them back. No test — models aren't tested per
  instruction.
  Done: Alembic migration applied cleanly, a second autogenerate produced an
  empty diff, and a manual insert/read-back of both models round-tripped
  correctly (`state=waiting`, generated `status_token`, `called_at=None`).
- [x] **T1.2** Write the one-time seed script for the single pilot
  restaurant, shaped after El Libro's restaurant record.
  Files: `backend/app/seed.py`.
  Depends on: T1.1.
  Check: run the seed script against a fresh DB, confirm one restaurant row
  exists (manual query). No test — static data, not logic.
  Done: `make seed` inserts "La Terraza Azul" and is idempotent (re-running
  it detects the existing row and skips).

## Phase 2 — Guest join

- [x] **T2.1** Repository: insert a waitlist entry in `waiting` state with a
  generated `status_token`.
  Files: `backend/app/repositories/waitlist_repository.py`.
  Depends on: T1.1.
  Check: manual — call it directly (script/shell) against a test DB,
  confirm a `waiting` row with a token exists. No test — creation isn't a
  state transition; repositories aren't tested per instruction.
  Done: called `WaitlistRepository.create_entry` directly — returned entry
  `state=waiting` with a non-empty `status_token`.
- [x] **T2.2** Service: `join(restaurant_id, name, phone, party_size)`
  delegates to the repository.
  Files: `backend/app/services/waitlist_service.py`.
  Depends on: T2.1.
  Check: manual — call it directly, confirm the same. No test — services
  aren't tested per instruction.
  Done: called `WaitlistService.join` directly — same result as T2.1.
- [x] **T2.3** Endpoint: `POST /restaurants/{id}/waitlist`.
  Files: `backend/app/api/routes/guest.py`, `app/schemas.py`, `app/main.py`
  (router registration + CORS), `app/config.py` (`allowed_origins`).
  Depends on: T2.2.
  Check: manual — `curl` the endpoint, confirm `201` and a token in the
  response.
  Done: `curl` returned `201` with `{"status_token": "..."}`; invalid
  input (`party_size: 0`, missing field) returned `422`; DB read-back
  confirmed the row landed with correct fields and `waiting` state.
- [x] **T2.4** Join page: name/phone/party-size form, posts to the join
  endpoint, stores the returned token (e.g. in the URL) for the status page.
  Files: `frontend/src/pages/Join.tsx`, `frontend/src/pages/Status.tsx`
  (navigation target, fleshed out in Phase 3), `frontend/src/api/client.ts`,
  `frontend/src/App.tsx` (routing).
  Depends on: T2.3.
  Check: manual run — submit the form, confirm navigation to the status
  page with a valid token.
  Done: `npm run build` type-checks clean; simulated the browser's request
  (CORS preflight + POST with `Origin: http://localhost:5173`) — both
  succeeded and the entry landed in the DB; confirmed the dev server
  resolves `/status/:token` (client-side route) at `200`. No Chrome
  automation available this session (declined), so the actual click →
  `navigate()` → render sequence wasn't observed in a live browser — noted
  as a gap below rather than assumed.

## Phase 3 — Guest status & position

- [ ] **T3.1** [P] Repository: `list_waiting(restaurant_id)` — a restaurant's
  `waiting` entries ordered by `(joined_at, id)`. At pilot scale (≤40
  waiting entries per restaurant), this single ordered list is all that's
  needed for position — no SQL rank/window function. This same method is
  reused by the host queue view in Phase 4, so it isn't written twice.
  Files: `backend/app/repositories/waitlist_repository.py`.
  Depends on: T1.1 (can proceed alongside Phase 2).
  Check: manual — seed a few `waiting` entries plus one `called` entry,
  confirm the query returns only the waiting ones, in join order. No test —
  a read query, not a state transition.
- [ ] **T3.2** Service: `get_status(token)` returns state + position while
  `waiting`, computed as the entry's index (+1) in `list_waiting`'s result.
  Files: `backend/app/services/waitlist_service.py`.
  Depends on: T3.1, T2.2.
  Check: manual — call it directly for a waiting token, confirm position
  matches where the entry falls in the ordered list. No test — services
  aren't tested per instruction. (The "position omitted once called" case
  is added in T5.5, once calling exists.)
- [ ] **T3.3** Endpoint: `GET /waitlist/status/{token}`.
  Files: `backend/app/api/routes/guest.py`.
  Depends on: T3.2.
  Check: manual — confirm the endpoint reflects position changes as other
  entries are added.
- [ ] **T3.4** Status page: polls the status endpoint every 5 seconds,
  displays position.
  Files: `frontend/src/pages/Status.tsx`, `frontend/src/api/client.ts`
  (shared polling hook).
  Depends on: T3.3.
  Check: manual run — join twice, confirm the first guest's position
  updates within 5s as expected.

## Phase 4 — Host queue view

- [ ] **T4.1** Endpoint: `GET /restaurants/{id}/waitlist`, backed directly by
  T3.1's `list_waiting` — no new repository query.
  Files: `backend/app/api/routes/host.py`.
  Depends on: T3.1.
  Check: manual — confirm the endpoint returns entries in join order.
- [ ] **T4.2** Host page: polls the queue endpoint every 5 seconds, lists
  name/party size/elapsed wait.
  Files: `frontend/src/pages/Host.tsx`.
  Depends on: T4.1.
  Check: manual run — join a few guests, confirm they appear on the host
  page within 5s, in order.

## Phase 5 — Call action & conflict handling (core concurrency slice)

- [ ] **T5.1** Repository: conditional call transition, scoped to a
  restaurant — `UPDATE ... SET state='called', called_at=? WHERE id=? AND
  restaurant_id=? AND state='waiting'`, returns whether a row was actually
  updated.
  Files: `backend/app/repositories/waitlist_repository.py`.
  Depends on: T2.1.
  Check (test-first): `backend/tests/test_waitlist_repository.py::test_call_transitions_waiting_to_called`
  plus `test_call_ignores_entry_from_a_different_restaurant` — same entry
  id, wrong `restaurant_id`, no row updated.
- [ ] **T5.2** The core concurrency test: fire two call requests at the same
  entry concurrently (threads/async tasks against the real test DB, not
  sequential calls) and assert exactly one reports success.
  Files: `backend/tests/test_concurrency.py`.
  Depends on: T5.1.
  Check (test-first): `backend/tests/test_concurrency.py::test_concurrent_call_only_one_succeeds`.
- [ ] **T5.3** Service: `call(restaurant_id, entry_id)` raises/returns a
  conflict result when the repository reports no row updated (already
  called, or entry belongs to a different restaurant).
  Files: `backend/app/services/waitlist_service.py`.
  Depends on: T5.1.
  Check: manual — call it against an already-`called` entry, and against an
  entry from a different restaurant, confirm the conflict result both times.
  No test — services aren't tested per instruction; the transition itself
  is already covered by T5.1/T5.2.
- [ ] **T5.4** Endpoint: `POST /restaurants/{restaurant_id}/waitlist/{entry_id}/call`,
  `200` on success, `409` on conflict (including cross-restaurant).
  Files: `backend/app/api/routes/host.py`.
  Depends on: T5.3.
  Check: manual — `curl` it twice for the same entry, confirm `200` then
  `409`; `curl` it once more with a different `restaurant_id` for a fresh
  waiting entry, confirm `409`.
- [ ] **T5.5** Service: extend `get_status` to omit position once an entry
  is `called` (completes T3.2's deferred case).
  Files: `backend/app/services/waitlist_service.py`.
  Depends on: T5.3, T3.2.
  Check: manual — call an entry, then fetch its status, confirm no
  position is returned. No test — services aren't tested per instruction.
- [ ] **T5.6** Wire the "Llamar" button on the host page to the call
  endpoint; update the status page to show the called state instead of a
  position.
  Files: `frontend/src/pages/Host.tsx`, `frontend/src/pages/Status.tsx`.
  Depends on: T5.4, T5.5.
  Check: manual run — click Llamar, confirm the guest's status page flips
  to "table ready" within one poll cycle, and that a second Llamar click
  (e.g. from a second browser tab) surfaces the conflict instead of
  double-calling.

## Phase 6 — End-to-end verification

- [ ] **T6.1** Run backend and frontend locally together; walk the golden
  path (join → watch position drop as earlier entries are called → get
  called → status flips) and the conflict path (two tabs racing a call on
  the same entry).
  Files: none (verification only).
  Depends on: all prior phases.
  Check: both paths observed working as described; no new automated test —
  this is the manual sign-off pass for the vertical slice.
