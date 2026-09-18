# Digital Waitlist — Frontend

React + TypeScript (Vite) frontend for the Digital Waitlist pilot. See
`../specs/001-digital-waitlist/` for the spec, plan, and tasks, and
`../backend/README.md` for running the API this depends on.

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

---

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.
