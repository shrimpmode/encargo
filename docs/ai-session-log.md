# AI session log — Digital Waitlist

This documents the AI-assisted session that took the client brief
(`task.md`) and prototype screens through spec, plan, tasks, and a full
implementation, as an actual back-and-forth with Claude Code rather than a
plain changelog. Quotes are the user's own words, lightly trimmed.

## 1. Kicking off spec-driven development

**User:** invoked `/spec-driven-development` on `task.md` and `screens/`,
with constraints up front — no Docker, keep it local, use `/juliopy` for
scaffolding, break work into phases, and test only the core parts, not
every API.

**Claude:** read the brief and both prototype screenshots, then noticed
that most of the brief's own "missing decisions" list actually resolved
itself by cross-referencing its Out-of-Scope and Observations sections
(no-show is automatic per Observations; WhatsApp's real outcomes are moot
since real WhatsApp is out of scope; single restaurant is explicit). Three
genuinely scope-changing ambiguities were left, and Claude asked about
them directly instead of guessing:

- How should a guest recover their status page on another device? →
  **"Not supported for demo."**
- How deep should the El Libro integration go? → **"One-time seed
  fixtures (recommended)."**
- What happens when two hosts act on the same guest at once? → **"Surface
  the conflict (recommended)."**

**Claude:** wrote `specs/001-digital-waitlist/spec.md` from the brief plus
those three answers, and asked for sign-off before moving on.

## 2. Tightening the spec, one instruction at a time

Over several short turns, the user kept narrowing scope and Claude updated
the spec each time rather than batching changes:

- **"Estimated wait is out of scope for now, make sure to update the
  spec"** → removed ETA from the overview, the guest story, and the
  functional requirement; added it as an explicit non-goal with the
  reasoning (no historical data yet).
- **"Table and reservation data are excluded because the demo does not
  assign tables."** → trimmed the seed-data requirement down to
  restaurant-only, added a non-goal.
- **"guest and host should poll every 5s"** → made the polling interval an
  explicit, numbered requirement on both the guest and host views.
- **"Rejoining is out of scope"** → removed the rejoin requirement
  entirely and added a non-goal instead of leaving it implicit.

At some point the user also rewrote `spec.md` directly — replacing the
functional-requirements list with a much smaller, more explicit one and
adding an "Implementation instructions" section that pinned the stack
(FastAPI, React/TypeScript, SQLAlchemy, SQLite) and spelled out a
minimal vertical slice, with a firm "do not implement" list (no
confirm/cancel, no automatic no-show, no seating, no reports, no auth, no
Docker). Claude treated that as authoritative going forward rather than
re-litigating it.

## 3. From spec to a plan and phased tasks

**User:** **"create implementation phases given the spec."**

**Claude:** pointed out that a plan hadn't been written yet, and that
writing it would be quick since the spec's own "Implementation
instructions" had already made most of the technical calls. Wrote
`plan.md` (repository/service layering, `/juliopy` scaffold with Postgres
swapped for SQLite and Docker dropped entirely, conditional-UPDATE
concurrency strategy, a requirement-coverage table) and `tasks.md` — six
phases, each a runnable vertical slice, presented together for review.

Three more corrections followed, each folded into both `plan.md` and
`tasks.md`:

- **"Lets only test the status changes transitions, concurrent calls / Do
  not test models, services only core logic"** → cut the testing plan down
  to exactly two automated tests in the whole project: the call
  transition and the concurrency race. Everything else — models,
  repositories' read queries, services, endpoints, all frontend — became
  "verified by running the app" instead of test-first.
- **"updates to an entry should be scoped to a restaurant"** → added
  `restaurant_id` to the call endpoint's path and to the conditional
  `UPDATE`'s `WHERE` clause, and changed the conflict response so a
  cross-restaurant call isn't distinguishable from an already-called
  entry (avoids leaking which entries exist elsewhere).
- **"Since it's only 40 users the position calc is viable by index"** →
  collapsed two separate repository queries (guest position, host queue)
  into one shared `list_waiting` method, with position computed as a
  simple list index instead of a SQL rank/window function.

## 4. Building it, phase by phase

**User:** **"Implement phase 0-1."**

**Claude:** ran the `/juliopy` scaffold skill for the backend, explicitly
overriding its Docker/Postgres defaults per the plan; scaffolded the
frontend with Vite's `react-ts` template; built the `Restaurant` and
`WaitlistEntry` models with an Alembic migration; wrote the one-time seed
script. Along the way it caught and removed two pieces of scaffold noise
that weren't intentional: `uv init`'s placeholder `main.py`, and a nested
git repo that `uv init` had silently created inside `backend/` (removed
before it could cause a gitlink surprise once the whole project went under
one repo).

**User:** **"Git Repository remote added / Do not include screens in the
push."**

**Claude:** added a root `.gitignore` excluding `screens/`, checked what a
full `git add -A` would actually sweep in, and made the initial commit —
holding off on pushing to ask first, since the very first push to a shared
remote is exactly the kind of action worth a quick confirmation rather
than assuming.

**User:** ran `/ship-pr` with **"Push the changes, validate sensitive data
before running the next phases."**

**Claude:** ran the full secret scan and gitignore audit (found and fixed
a real gap — `.env` was only excluding the exact filename, not
`.env.local`/etc., and the tool caches were relying on their own
self-generated `.gitignore`s rather than the project's own). Then, since
the remote had zero branches yet, pushed `main` directly rather than
forcing an empty-base PR that GitHub can't actually create — and said so,
rather than silently deviating from the usual branch-and-PR flow.

**User:** **"Implement phase 2 / No commit / Validate against a
definition of done or acceptance criteria."**

**Claude:** invoked the `implement` skill, wrote out the acceptance
criteria before touching code, built the join endpoint and the frontend
Join page, and then went further than a happy-path check: called the
repository and service layers directly (not just through the HTTP
endpoint), simulated the exact CORS preflight and `Origin` header a real
browser would send, and confirmed the SPA route resolved. It also asked to
use browser automation for a real click-through; the user declined the
Chrome extension, so Claude flagged that one criterion — the literal
click → navigate → render sequence — as unverified rather than assuming it
worked, in the checklist it reported back.

**User:** **"Create a PR."**

**Claude:** branched `feat/guest-join` off `main`, re-ran the secret and
gitignore validation over the actual diff, staged only those files, and
opened PR #1 — carrying the same acceptance-criteria checklist into the
PR description, including the one flagged gap.

## 5. The pattern repeats, and a merged-branch surprise

**User:** ran `/implement phase 3-4`.

**Claude:** implemented the status/position endpoint and the host queue
view, reusing the shared `list_waiting` query as planned. To prove the
position logic actually worked (not just that it compiled), it joined
three guests, then directly flipped one entry's state to `called` in the
database — bypassing the not-yet-built call endpoint — to prove
`list_waiting` excluded it and that the guest behind it saw their position
correctly drop.

**User:** ran `/ship-pr` again, no extra instructions this time.

**Claude:** checked the current branch first and found that PR #1 had
already been merged by the user outside the session — `main` had moved.
Rather than pile more commits onto an already-merged branch, it cut a
fresh branch off the updated `main`, carried the uncommitted work onto it
cleanly, and opened PR #2 — explaining the branch-naming decision instead
of just doing it silently.

## 6. Finishing the slice

**User:** ran `/implement rest of the phases`.

**Claude:** found PR #2 had also been merged, branched again off updated
`main`, and implemented the concurrency-sensitive core: a conditional
`waiting → called` transition scoped to a restaurant, and the one
concurrency test the whole project actually needed — two simultaneous
call attempts on the same entry via real `asyncio` concurrency, asserting
exactly one succeeds. It wrote both tests first (confirmed they failed for
the right reason before any implementation existed), and then went a step
further: deliberately broke the guard in the implementation to confirm
the tests would actually catch that break, rather than trusting that a
passing test meant a correct test. Both did.

It then walked the full golden path and conflict path end to end with both
servers running — join, watch position drop as an earlier guest gets
called, see the called guest's status flip, see a repeat or
cross-restaurant call get rejected with `409` — using requests carrying
the real browser `Origin` header, and reported the one recurring,
consistent gap across every phase: no Chrome automation was available this
session, so no live browser click was directly observed, even though
everything underneath the UI was verified with real dynamic data.

**User:** ran `/ship-pr` once more.

**Claude:** opened PR #3, completing all six phases of `tasks.md`.

## What this session actually shows

The spec, plan, and tasks weren't written once and executed blindly — they
were corrected repeatedly, in small turns, and each correction was
propagated to every artifact it touched (spec → plan → tasks →
implementation) rather than left to drift. Testing scope, in particular,
was deliberately narrowed twice by the user down to exactly two tests in
the whole codebase, and Claude respected that boundary throughout instead
of "helpfully" adding more coverage. Where a check genuinely couldn't be
performed — a live browser interaction, with no browser tool available —
that was reported as a gap in the final checklist each time, not glossed
over.
