# Digital Waitlist — Spec

## Overview

Restaurants with heavy walk-in traffic currently run their Friday waitlist on
paper: names get lost, guests leave without telling anyone, and the host
can't keep up. This feature replaces that notebook with a digital waitlist
for a single restaurant, as a demo for a three-week pilot.

A guest joins the queue from their phone, watches their position update
live, and is notified in-app when their table is ready, with a chance to
confirm or cancel. The host runs the queue from a shared tablet at the door:
seeing who's waiting, calling the next party, and marking them seated.

This is explicitly a demo/pilot build, not the final production system: it
runs locally for one restaurant, with no real messaging provider and no
cloud deployment. See Non-goals.

## User stories

1. **Guest joins the queue.** A walk-in guest opens the join page (reached
   via a link/QR at the door, out of scope to generate), enters their name,
   phone number, and party size, and joins the waitlist for the restaurant
   tied to that page.

2. **Guest tracks their status.** After joining, the guest sees a live view
   of their position in the queue, without needing to refresh manually.

3. **Guest gets called.** When the host calls the guest's party, the guest's
   status page updates to show their table is ready, with two choices:
   "I'm on my way" or "I'm not coming." Their response is recorded.

4. **Guest doesn't respond in time.** If the guest neither confirms nor
   cancels within the call window, they are automatically marked as a
   no-show — no host action required.

5. **Host manages the queue.** A host on a shared tablet sees the current
   waiting list for their restaurant: name, party size, and how long
   they've been waiting. The host can call the next party ("Llamar") and,
   once the party has arrived, mark them seated ("Sentar").

6. **Two hosts work the same door.** On a busy Friday, two hosts may act on
   the tablet at the same time. If both try to act on the same guest, only
   the first action succeeds; the second host is told the action no longer
   applies and their view updates to the current state.

## Functional requirements

1. The application is seeded with one restaurant.
2. A guest joins by submitting name, phone number, and party size.
3. Joining creates a waitlist entry in the `waiting` state and returns an
   unguessable private status token.
4. The guest status page uses that token and polls every five seconds.
5. While waiting, the guest sees their FIFO position among waiting entries.
6. The host page polls every five seconds and shows all waiting entries,
   ordered by `(joined_at, id)`.
7. The host can call a specific waiting entry, scoped to their restaurant —
   an entry belonging to a different restaurant cannot be called.
8. Calling conditionally transitions that entry from `waiting` to `called`
   and records `called_at`, only when the entry belongs to the requested
   restaurant.
9. A called guest sees that their table is ready; queue position is no
   longer shown.
10. If two hosts call the same entry, only one update succeeds. The second
    request returns `409 Conflict`, displays an explanatory message, and
    refreshes the queue.
11. Position is calculated dynamically and is not stored.
12. El Libro has no runtime role; the seeded restaurant only reflects its
    data shape.

## Non-goals

Pulled directly from the client's stated Out of Scope, plus the two demo
constraints agreed for this spec:

- QR code generation. The join page is associated with a single,
  pre-selected restaurant rather than resolved dynamically from a scanned
  code.
- Elapsed-time display and animation of position changes on the guest's
  status view.
- Estimated wait time for the guest. Only live position is shown; there
  isn't yet enough historical data to produce a meaningful estimate.
- Real WhatsApp or SMS delivery. The "table ready" notification is an
  in-app state change on the guest's already-open status page, not a
  message sent through a provider.
- End-of-day report.
- Drag-and-drop reordering or manual queue prioritization by the host.
- Cloud deployment (Google Cloud / Cloud Run) and containerization — this
  demo runs locally.
- Multi-restaurant selection UI — only one restaurant is served by the join
  page for this pilot, even though the data model may hold more.
- Cross-device or cross-session recovery of a guest's status page. The
  private status link is the only way back in; if it's lost, the guest asks
  the host, who can look them up on the tablet queue view.
- Live integration with El Libro. Its data only informs the shape of
  one-time seed fixtures.
- Table and reservation data or assignment. The demo does not assign guests
  to specific tables, so only restaurant identity is needed from El Libro's
  data — not its tables or reservations.
- Host authentication/login — the tablet is treated as a trusted, shared
  device for the restaurant, consistent with there being no login screen in
  the prototype.
- Rejoining the waitlist. A guest whose entry reaches a terminal state
  (`cancelled`, `no_show`, or `seated`) has no in-app way to create a new
  entry for this demo.

## Open questions

None remaining that would change scope. Two smaller, non-scope-affecting
items are left as explicit assumptions rather than blocking questions:

- **Call window length**: assumed to be 10 minutes, matching the copy shown
  in the prototype's WhatsApp screen ("Tienes 10 minutos para acercarte a la
  entrada").
- **Exact copy/wording** for the in-app "table ready" screen and button
  labels: assumed to match the prototype's Spanish copy ("Voy en camino" /
  "Ya no voy") unless told otherwise.


## Implementation instructions

Build only the required vertical slice:

1. Seed one restaurant.
2. Guest joins with name, phone number, and party size.
3. Backend creates a `waiting` entry and returns an unguessable status token.
4. Guest status page polls every five seconds and displays queue position.
5. Host page polls every five seconds and displays waiting entries.
6. Host calls a specific entry.
7. Backend conditionally transitions `waiting → called`.
8. Guest status page displays the called state.
9. Concurrent actions on the same entry result in one success and one
   `409 Conflict`.

Use FastAPI, React with TypeScript, SQLAlchemy, and SQLite.

Do not implement:

- Guest confirmation or cancellation.
- Automatic no-show processing.
- Seating actions.
- Estimated wait time.
- Background tasks.
- WebSockets or SSE.
- WhatsApp or SMS.
- Table assignment.
- Rejoining or status recovery.
- Host authentication.
- Multiple restaurants.
- El Libro integration.
- Reports.
- Docker or cloud deployment.

The data model may reserve timestamps or states for later lifecycle work,
but do not expose unused endpoints or UI controls.
