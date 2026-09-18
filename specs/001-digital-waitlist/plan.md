# Digital Waitlist — Plan

## Technical approach

Backend and frontend are two separate local processes; no container
orchestration.

- **Backend**: FastAPI, scaffolded with `/juliopy`, but with two overrides
  from that skill's defaults: no Dockerfile/docker-compose (local only, per
  instruction), and SQLite in place of Postgres. Everything else from the
  scaffold is kept: uv, ruff, mypy, pytest, typed config, Makefile, health
  check. Data access goes through a repository layer (raw conditional SQL
  updates for the call-conflict check) fronted by a thin service layer
  (join, call, position calculation) — per the spec's own repository/service
  layering direction.
- **Frontend**: React + TypeScript via Vite (`npm create vite@latest --
  --template react-ts`) — this is outside `/juliopy`'s scope (backend-only
  scaffold), so it's set up by hand as a sibling app. Three views: Join,
  Guest status, Host queue. Both status and host views poll every 5 seconds
  (FR4, FR6) with a plain `setInterval` + `fetch`; no WebSockets/SSE
  (explicitly excluded).
- **Concurrency control**: the call action is a conditional update —
  `UPDATE waitlist_entries SET state='called', called_at=? WHERE id=? AND
  restaurant_id=? AND state='waiting'` — checked by affected-row count. Zero
  rows updated means either someone else already acted on it, or the entry
  doesn't belong to the calling restaurant (FR7, FR8); the API returns `409
  Conflict` either way — cross-restaurant access isn't distinguished from a
  race, so it can't be used to probe which entries exist. This is enough for
  SQLite's single-writer model and needs no extra locking primitives.
- **Position**: computed at read time from the same ordered `waiting`-entries
  list used by the host queue view — the guest's position is just its index
  (+1) in that list (FR5, FR11), never stored, so it can't drift from the
  underlying state. At pilot scale (≤40 waiting entries per restaurant) an
  in-memory index is viable; no SQL rank/window function is needed.

## Affected components/files

Exact paths follow whatever `/juliopy`'s scaffold generates; this is the
intended shape:

- `backend/app/models.py` — `Restaurant`, `WaitlistEntry` (SQLAlchemy
  models); `WaitlistEntry.state` as a small enum, schema allows for future
  states (`seated`, `cancelled`, `no_show`) per the spec's note on reserving
  columns, but only `waiting`/`called` are read or written by this slice.
- `backend/app/repositories/waitlist_repository.py` — inserts, the
  conditional call-transition update, and a single `list_waiting` query
  (used both for the host queue view and, by index, for guest position).
- `backend/app/services/waitlist_service.py` — join, call, get-status,
  list-waiting; where the 409 decision is made from the repository's
  affected-row result.
- `backend/app/api/routes/guest.py` — `POST /restaurants/{id}/waitlist`,
  `GET /waitlist/status/{token}`.
- `backend/app/api/routes/host.py` — `GET /restaurants/{id}/waitlist`,
  `POST /restaurants/{id}/waitlist/{entry_id}/call`.
- `backend/app/seed.py` — one-time seed of the single restaurant (FR1,
  FR12), run at startup or via a Makefile target.
- `backend/app/db.py` — SQLite engine/session setup (from `/juliopy`,
  Postgres swapped for SQLite).
- `frontend/src/pages/Join.tsx`, `Status.tsx`, `Host.tsx`
- `frontend/src/api/client.ts` — typed fetch helpers, including the 5s
  polling hook shared by Status and Host.

## Data/API changes

- **Tables**: `restaurants(id, name)`; `waitlist_entries(id, restaurant_id,
  name, phone, party_size, state, status_token, joined_at, called_at)`.
  `status_token` is a random unguessable string (FR3), unique-indexed.
- **Endpoints**:
  - `POST /restaurants/{id}/waitlist` → `201` with `status_token`.
  - `GET /waitlist/status/{token}` → guest's state + position (position
    omitted once `called`, per FR9).
  - `GET /restaurants/{id}/waitlist` → all `waiting` entries, ordered.
  - `POST /restaurants/{id}/waitlist/{entry_id}/call` → `200` on success,
    `409` if already called/seated by someone else, or if `entry_id` isn't
    a `waiting` entry belonging to `{id}`.
- No El Libro runtime call anywhere — seed data is static, authored once
  from El Libro's shape (FR12).

## Testing strategy

Framework: **pytest** (from the `/juliopy` scaffold), backend only — no
frontend test framework is introduced. Scope is deliberately narrow, per
instruction: only the state-transition logic and the concurrency behavior
around it get automated tests. Models, repository CRUD/query methods that
don't themselves change state (create, list, position lookup), and the
service layer are not tested directly — they're exercised indirectly by
running the app, and by the two tests below where the transition logic
lives. Tests hit that core logic and a real SQLite test database (file or
in-memory), not a mocked layer — the whole point is catching a real
conditional-update race.

- **Call transition**: the conditional `waiting → called` update succeeds
  exactly once for a given entry.
- **Concurrency**: two call requests fired at the same entry — exactly one
  succeeds, the other observes the conflict. This must exercise real
  concurrent execution (threads/async tasks against the same DB), not two
  sequential calls, or it won't catch the race it's meant to catch.

Not tested: models, repository create/list/position queries, the service
layer, request validation, endpoint response shapes, frontend rendering —
all verified by running the app instead.

tasks.md marks only the two transition/concurrency tasks as test-first;
every other task (including data model, seed, join, position, host list,
and all frontend work) is verified by running the app.

## Risks and tradeoffs

- **SQLite + multiple tablets**: SQLite serializes writes; the conditional
  `UPDATE ... WHERE state='waiting'` is what makes the 409 path correct
  under that serialization — no additional locking needed at this scale
  (3 restaurants × 40 entries/night).
- **No Docker**: onboarding is a plain `uv sync` + `npm install`; the
  `/juliopy` Makefile still gives a one-command `make dev`, just without a
  container.
- **Position is recomputed on every poll via list index**: fine at pilot
  scale (≤40 waiting rows per restaurant); would need a real rank query (or
  an index on `(restaurant_id, state, joined_at)`) before the 150-location
  rollout, not for this demo.

## Requirement coverage

| Spec requirement | Plan section |
|---|---|
| FR1 seeded restaurant | Data/API changes; `seed.py` |
| FR2 guest joins | Endpoints: `POST .../waitlist`; `Join.tsx` |
| FR3 waiting entry + token | Data model; repository insert |
| FR4 guest polls every 5s | Frontend polling hook; `Status.tsx` |
| FR5 FIFO position while waiting | Position query (read-time, not stored) |
| FR6 host polls every 5s, ordered list | `GET /restaurants/{id}/waitlist`; `Host.tsx` |
| FR7 host calls an entry | `POST /waitlist/{entry_id}/call` |
| FR8 conditional waiting→called | Conditional UPDATE in repository |
| FR9 called guest sees no position | Service: `get-status` omits position when `called` |
| FR10 concurrent call → one 409 | Conditional UPDATE + affected-row check; concurrency test |
| FR11 position not stored | Position query design |
| FR12 El Libro shape only, no runtime dependency | `seed.py`, static fixtures |
