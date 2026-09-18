# Digital Waitlist — Frontend

React + TypeScript (Vite) frontend, styled with Tailwind CSS, for the
Digital Waitlist pilot. See `../specs/001-digital-waitlist/` for the spec,
plan, and tasks, and `../backend/README.md` for running the API this
depends on.

## Prerequisites

- [Node.js](https://nodejs.org/) (with npm).
- The backend running — see `../backend/README.md`. Without it, the app
  loads but every request (join, status, host queue) will fail.

## Running locally

```
npm install
npm run dev
```

Requires the backend running at `http://localhost:8000` (see
`../backend/README.md`) — override with `VITE_API_BASE_URL` in `.env` if
it's running elsewhere.

## Routes

| Route | Page | What to test there |
| --- | --- | --- |
| `/` | Join | Submit name/phone/party size for the single pilot restaurant; on success, navigates to `/status/:token`. |
| `/status/:token` | Status | The guest's live view — polls every 5s, shows FIFO position while `waiting`, switches to "table ready" once called. Reach it directly with any valid token from a join response. |
| `/host` | Host | The host's queue view — polls every 5s, lists all `waiting` entries in join order, and calls the next party via "Llamar" (surfaces a conflict message if it's already been called elsewhere). |

To exercise the full flow: open `/host` in one tab, `/` in another, join a
guest, watch them appear on the host page within 5s, then click "Llamar"
and watch the guest's `/status/:token` tab flip to the called state on its
next poll.

## Common commands

| Command | What it does |
| --- | --- |
| `npm run dev` | Start the dev server with hot reload |
| `npm run build` | Type-check (`tsc -b`) and build for production |
| `npm run lint` | Run oxlint |
| `npm run preview` | Serve the production build locally |

## Environment variables

`VITE_API_BASE_URL` — the backend's base URL. Defaults to
`http://localhost:8000` if unset, so `.env` is optional for the standard
local setup; copy `.env.example` to `.env` only if the backend runs
somewhere else.

## Project structure

```
src/
  App.tsx          # routes
  pages/            # Join, Status, Host — one file per route
  api/
    client.ts        # typed fetch helpers + the 5s polling hook
```
