# Digital Waitlist

A digital waitlist for restaurants with heavy walk-in traffic: a guest
joins from their phone and tracks their live position; a host manages the
queue from a shared tablet and calls the next party. This is a **local-
only pilot demo** for a single restaurant — no Docker, no cloud, no auth.
See `specs/001-digital-waitlist/` for the spec, plan, and tasks behind it,
and `docs/` for the AI session log this was built with.

The project is two independent local services:

- **`backend/`** — FastAPI + SQLite, port `8000`.
- **`frontend/`** — React + TypeScript (Vite) + Tailwind, port `5173`.

Each has its own README with full detail. This is just the fastest path
to running both together.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages the backend's Python version,
  virtualenv, and dependencies.
- [Node.js](https://nodejs.org/) (with npm) — for the frontend.

## Quick start

In one terminal:

```
cd backend
cp .env.example .env
make migrate
make seed
make dev
```

In another terminal:

```
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** — that's the guest join page for the
one seeded restaurant. The host queue view is at
**http://localhost:5173/host**. Full route list and a suggested two-tab
test flow are in `frontend/README.md`.

## Where to look next

| Question | Where |
| --- | --- |
| What does this do and why these scope boundaries? | `specs/001-digital-waitlist/spec.md` |
| How is it built (stack, layering, testing strategy)? | `specs/001-digital-waitlist/plan.md` |
| What's done vs. left? | `specs/001-digital-waitlist/tasks.md` |
| Backend commands, env vars, project structure | `backend/README.md` |
| Frontend routes, what to test where | `frontend/README.md` |
