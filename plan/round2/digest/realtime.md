# realtime — Multiplayer & Realtime
PHASE P1 prio 1 dependsOn ['identity', 'data-layer']
SUMMARY: Yjs via Hocuspocus for documents, presence and multi-window sync; Electric shapes for live records; conflict and offline UX.
DESC: Goal: every PaperOS app is multiplayer by default, for humans and agents. A self-hosted Hocuspocus server persists Yjs documents to Postgres with auth hooks, powering collaborative rich text, canvas and presence (cursors, avatars, selections, who is viewing). Record changes stream through Electric shapes and reconcile with local writes; a conflict UX handles stale data and merges. State syncs across multiple OS windows and tabs, agents appear as live participants, and follow mode supports support and pair review. Load tests and an offline write queue harden it. Non-goal: a custom CRDT or peer-to-peer transport.
MILESTONES: ['Yjs server and presence 2026-09-22: Hocuspocus deployed, CRDT ADR, presence, collaborative text', 'Record sync and conflict UX 2026-09-26: Electric record streaming, conflict UX, multi-window sync', 'Scale and offline tested 2026-09-30: Agent presence, load test, offline queue, follow mode']


## PAP-139 [P0 Research S prio2 Ready for Claude] Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR
key=realtime/realtime-research milestone=Yjs server and presence agent=Builder: Scout (Library Evaluator sub-agent) with Nova (CRDT
blockedBy=[] blocks=[]
GOAL: Confirm with measurements that Yjs is the right document CRDT for PaperOS before the Hocuspocus server, collaborative editor and canvas are built on it. The output is an ADR in the decision log plus a reproducible benchmark harness, so the choice can be reopened later with the same numbers if Loro or Automerge overtake Yjs.
SCOPE: In:

* Benchmark harness in `packages/collab/bench/` comparing `yjs` 13.6.x, `@automerge/automerge` 2.x (with `automerge-repo`) and `loro-crdt` 1.x.
* Workloads: (a) rich-text doc of 200k characters with 50k random edits, (b) canvas map of 10k shapes with 20k property updates, (c) 50 simulated peers editing concurrently for 60s with 200 ms artificial latency.
* Metrics: encoded document size, load time from snapshot, memory after load, per-op apply time (p50/p99), merge time of two divergent 10k-op histories, WASM bundle size gzipped, TypeScript typing quality, ecosystem (editor bindings for Tiptap and tldraw, server persistence options, presence/awareness support, licence).
* ADR `docs/decisions/00xx-document-crdt.md` following the template from `collab/decision-log` (status, context, options, decision, consequences, reopen criteria).
* Registry entries for all three libraries in `libra
SPEC(first 1200): * Harness is a Vitest bench file (`vitest bench`) plus a Node script `pnpm bench:crdt --out results.json` that runs all three implementations behind one interface `CrdtAdapter { create(); applyText(pos, text); deleteText(pos, len); setShape(id, props); encode(); load(bytes); merge(other) }`.
* Results table generated as Markdown (`bench/results.md`) and committed; numbers must come from a fresh run on the CI runner class (`ubuntu-latest`, Node 22) so they are comparable with later reruns.
* Scoring uses the rubric from `libraries/eval-rubric` (licence, maintenance, bundle size, a11y n/a, TS quality, agent-friendliness) with weights recorded in the ADR.
* The ADR must state explicit reopen criteria, for example "Loro ships stable Tiptap and tldraw bindings and beats Yjs on p99 apply time by 2x".
* Recommend the Yjs persistence encoding (`Y.encodeStateAsUpdateV2`) and the snapshot cadence the server should use; this feeds `realtime/yjs-server`.
DOD:
* `pnpm bench:crdt` runs on CI in under 10 minutes and writes `results.json` and `results.md`.
* All three workloads produce numbers for all three libraries (no "n/a" without an explanation).
* ADR merged with status `accepted`, linked from the decision log index and from the `realtime` project description.
* Registry updated with three entries and owners.
* Unit test asserting the adapter interface behaves identically (same final text) across implementations for a deterministic edit script.
* Linear comment on the issue with the results table, the ADR link and a one-paragraph recommendation.
* Changelog entry under `docs/changelog/` (developer audience).
EDGE:
* WASM initialisation must be awaited before timing; exclude it from per-op numbers but report it separately.
* Automerge text uses different offset semantics (UTF-16 vs grapheme); the adapter must normalise or document the difference.
* Garbage collection differences (Yjs `gc: true`) change encoded size; benchmark with GC on and off.
* Memory measurements need `--expose-gc` and a forced GC before reading `process.memoryUsage()`.
* Loro version churn: pin exact versions in `bench/package.json` and record them in the ADR.
* Runner noise: run each workload 5 times and report the median.
DEPS: * `libraries/eval-rubric` for the scoring rubric (use the draft if not yet merged).
* `collab/decision-log` for the ADR template; if unavailable, use `docs/decisions/TEMPLATE.md` from `forge/vcs-decision-adr`.
* Feeds `realtime/yjs-server`, `realtime/collab-text`, `collab/canvas-view`.


## PAP-140 [P0 Infra M prio1 Backlog] Deploy a Hocuspocus (Yjs) server with auth hook, Postgres persistence and room-per-document
key=realtime/yjs-server milestone=Yjs server and presence agent=Builder: Forge (Ops Runner sub-agent) for deployment and per
blockedBy=['PAP-25', 'PAP-57'] blocks=['PAP-147', 'PAP-145', 'PAP-142', 'PAP-141', 'PAP-132', 'PAP-131']
GOAL: Stand up the multiplayer backbone: a self-hosted Hocuspocus server that authenticates every WebSocket connection with a Better Auth session or agent API key, persists one Yjs document per room to Postgres, and enforces per-document read/write permissions. Every later realtime feature (presence, collaborative text, canvas, multi-window) connects to this server.
SCOPE: In:

* `apps/collab-server/` (Node 22, TypeScript) running `@hocuspocus/server` 3.x with extensions `@hocuspocus/extension-database` (custom Postgres store via Drizzle), `@hocuspocus/extension-logger`, `@hocuspocus/extension-throttle`, and `@hocuspocus/extension-redis` behind a flag for horizontal scaling.
* Room naming `doc:<tenantId>:<entityType>:<entityId>`; one Yjs doc per room; awareness enabled.
* Auth hook (`onAuthenticate`) validating a Better Auth session token or `pos_agent_` API key, resolving a principal, and calling the permission engine for `document.read` / `document.write`; read-only connections get `connection.readOnly = true`.
* Persistence: table `yjs_documents(room text pk, tenant_id uuid, state bytea, vector bytea, updated_at, size_bytes)` plus `yjs_updates` append log (compacted into `state` every 500 updates or 60 s, whichever first). RLS by tenant per `data-layer/
SPEC(first 1200): * Server config: `port 1234`, `timeout 30000`, `debounce 2000`, `maxDebounce 10000`, `quiet true`; `onLoadDocument` reads `state` from Postgres, `onStoreDocument` writes `Y.encodeStateAsUpdateV2`; `onChange` appends to `yjs_updates`.
* Token passed as `token` in the provider handshake; server verifies via `packages/auth` `verifySessionToken()` or `verifyApiKey()`; `context` carries `{ principalId, principalType, tenantId, scopes }` used by all later hooks.
* Permission check reuses `packages/permissions` `can(principal, action, resource)`; resource derived from the room name; unknown entity types are rejected (`4403`).
* Limits: 2 MB max message, 20 MB max document (reject with `4413` and emit `collab.document.too_large`), 100 connections per principal.
* Room lifecycle: unload after 30 s with zero connections; `DELETE /admin/rooms/:room` (admin scope) forces unload and snapshot.
* Env via `app-shell/env-config`: `COLLAB_DATABASE_URL`, `COLLAB_REDIS_URL?`, `COLLAB_PUBLIC_URL`, `AUTH_BASE_URL`.
* Docs: `docs/platform/realtime/server.md` with a sequence diagram (connect, auth, load, sync, store) and a runbook.
DOD:
* `docker compose up collab-server` connects from `apps/web` on localhost; two browsers editing a `Y.Text` converge.
* Vitest integration tests: auth rejects expired token, read-only principal cannot write (update dropped and logged), persistence round-trip after server restart, compaction reduces `yjs_updates` rows.
* RLS test proves tenant A cannot load tenant B's room even with a forged room name.
* Deployed on the VPS at `wss://collab.<domain>` with TLS; `/healthz` monitored by `data-layer/observability`.
* Metrics visible on a Grafana panel; screenshot attached to the PR.
* Provider reconnects within 5 s after the server restarts (Playwright test toggles the container).
* Docs, changelog entry, and a Linear comment with the wss URL and demo instructions.
EDGE:
* Token expires mid-session: server sends `4401`, provider refreshes the session via Better Auth and reconnects without losing local edits.
* Postgres unavailable on `onStoreDocument`: retry with backoff, keep the doc in memory, alert after 3 failures; never drop updates silently.
* Two server instances without Redis: reject start with a clear error when `REPLICAS > 1` and no Redis URL.
* Client sends updates for a room it authenticated for but whose permission has since been revoked: re-check permissions every 5 minutes and on `permission.changed` events.
* Corrupt state blob: fall back to replaying `yjs_updates`; if that fails, quarantine the row and start empty with an audit event.
* Room names with unexpected characters or over 255 bytes are rejected.
DEPS: * `identity/better-auth` (session/API-key verification), `identity/rbac-abac` (permission engine), `data-layer/drizzle-schema` and `data-layer/rls-tenancy` (tables and policies), `app-shell/env-config` (secrets), `realtime/realtime-research` (encoding decision). Consumed by `realtime/presence`, `realtime/collab-text`, `collab/canvas-view`, `realtime/multi-window-sync`.


## PAP-141 [P1 Build M prio1 Backlog] Build the presence layer: cursors, avatars, selections and 'who is viewing' across pages
key=realtime/presence milestone=Yjs server and presence agent=Builder: Nova (CRDT Engineer sub-agent). Reviewer: Iris (Com
blockedBy=['PAP-140'] blocks=['PAP-149', 'PAP-146']
GOAL: Make every PaperOS page show who is here: live cursors, selection highlights, avatar stacks and a "who is viewing" indicator that works on any page, not only inside editors. Presence rides on Hocuspocus awareness so it needs no extra infrastructure, and it is the foundation for agent presence and follow mode.
SCOPE: In:

* `packages/collab/src/presence/` with a `PresenceProvider` (React context) that joins an awareness room per page (`page:<tenantId>:<routeId>`) and optional per-entity rooms.
* Awareness payload schema (Zod): `{ principalId, principalType: 'human'|'agent', name, avatarUrl?, color, cursor?: { x, y, elementId? }, selection?: { entityId, fieldId? } | { from, to }, viewport?, focusedRoute, lastActive, idle: boolean }`.
* Components in `packages/ui` (built on `design-system/data-display` AvatarStack): `PresenceAvatars` (max 5 + overflow count, tooltip with names), `LiveCursor` (name label, fades after 4 s idle, hidden on touch devices), `SelectionHighlight` (outline colour per user around a row, cell or block), `ViewersBadge` ("3 viewing" pill for list items).
* Colour assignment: deterministic palette of 12 accessible colours from `design-system/tokens` chosen by hashing `principalId`.

SPEC(first 1200): * Awareness updates throttled to 50 ms for cursor, immediate for selection and route changes; cursor coordinates are relative to the nearest `[data-presence-surface]` element so they survive resizes and different window sizes.
* Presence rooms authenticate through the same provider as `realtime/yjs-server`; the room stores no persistent document (server flag `ephemeral: true` skips persistence).
* Privacy: customers see only staff and agents assigned to them plus other members of their own organisation, decided by `packages/permissions` action `presence.view`; staff see everyone in the tenant. Names shown are display names from `identity/audience-model`.
* Per-page opt-in via page spec field `realtime.presence: true|false` (default true for staff surfaces, false for customer surfaces) read from `spec-builder/schema`.
* Accessibility: avatar stack has `aria-label="3 people viewing: Ada, Bo, Forge (agent)"`; cursors are `aria-hidden`; a visually hidden live region announces joins and leaves at most once per 10 s.
* Multi-window: the same user in two windows appears once (dedupe by `principalId`, show a small "x2" badge).
* Storybook stories for all four components in light, dark and 
DOD:
* Two browsers on the same page show each other's avatar within 1 s and cursor movement under 100 ms on localhost.
* Vitest tests for payload validation, colour hashing stability, idle transitions and dedupe.
* Playwright test with two contexts asserting avatars and selection highlights render at 375, 1024 and 1920 px; screenshots attached.
* Storybook stories published; axe passes on each.
* Permission test: customer context cannot see another customer's presence.
* Docs page `docs/platform/realtime/presence.md` with the payload schema and page-spec flag.
* Changelog entry and Linear comment with a demo link (GitHub Pages Storybook and staging URL).
EDGE:
* 50+ viewers on one page: stack shows 5 avatars + "+45" and the tooltip lists the first 20 with "and 25 more".
* Cursor over a scrolled container: coordinates are surface-relative, so scrolling in one window does not move cursors in another.
* User loses connection: their avatar dims after 5 s and disappears after 30 s (awareness timeout).
* Very long display names truncate to 24 characters with full name in the tooltip.
* Reduced motion: cursor movement is not animated; joins do not pulse.
* Same principal in three windows and a tab that is hidden: counts as one active viewer if any window is active.
DEPS: * `realtime/yjs-server` (awareness transport), `design-system/data-display` (AvatarStack, Badge), `design-system/tokens` (palette), `identity/rbac-abac` (`presence.view`), `spec-builder/schema` (page flag, optional at first). Consumed by `realtime/agent-presence`, `realtime/followmode`, `tables/grid-view`, `collab/canvas-view`.


## PAP-142 [P1 Build M prio1 Backlog] Add collaborative rich text (Tiptap + Yjs) as the shared editor for docs and comments
key=realtime/collab-text milestone=Yjs server and presence agent=Builder: Nova (CRDT Engineer sub-agent). Reviewer: Sentinel 
blockedBy=['PAP-127', 'PAP-140'] blocks=[]
GOAL: Ship one collaborative rich-text editor that every PaperOS surface reuses: docs, comments, issue descriptions, notes fields in tables. It binds Tiptap to a Yjs document on the Hocuspocus server so multiple people and agents can edit simultaneously with live carets, and it degrades to a local-only editor when offline or when a field is not shared.
SCOPE: In:

* `packages/collab/src/editor/` exporting `<RichTextEditor room? value? onChange? readOnly placeholder mentions attachments />` built on `@tiptap/react` 3.x with `@tiptap/starter-kit`, `@tiptap/extension-collaboration`, `@tiptap/extension-collaboration-caret`, `@tiptap/extension-mention`, `@tiptap/extension-link`, `@tiptap/extension-placeholder`, task lists, tables, code blocks with `lowlight` highlighting, and image nodes uploading through `data-layer/file-storage`.
* Two modes: `room` given means Yjs-backed via `createDocProvider` from `realtime/yjs-server`; no room means controlled local editor with JSON value (same schema).
* Toolbar and bubble menu built from `design-system/primitives` (Button, Menu, Tooltip) with all actions registered in `input/command-registry` (`editor.bold`, `editor.link`, ...), so shortcuts and the command palette work.
* Mentions of users, agents and ent
SPEC(first 1200): * Yjs mapping: `Y.XmlFragment` named `default` inside the room document; the same room may host other fragments (canvas, metadata).
* Caret colours and names come from `realtime/presence` payload; agents show a distinct caret style defined later by `realtime/agent-presence` (use a dashed caret for `principalType === 'agent'` now).
* `readOnly` derives from the provider's `connection.readOnly` when collaborative; the toolbar hides and a `Badge` reads "View only".
* Content JSON schema exported as `richTextSchema` (Zod) in `packages/core` for storing non-collaborative fields in Postgres `jsonb` columns; a `renderRichText(json)` server-side renderer produces sanitised HTML (via `@tiptap/html` plus `sanitize-html`) for emails and PDFs.
* Undo/redo uses `y-undo-manager` scoped to the local user's changes (`trackedOrigins`), bound to the registry commands `edit.undo`/`edit.redo`.
* Accessibility: `role="textbox"` with `aria-multiline`, toolbar `role="toolbar"` with roving tabindex from `input/focus-management`, all buttons labelled; link dialog is a `Dialog` primitive.
* Performance: 100k-character document types with no dropped frames at 60 fps on a mid-range laptop; measured in the Pla
DOD:
* Two browsers editing the same room converge and show each other's carets; offline edits in one browser merge on reconnect (Playwright test with network offline).
* Vitest tests for markdown round-trip, mention insertion, schema validation and the server renderer sanitising script tags.
* Storybook stories for all variants at 320, 768 and 1280 px with axe passing.
* Toolbar actions appear in the command palette with correct shortcuts.
* Docs `docs/platform/realtime/editor.md` with usage for both modes.
* Changelog entry, Linear comment with Storybook link and a 20-second video of two-cursor editing from `quality/video-replays`.
EDGE:
* Pasting 5 MB of HTML from Word: strip styles, cap at 1 MB, and toast the truncation.
* Image upload fails: keep a placeholder node with a retry action; never lose the surrounding text.
* Mention of a user who later loses access: render as plain text with a tooltip "no longer has access".
* Room switches while the editor is mounted (navigating between comments): destroy and recreate the provider; no stale content flashes.
* IME composition (Japanese, Korean) must not be broken by collaboration transforms; test with Playwright `keyboard.insertText`.
* Read-only user tries to type: no-op, brief toast once per session.
DEPS: * `realtime/yjs-server`, `collab/collab-research` (confirms Tiptap over BlockNote), `design-system/primitives`, `input/command-registry`, `data-layer/file-storage`, `realtime/presence`. Consumed by `collab/comments`, `collab/docs-engine`, `tables/field-types` (rich text field), `pm-linear/pm-data-model`.


## PAP-143 [P1 Build L prio1 Backlog] Stream record changes via Electric shapes to all connected clients and reconcile with local writes
key=realtime/record-sync milestone=Record sync and conflict UX agent=Builder: Nova (CRDT Engineer sub-agent) with Forge (Schema W
blockedBy=['PAP-36'] blocks=['PAP-148', 'PAP-144']
GOAL: Make every table, list and detail page update live when any human or agent changes a record, without a page refresh and without custom WebSocket code per feature. Electric shapes stream Postgres changes into each client's PGlite; this issue wires those streams into React, reconciles them with optimistic local writes, and defines how the UI learns that data changed under it.
SCOPE: In:

* `packages/sync/src/live/`: `useLiveQuery(query)` (PGlite live query over synced tables), `useShape(table, where)` (subscribe/unsubscribe with reference counting), and `useRecord(table, id)`.
* Reconciliation between the offline outbox from `data-layer/local-first-sync` and incoming shape rows: optimistic rows carry `_pending: true`; when the server row arrives with a matching `mutation_id` (set by the API on write), the optimistic row is dropped; if the server row differs from what the client expected, emit a `conflict` event consumed by `realtime/conflict-ux`.
* Shape registry additions for `tables/*` entities (`records`, `fields`, `views`) and PM entities from `pm-linear/pm-data-model`, each with a server-side `where` derived from tenant and permission.
* Change indicators: `useRecordChanges(id)` returns `{ changedFields, actor, at }` for 5 s after a remote change so cells can f
SPEC(first 1200): * Libraries: `@electric-sql/client` 1.x, `@electric-sql/pglite` 0.3.x with `live` extension, `@electric-sql/react`. Shapes are subscribed through the proxy `GET /api/sync/shape` with the Better Auth session; the proxy attaches `where tenant_id = $1` and, for restricted tables, a permission-derived predicate from `identity/rbac-abac`.
* Every write goes through oRPC (`data-layer/api-layer`); the API stamps `mutation_id uuid` and `updated_by principal_id` on the row so clients can match echoes and attribute changes.
* `mutate()` from `data-layer/local-first-sync` is extended with `expect: (before) => after` so the reconciler can compare the expected post-state to the server row field by field; mismatches list `conflictingFields`.
* Lag budget: remote change visible in other clients within 500 ms p95 on staging; measured by a Playwright test that writes via API and polls the DOM.
* Permission changes: when a shape's `where` would change (role edited), the server returns `409 shape-invalid`; the client drops and resubscribes.
* Memory: unsubscribe shapes 30 s after the last consumer unmounts; cap of 50 concurrent shapes per client with LRU eviction and a console warning.
DOD:
* Grid demo page: editing a cell in browser A updates browser B within 500 ms; screenshot pair attached at 768 and 1440 px.
* Vitest tests for reconciler: echo match drops optimistic row; mismatch emits conflict with correct fields; out-of-order arrival handled.
* Integration test with a real Electric container in CI (`ops/compose/test.yml`).
* Permission test: revoking access removes rows from the client within one resubscribe cycle.
* Dev inspector documented in `docs/platform/realtime/record-sync.md` with a data-flow diagram.
* Changelog entry and Linear comment with the staging demo link and lag measurement.
EDGE:
* Client offline for an hour returns with 300 outbox writes while 2,000 remote rows arrive: apply remote rows first, then replay outbox; conflicts surface per row.
* Row deleted remotely while the user is editing it: keep the editor open with a "deleted by X" banner and offer restore via audit log (`data-layer/audit-log`).
* Shape with 500k rows: server refuses shapes without a bounding predicate; the client must page via the views query compiler.
* Clock skew: never use client timestamps for ordering; use server `lsn`.
* Duplicate `mutation_id` echoes after a retry: idempotent drop.
* Schema migration adds a column: PGlite schema hash mismatch triggers a reset with a non-blocking toast.
DEPS: * `data-layer/local-first-sync` (PGlite, outbox, proxy), `data-layer/api-layer` (mutation stamping), `identity/rbac-abac` (predicates), `tables/query-compiler` (consumer, shares the shape registry). Consumed by `realtime/conflict-ux`, `realtime/offline-queue`, `tables/grid-view`, `pm-linear/board-views`.


## PAP-144 [P1 Spec S prio2 Backlog] Design conflict and stale-data UX: merge banners, last-writer indicators, undo
key=realtime/conflict-ux milestone=Record sync and conflict UX agent=Builder: Quill (Page Spec Writer sub-agent) with Iris (Compo
blockedBy=['PAP-143'] blocks=[]
GOAL: Specify how PaperOS tells a user that someone else changed what they are looking at or editing, and what they can do about it. The output is a written UX spec plus page-spec-ready component definitions so that `realtime/record-sync`, `realtime/offline-queue` and the tables engine implement one consistent behaviour instead of ad hoc alerts.
SCOPE: In:

* Spec document `docs/platform/realtime/conflict-ux.md` covering: field-level stale indicators, "updated by X just now" attribution, merge banner for form conflicts, last-writer-wins rules per field type, undo of a remote overwrite, offline pending states and failed-write recovery.
* Component definitions (props, states, copy) for `StaleFieldIndicator`, `ConflictBanner`, `RemoteChangeFlash`, `PendingWriteBadge`, `FailedWriteDialog`, each mapped to a spec component ID (`ui.conflictBanner` etc.) for `design-system/component-spec-mapping`.
* Decision table: for each field type from `tables/field-types` whether concurrent edits auto-merge (rich text via Yjs, multi-select union), last-writer-wins with attribution (number, date, single select), or require manual resolution (currency amounts over a threshold, status transitions).
* Copy deck in `packages/collab/src/copy/conflicts.ts` revie
SPEC(first 1200): * Trigger inputs come from `realtime/record-sync`: `conflict` events `{ recordId, conflictingFields, mine, theirs, actor, at }` and `useRecordChanges` for non-conflicting remote changes.
* Rules: if the user has not touched a field, a remote change applies silently with a 5 s flash and tooltip "Changed by Ada 3 s ago". If the user has a dirty local value in the same field, show `ConflictBanner` inline above the form section with two buttons: "Keep mine" (re-submit) and "Use theirs" (discard local), plus "Compare" opening a side-by-side sheet. Never block typing.
* Undo: after a remote value overwrote a non-dirty field, `Ctrl/Cmd+Z` inside that field restores the previous value as a new write (attributed to the current user), via `input/command-registry` command `edit.undoRemote`.
* Offline: `PendingWriteBadge` (clock icon) on saved-but-unsynced rows; on reconnect it resolves to a check for 2 s; failures open `FailedWriteDialog` with retry/discard/copy-to-clipboard.
* Agents: when the actor is an agent, attribution uses `ActorBadge` and links to the prompt log entry (`collab/prompt-log-ui`) so a human can see why.
* Accessibility: banner is `role="alert"` once, indicators are descri
DOD:
* Spec merged with the decision table covering every field type in `tables/field-types` (mark unknowns as "TBD with owner").
* Five component definitions with props (TypeScript interfaces), copy and spec IDs registered.
* Static Storybook stories for all five states at 375 and 1280 px, axe clean, screenshots attached.
* Follow-up Linear issues created in `tables`, `realtime` and `spec-builder` for implementation, linked from the spec.
* ADR-style rationale for last-writer-wins vs manual resolution recorded in `collab/decision-log`.
* Changelog (docs) entry and a Linear comment summarising the rules in ten lines with the Storybook link; the rules ride along in the next weekly release digest (`quality/review-report`) rather than opening a separate Needs Justin item.
EDGE:
* Three people edit the same field within a second: banner shows the latest actor and "and 1 other".
* Conflict on a field the user cannot see (hidden column): show a row-level indicator instead of nothing.
* Remote change arrives while a select dropdown is open: defer applying until it closes.
* Agent and human conflict where the agent wrote later: the human's "Keep mine" must still win and post a comment mentioning the agent.
* Status field transitions that are invalid after the remote change (e.g., "Done" to "In Progress" not allowed): show a validation error, not a conflict banner.
* Screen reader users: alerts must not fire more than once per record per 10 s.
DEPS: * `realtime/record-sync` (event shapes), `tables/field-types` (type list), `design-system/component-spec-mapping`, `design-system/data-display`, `collab/decision-log`. Consumed by `realtime/offline-queue`, `tables/grid-view`, `spec-builder/layout-codegen`.


## PAP-145 [P1 Build M prio2 Backlog] Sync state across multiple OS windows and tabs of the same user via BroadcastChannel and Yjs
key=realtime/multi-window-sync milestone=Record sync and conflict UX agent=Builder: Nova (CRDT Engineer sub-agent) with Forge (Tauri Sm
blockedBy=['PAP-21', 'PAP-140'] blocks=['PAP-23']
GOAL: Keep every window and tab of the same user coherent: a record edited in a detached inspector window on monitor two is instantly reflected in the main window on monitor one, selection and navigation can be shared, and the app never fights itself with duplicate connections. This is what makes the multi-monitor window manager from `app-shell/breakpoints-windows` feel like one application.
SCOPE: In:

* `packages/collab/src/windows/`: a `WindowBus` over `BroadcastChannel` (web and Tauri webviews sharing an origin) with a Tauri fallback via `@tauri-apps/api` `emit`/`listen` when webviews have different origins; typed message schema (Zod).
* Leader election (one window holds the Hocuspocus and Electric connections; followers proxy through the leader) using `navigator.locks` with a heartbeat fallback; re-election within 2 s when the leader closes.
* Shared state channels: `selection` (current entity/record), `navigation` (route changes with `follow` flag), `presence` (single awareness entry per user, aggregated across windows as required by `realtime/presence`), `auth` (sign-out propagates), `theme` and `keymap` changes.
* Yjs: followers connect to the leader's `Y.Doc` via `y-webrtc`-free in-process relay: leader forwards updates over the bus; each window still keeps `y-indexeddb` f
SPEC(first 1200): * Channel name `paperos:<tenantId>:<userId>`; messages `{ type, from: windowId, ts, payload }`; `windowId` is a UUID stored in `sessionStorage`.
* Leader duties: hold one `createDocProvider` per room and one Electric shape set; relay Yjs updates (`Y.encodeStateAsUpdate` diffs) and shape rows to followers; followers send writes to the leader, which forwards to the API; if the bus is unavailable, each window falls back to its own connections (logged as degraded).
* Navigation follow: when enabled, a follower window mirrors the main window's selected record into its own route (`/records/:id` inside an inspector layout) but keeps independent scroll and zoom.
* Conflict avoidance: the same record open for editing in two windows uses the same Yjs doc for rich text; for form fields the last window to blur wins and the other window shows the `RemoteChangeFlash` from `realtime/conflict-ux`.
* Tauri: `panel-<id>` windows from `app-shell/breakpoints-windows` load the same origin, so `BroadcastChannel` works; Android/iOS have a single window and the bus is a no-op.
* Performance: relaying 1,000 Yjs updates per second between three windows must not exceed 10% CPU on the leader (measured with th
DOD:
* Playwright test with three pages (same context) proving: one WebSocket connection to the collab server, edits propagate under 50 ms, closing the leader re-elects and reconnects without data loss.
* Tauri desktop manual run on Linux with a detached inspector on a second display, recorded as a video via `quality/video-replays`.
* Vitest tests for message schema, leader election and fallback.
* Screenshots at 1280 and 1920 px of main window plus detached panel; `WindowChip` visible.
* Docs `docs/platform/realtime/multi-window.md` with a sequence diagram of election and relay.
* Changelog entry and Linear comment with the video link.
EDGE:
* Two leaders after a laptop sleep: heartbeat conflict resolution picks the lowest `windowId` and the other demotes within one heartbeat.
* Private-browsing tab where `BroadcastChannel` or `navigator.locks` is unavailable: run standalone with a console warning.
* Sign-out in one window: all windows clear state and navigate to sign-in within 500 ms.
* Follower sends a write while leader is mid-reconnect: queue locally up to 1,000 messages then surface `PendingWriteBadge`.
* Different tenant selected in a second window: the bus is tenant-scoped, so windows simply do not talk; the tenant switcher warns when other windows exist.
* Window closed via task manager (no `beforeunload`): heartbeat timeout handles it.
DEPS: * `realtime/yjs-server`, `app-shell/breakpoints-windows` (detached windows, `list_displays`), `realtime/record-sync` (shape relay), `realtime/presence` (aggregation), `identity/better-auth` (sign-out event).


## PAP-146 [P2 Build S prio2 Backlog] Show agents as live participants (typing, editing, reviewing) with distinct visual identity
key=realtime/agent-presence milestone=Scale and offline tested agent=Builder: Nova (CRDT Engineer sub-agent) with Atlas (Dispatch
blockedBy=['PAP-60', 'PAP-141'] blocks=[]
GOAL: Make Claude agents visible collaborators everywhere a human would be: an agent editing a spec, typing a comment or reviewing a PR appears in presence with a distinct visual identity, its current activity and a link to what it is doing. This keeps the agent org honest and lets Justin and staff see machine work happening in real time rather than discovering it afterwards.
SCOPE: In:

* Extend the awareness payload from `realtime/presence` with `agent?: { character, subAgent?, issueKey?, activity: 'reading'|'editing'|'typing'|'reviewing'|'waiting', sessionId }`.
* `packages/agents/src/presence-client.ts`: a Node client used by the orchestrator session hooks (`agents/prompt-logging-hook`) to join presence rooms with the agent's `pos_agent_` key, set activity on tool calls (Edit → `editing`, Read → `reading`, PR review → `reviewing`) and leave on session end.
* Visual identity in `packages/ui`: `AgentAvatar` (character glyph and colour from `agents/character-schema`, square shape versus round human avatars, small "AI" corner mark), dashed live cursor and caret, `ActivityChip` ("Forge is editing page.spec.yaml · PAP-42").
* "Agents here" section in `PresenceAvatars` tooltip, and an `AgentActivityPanel` in the staff console shell listing active agents with links to t
SPEC(first 1200): * Activity mapping is a pure function `toolCallToActivity(tool, args)` with tests; unknown tools map to `waiting`; activity resets to `waiting` after 30 s without tool calls.
* Rooms: agents join `page:<tenant>:<route>` for the page they are editing when the tool touches a spec or page file mapped by `spec-builder/validator`'s route index; otherwise they join `issue:<tenant>:<issueKey>` so the PM board views (`pm-linear/board-views`) can show them on the card.
* Colour and glyph are read from the character registry generated by `agents/roster-v1` (`.claude/agents/*.md` frontmatter → `packages/agents/src/characters.json`).
* Customers never see agent cursors; when `agentPresence: all` they see only the avatar with the label "Assistant" (name mapping in `identity/audience-model`).
* Accessibility: `AgentAvatar` `aria-label="Forge (agent), editing"`; live region announces "An agent started editing this page" once.
* Attribution links: clicking an agent avatar opens a popover with character, sub-agent, issue link and "View session" (prompt log) if the viewer has `promptlog.read`.
DOD:
* Running an orchestrator session against staging shows the agent avatar on the target page and issue card within 2 s of the first tool call; screenshot at 1024 and 1920 px.
* Vitest tests for `toolCallToActivity`, payload validation and visibility rules per audience.
* Storybook stories for `AgentAvatar`, `ActivityChip`, `AgentActivityPanel` in three themes; axe clean.
* Permission test that a customer session cannot fetch agent details beyond "Assistant".
* Docs `docs/platform/realtime/agent-presence.md` and handbook note in `agents/character-docs`.
* Changelog entry and Linear comment with a video of an agent editing alongside a human.
EDGE:
* 20 parallel sessions on one issue: the card shows up to 3 agent avatars plus a count.
* Session crashes without leaving: awareness timeout removes it after 30 s; the panel marks it "lost".
* Same character in two sessions: distinct entries keyed by `sessionId`, labelled "Forge (2)".
* Agent edits a file with no route mapping: appears only on the issue, never on a wrong page.
* Character renamed mid-build: fall back to a neutral glyph if the registry lacks the key.
* Reduced-motion users: no pulsing on activity change.
DEPS: * `realtime/presence`, `identity/agent-principals` (keys, "Assistant" mapping), `agents/character-schema` and `agents/roster-v1` (glyphs, colours), `agents/prompt-logging-hook` (tool-call events), `pm-linear/board-views` (card slot).


## PAP-147 [P2 Review M prio2 Backlog] Load test 500 concurrent users per room and 10k rooms; tune persistence and scaling
key=realtime/load-test milestone=Scale and offline tested agent=Builder: Sentinel (Edge Case Hunter sub-agent) writes the ha
blockedBy=['PAP-140'] blocks=[]
GOAL: Find the real limits of the collab server and record sync before a tenant does: 500 concurrent users in one room and 10,000 active rooms across the cluster, with p95 latency and memory measured. Tune persistence, compaction and scaling knobs until the targets pass, and turn the harness into a nightly CI job so regressions are caught.
SCOPE: In:

* Load harness in `apps/collab-server/load/` using k6 (0.5x, `xk6-websockets` extension) for WebSocket rooms and a Node worker pool for Yjs-aware clients (k6 cannot run Yjs; workers use `@hocuspocus/provider` with `ws`).
* Scenarios: (a) one room, 500 clients, each typing 2 chars/s for 10 minutes; (b) 10,000 rooms, 2 clients each, one edit per 10 s; (c) reconnect storm: 2,000 clients reconnect within 5 s after a simulated server restart; (d) awareness-only: 1,000 clients moving cursors at 20 Hz.
* Electric shape load: 1,000 clients subscribed to a 100k-row `records` shape receiving 50 writes/s.
* Targets: p95 update propagation under 250 ms (scenario a), under 500 ms (b); server RSS under 4 GB for (b); no dropped updates; reconnect storm fully recovered under 60 s; zero data loss verified by comparing final `Y.Text` across all clients.
* Tuning outputs: Hocuspocus `debounce`/`maxDeb
SPEC(first 1200): * Harness entry `pnpm load:collab --scenario a --target wss://collab-staging.<domain> --duration 10m --out results/`; outputs JSON summary plus an HTML report (k6 `handleSummary`).
* Each client authenticates with a load-test agent key minted via `identity/agent-principals` (`scope: loadtest`, tenant `loadtest`), so RLS and auth are exercised too; the tenant is truncated after each run.
* Correctness check: workers append `${clientId}:${seq}` tokens; after quiescence every client's text must contain all tokens exactly once.
* Metrics scraped from `/metrics` (`realtime/yjs-server`) and Postgres (`pg_stat_statements`), stored under `results/<date>/` and compared to `load/baseline.json`; a regression over 20% fails the nightly job.
* Report template `load/REPORT.md`: target, result, pass/fail, knob changes, recommended max per instance, scaling formula (rooms per GB, connections per vCPU).
DOD:
* All four Yjs scenarios and the Electric scenario run against staging with results committed under `apps/collab-server/load/results/`.
* Targets met or, where not met, an ADR recording the accepted limit and a follow-up issue.
* Tuning commits each carry before/after numbers in the message.
* Nightly job runs green for three consecutive nights and posts a summary comment to this issue.
* Grafana dashboard screenshot attached to the PR.
* Docs `docs/platform/realtime/capacity.md` with the scaling formula and runbook for adding instances.
* Changelog entry (developer) and Linear comment with the report link.
EDGE:
* Load generator saturates first (CPU-bound workers): distribute across two runner machines and verify generator p95 separately.
* Postgres `yjs_updates` table grows to millions of rows in scenario (b): compaction must keep it under 1M; test vacuum behaviour.
* Redis fan-out adds latency for single-instance deployments; document the break-even point.
* Client clocks drift: measure propagation with server-echoed timestamps, not client clocks.
* Caddy default idle timeout closes quiet WebSockets: set `read_timeout` and verify scenario (b) survives 10 minutes idle.
* A run left the `loadtest` tenant dirty: harness refuses to start until cleanup completes.
DEPS: * `realtime/yjs-server` (target, metrics), `data-layer/observability` (Grafana), `identity/agent-principals` (keys), `realtime/record-sync` (Electric scenario), `pm-linear/webhooks` (result comments).


## PAP-148 [P2 Build M prio2 Backlog] Implement the offline write queue with retry, ordering and user-visible sync status
key=realtime/offline-queue milestone=Scale and offline tested agent=Builder: Nova (CRDT Engineer sub-agent). Reviewer: Sentinel 
blockedBy=['PAP-143'] blocks=[]
GOAL: Let customers keep working on a train, in a basement or on a flaky mobile connection: writes queue locally in order, retry intelligently, and the UI always tells the truth about what has and has not reached the server. This hardens the outbox that `data-layer/local-first-sync` introduced into a product-grade feature with visible sync status.
SCOPE: In:

* `packages/sync/src/outbox/` rewrite: durable queue in PGlite table `outbox(id, seq, mutation_id, procedure, input jsonb, depends_on, status: queued|sending|failed|conflict, attempts, last_error, created_at)` with strict FIFO per entity and parallelism across independent entities.
* Retry policy: exponential backoff 1 s → 60 s with jitter, 20 attempts, then `failed`; network errors retry forever while offline (no attempt counted); 4xx other than 409/429 fail immediately.
* Dependency tracking: a create followed by an update of the same temp ID are chained; temp IDs (`tmp_` UUID) are remapped when the server returns the real ID.
* `SyncStatusIndicator` in `packages/ui` for the status bar: states `synced`, `syncing (n)`, `offline (n queued)`, `attention (n failed)`; click opens `SyncQueueSheet` listing items with retry, discard, and "copy details".
* `useSyncStatus()` hook and `navig
SPEC(first 1200): * API: `enqueue({ procedure, input, entity: { table, id }, optimistic })`, `flush()`, `retry(id)`, `discard(id)`, `subscribe(cb)`; the existing `mutate()` becomes a thin wrapper.
* Server idempotency: oRPC middleware in `data-layer/api-layer` stores `mutation_id` in `idempotency_keys(tenant_id, mutation_id, response, expires_at 24h)` and replays the stored response on duplicates.
* Ordering: single in-flight request per entity; independent entities flush with concurrency 4; batches up to 25 mutations use `POST /api/rpc/batch`.
* 409 responses carry `{ code: 'conflict', server: row }` and move the item to `conflict`, emitting the event `realtime/conflict-ux` consumes; 429 honours `Retry-After`.
* Copy in `packages/collab/src/copy/sync.ts`; indicator uses icon plus text, never colour only; `role="status"`, announces transitions at most once per 30 s.
* Storage guard: refuse new writes when the queue exceeds 5,000 items or 50 MB, with a blocking dialog explaining why.
* Telemetry: `sync.flush` spans via `data-layer/observability` with queue depth and attempt count.
DOD:
* Playwright tests: go offline, make 20 edits across 3 entities including create-then-update, come back online, all land in order with remapped IDs; captive-portal simulation (200 with HTML body) treated as offline.
* Vitest tests for backoff, dependency chaining, idempotent replay and storage guard.
* Screenshots of all four indicator states and the queue sheet at 320, 768 and 1280 px.
* Tauri desktop restart test: queued writes persist and flush on relaunch (video).
* Docs `docs/platform/realtime/offline.md` with a state diagram.
* Changelog entry and Linear comment with the demo link.
EDGE:
* Session expired while offline: on reconnect, refresh the session first; if that fails, keep the queue and show "Sign in to sync".
* Server-side validation now rejects an old queued write (schema changed): mark `failed` with the message; never drop silently.
* User signs out with queued writes: warn and require confirmation; discard on confirm.
* Two devices edit offline, both come online: ordering by server arrival; conflicts surface via 409 to the later one.
* Clock jump (device time changed) must not break backoff timers; use monotonic `performance.now()`.
* Optimistic row for a failed create remains visible with an error badge until discarded.
DEPS: * `data-layer/local-first-sync` (PGlite, existing outbox), `data-layer/api-layer` (idempotency middleware, batch), `realtime/record-sync` (reconciliation), `realtime/conflict-ux` (conflict handling), `app-shell/pwa` and `app-shell/tauri-mobile` (background flush).


## PAP-149 [P2 Build M prio3 Backlog] Add follow mode and shared cursor sessions for support and pair review
key=realtime/followmode milestone=Scale and offline tested agent=Builder: Nova (CRDT Engineer sub-agent). Reviewer: Sentinel 
blockedBy=['PAP-141'] blocks=[]
GOAL: Let a support agent or reviewer guide someone through the app live: click a person in presence and "follow" them so your view mirrors their navigation, scroll position and selection, or start a shared cursor session where both parties see each other's pointer and a highlighted element. This replaces screen-sharing for support and pair review, and it works between humans and agents.
SCOPE: In:

* `packages/collab/src/follow/`: `useFollow(targetPrincipalId)` (follower) and leader broadcasting of `{ route, params, scroll: { surfaceId, x, y }, selection, viewport zoom, highlightedElement }` through the presence awareness room from `realtime/presence`.
* Consent model: staff can follow customers only after the customer accepts a request ("Ada from support wants to view along with you") or when an active support session exists; staff and agents can follow each other freely; customers can follow staff during a shared session.
* Shared cursor session: bidirectional cursors with name labels, "point" ping (click with modifier) that ripples an element for both, and a persistent highlight ring on any `[data-spec-component]` element.
* UI: `FollowBar` pinned at top ("Following Ada · Stop"), leader banner ("Bo is following you · End"), request dialog, and entry points in the presence a
SPEC(first 1200): * Leader emits at most 10 updates/s; scroll positions are relative to `[data-presence-surface]` ids so different window sizes still align; the follower scrolls the matching surface with `scrollTo` and shows an "out of view" arrow when the leader's highlighted element is off-screen.
* Navigation mirroring uses TanStack Router `navigate` with the leader's route and params; if the follower lacks permission for that route, `FollowBar` shows "Ada is on a page you cannot view" and waits.
* Follower interactions pause following for 10 s (local exploration), then a "Resume following" button appears; explicit Stop ends the session.
* Requests are awareness messages with a 60 s timeout; acceptance is recorded with `consentedAt`; customers can end at any time from the banner.
* Impersonation interplay: following is view-only; acting on behalf of the customer requires `identity/impersonation` and is a separate, audited action.
* Agents as leaders: an agent running a walkthrough (future onboarding character) can lead; agents cannot follow customers.
* Accessibility: all state changes announced via a live region; every control keyboard reachable; commands `follow.start`, `follow.stop`, `follow.p
DOD:
* Playwright test with two contexts: staff requests, customer accepts, navigation and scroll mirror within 300 ms, follower explores and resumes, session ends; screenshots at 375 (customer, mobile) and 1440 px (staff).
* Vitest tests for consent rules per audience and rate limiting.
* Permission test: staff cannot follow a customer without consent or an active support session.
* Audit entries verified for start and end.
* Storybook stories for `FollowBar`, leader banner and request dialog in three themes.
* Docs `docs/platform/realtime/follow-mode.md` including a support runbook.
* Changelog entry and Linear comment with a 30-second demo video.
EDGE:
* Leader goes offline: follower sees "Ada disconnected" and the session ends after 30 s.
* Leader opens a modal: follower mirrors modal open state via the highlighted element id, not by replaying clicks.
* Leader in a detached Tauri window (`realtime/multi-window-sync`): the leader's aggregated presence reports the focused window's route.
* Follower on a phone following a 1920 px desktop leader: horizontal positions clamp; highlight ring still targets the same element.
* Two staff follow one customer: both receive updates; the customer banner lists both names.
* Leader navigates to an external URL: following pauses with a notice.
DEPS: * `realtime/presence` (transport and avatars), `identity/rbac-abac` and `identity/impersonation` (consent and boundaries), `data-layer/audit-log`, `input/command-registry`, `app-shell/router-layouts` (navigate API). Optional entry point in `growth/support-inbox`.
