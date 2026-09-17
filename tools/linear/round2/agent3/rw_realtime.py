R = {}

R["PAP-139"] = {
"Goal": "Confirm with measurements that Yjs is the right document CRDT before the Hocuspocus server (PAP-140), editor (PAP-142) and canvas (PAP-132) are built on it. Output: an ADR plus a reproducible benchmark harness so the choice can be reopened with the same numbers if Loro or Automerge overtake Yjs.",
"Scope": """In:

* Harness `packages/collab/bench/` comparing `yjs` 13.6.x, `@automerge/automerge` 2.x and `loro-crdt` 1.x behind one `CrdtAdapter` interface.
* Workloads: (a) 200k-character rich-text doc with 50k random edits; (b) canvas map of 10k shapes with 20k property updates; (c) 50 simulated peers for 60 s at 200 ms latency.
* Metrics: encoded size, load time, memory after load, per-op apply p50/p99, merge time of two divergent 10k-op histories, gzip WASM size, TypeScript quality, ecosystem (Tiptap and React Flow bindings, server persistence, awareness, licence).
* ADR `docs/adr/00NN-PAP-139-document-crdt.md` in the PAP-130 format with reopen criteria; registry entries for the three libraries (PAP-216).

Out: record-level sync (PAP-31), peer-to-peer transports, any server.""",
"Spec": """* `vitest bench` file plus `pnpm bench:crdt --out results.json`; results table `bench/results.md` committed from a fresh run on `ubuntu-latest`, Node 22, median of 5 runs.
* Scoring per PAP-209 weights recorded in the ADR.
* The ADR recommends the persistence encoding (`Y.encodeStateAsUpdateV2`) and snapshot cadence for PAP-140.""",
"Interface contract": """Exposes: `CrdtAdapter { create(); applyText(pos, text); deleteText(pos, len); setShape(id, props); encode(); load(bytes); merge(other) }` for future reruns; `results.json` `{ lib, workload, metric, value, unit, runs }[]`; ADR `decision` block naming the library, encoding (`updateV2`), snapshot cadence (every 500 updates or 60 s) and pinned versions, which PAP-140 copies into its config and PAP-142 into its peer matrix. Consumes: rubric weights from PAP-209 (draft acceptable), ADR template from PAP-130 or `docs/decisions/TEMPLATE.md` from PAP-44.""",
"Definition of done": """* `pnpm bench:crdt` runs on CI under 10 minutes and writes `results.json` and `results.md`; every workload has numbers for every library.
* ADR merged as `accepted`, linked from the ADR index and the realtime project description; registry updated.
* Linear comment with results table, ADR link and a one-paragraph recommendation; developer changelog entry.""",
"Test plan": """* Unit: deterministic 1,000-op edit script yields identical final text across all three adapters; encode/load round-trip per adapter; merge of two divergent histories converges.
* Bench: each workload asserts it completes and reports p50/p99; WASM init measured separately; memory read after `global.gc()` with `--expose-gc`.
* CI: bench job runs on a fixed runner class and fails if any cell is missing; results file diffed against the committed one (informational).
* Review: Sentinel reruns `pnpm bench:crdt` locally and compares medians within 20 percent.""",
"Demo": "Run `pnpm bench:crdt --workload a --runs 1` and watch the table print for three libraries; open `bench/results.md` and the ADR's decision block. Under two minutes.",
"Edge cases": """* Await WASM init before timing; report it separately.
* Automerge UTF-16 vs grapheme offsets: adapter normalises or documents.
* Yjs `gc: true` changes encoded size: measure both.
* Loro version churn: pin exact versions in `bench/package.json`.
* Runner noise: median of 5.""",
"Dependencies": "None hard (Ready). Soft: PAP-209, PAP-130. Blocks PAP-140 (encoding and cadence); informs PAP-142, PAP-132.",
"Agent": "Builder: Scout (Library Evaluator) with Nova (CRDT Engineer) on workloads. Reviewer: Nova signs the ADR; Sentinel (Code Reviewer) reviews the harness.",
"Size": "S: two-day time box with a fixed output shape.",
}

R["PAP-140"] = {
"Goal": "Stand up the multiplayer backbone: a self-hosted Hocuspocus server that authenticates every WebSocket with a Better Auth session or agent key, persists one Yjs document per room to Postgres under RLS and enforces per-document read and write permissions. Presence, collaborative text, canvas and multi-window sync all connect here.",
"Scope": """In:

* `apps/collab-server/` (Node 22) on `@hocuspocus/server` 3.x with `extension-database` (Drizzle Postgres store), `extension-logger`, `extension-throttle`, `extension-redis` behind a flag.
* Rooms `doc:<tenantId>:<entityType>:<entityId>`, `page:<tenantId>:<routeId>` (ephemeral) and `canvas:<appId>`; one Yjs doc per room; awareness on.
* `onAuthenticate`: verify session token or `pos_agent_` key, resolve principal, call PAP-59 `can()` for `document.read|write`; read-only connections get `connection.readOnly`.
* Persistence: `yjs_documents(room pk, tenant_id, state bytea, vector bytea, updated_at, size_bytes)` plus `yjs_updates` append log compacted every 500 updates or 60 s; RLS by tenant (PAP-34).
* Compose and Coolify definition `ops/compose/collab-server.yml` at `wss://collab.<domain>` behind Caddy; `/healthz`; Prometheus `/metrics`.
* Client `packages/collab/src/provider.ts` `createDocProvider({ room, token })` wrapping `@hocuspocus/provider` with backoff and `y-indexeddb`.

Out: presence UI (PAP-141), editors (PAP-142), load tuning (PAP-147), Electric record sync (PAP-143).""",
"Spec": """* Config `port 1234`, `timeout 30000`, `debounce 2000`, `maxDebounce 10000`; `onLoadDocument` reads `state`, `onStoreDocument` writes `encodeStateAsUpdateV2` (PAP-139), `onChange` appends to `yjs_updates`.
* `context = { principalId, principalType, tenantId, scopes }` for all hooks; unknown entity types rejected `4403`.
* Limits: 2 MB message, 20 MB document (`4413`, event `collab.document.too_large`), 100 connections per principal; permissions re-checked every 5 minutes and on `permission.changed`.
* Rooms unload 30 s after the last connection; `DELETE /admin/rooms/:room` forces snapshot and unload.
* Env via PAP-17: `COLLAB_DATABASE_URL`, `COLLAB_REDIS_URL?`, `COLLAB_PUBLIC_URL`, `AUTH_BASE_URL`.""",
"Interface contract": """Exposes: `createDocProvider({ room, token, ephemeral? }) -> { provider, doc, awareness, status$ }`, `roomName(kind, tenantId, ...parts)` and `parseRoom()` in `packages/collab/rooms.ts`, close codes `4401` (expired), `4403` (denied), `4413` (too large); tables above; metrics `collab_connections`, `collab_rooms`, `collab_messages_total`, `collab_store_latency_seconds`; admin route above; event `collab.document.too_large`. Consumes: `verifySessionToken()` and `verifyApiKey()` from `@paperos/auth` (PAP-223), `can(principal, action, resource)` from `@paperos/permissions` (PAP-227), migrations and RLS helpers (PAP-32, PAP-34, PAP-228), env schema (PAP-17), VPS, Caddy and Coolify (PAP-25), encoding decision (PAP-139).""",
"Definition of done": """* `docker compose up collab-server` connects from `apps/web`; two browsers editing a `Y.Text` converge.
* RLS test proves tenant A cannot load tenant B's room even with a forged room name.
* Deployed at `wss://collab.<domain>` with TLS; `/healthz` monitored by PAP-40; Grafana panel screenshot on the PR.
* `docs/platform/realtime/server.md` with sequence diagram and runbook; changelog entry; Linear comment with wss URL and demo steps.""",
"Test plan": """* Vitest integration (Postgres in CI): expired token → `4401`; read-only principal's update dropped and logged; persistence round-trip across a server restart; compaction reduces `yjs_updates` below 500 rows; corrupt `state` falls back to replaying updates; oversize message → `4413`.
* RLS: PAP-34 harness with two tenants and a forged room name.
* Playwright: two contexts converge on `Y.Text` within 1 s; container restart via `docker compose restart` and the provider reconnects within 5 s without losing an offline edit.
* Ops: `/healthz` and `/metrics` scraped in the compose test; Caddy WebSocket idle timeout verified at 10 minutes idle.""",
"Demo": "Open the `/_app/dev/collab-demo` page in two browsers, type in one, see the other; stop the container, keep typing, start it and watch the text merge; open Grafana's collab panel. Under two minutes.",
"Edge cases": """* Token expires mid-session: `4401`, provider refreshes and reconnects without losing edits.
* Postgres down on store: retry with backoff, keep in memory, alert after 3 failures.
* `REPLICAS > 1` without Redis: refuse to start.
* Room name over 255 bytes or with odd characters: rejected.""",
"Dependencies": "PAP-25, PAP-57, PAP-59, PAP-139 (hard, encoded). Soft: PAP-32, PAP-34, PAP-17, PAP-40. Blocks PAP-131, PAP-132, PAP-141, PAP-142, PAP-145, PAP-147 and the planned runtime docs store.",
"Agent": "Builder: Forge (Ops Runner) for deployment and persistence with Nova (CRDT Engineer) for the provider. Reviewer: Sentinel (Security Auditor) on auth and RLS, Sentinel (Code Reviewer) on the rest.",
"Size": "M: well-trodden library integration; auth, RLS and deployment must all be right.",
}

R["PAP-141"] = {
"Goal": "Make every PaperOS page show who is here: live cursors, selection highlights, avatar stacks and a who-is-viewing indicator on any page, not only inside editors. Presence rides on Hocuspocus awareness and is the foundation for agent presence (PAP-146) and follow mode (PAP-149).",
"Scope": """In:

* `packages/collab/src/presence/`: `PresenceProvider` joining `page:<tenantId>:<routeId>` (ephemeral room from PAP-140) and optional entity rooms; hooks `usePresence()`, `useMyPresence()`, `useViewers(entityId)`.
* Awareness payload (Zod): `{ principalId, principalType: 'human'|'agent', name, avatarUrl?, color, cursor?: { x, y, surfaceId }, selection?: { entityId, fieldId? } | { from, to }, viewport?, focusedRoute, lastActive, idle }`.
* Components in `packages/ui` on PAP-71 `AvatarStack`: `PresenceAvatars` (5 plus overflow), `LiveCursor` (fades after 4 s, hidden on touch), `SelectionHighlight`, `ViewersBadge`.
* Colours: 12 accessible tokens from PAP-66 chosen by hashing `principalId`; idle after 60 s or hidden tab.

Out: agent visuals (PAP-146), follow mode, chat, history.""",
"Spec": """* Cursor throttled to 50 ms; selection and route immediate; coordinates relative to the nearest `[data-presence-surface]`.
* Privacy: `presence.view` policy (PAP-59): customers see staff, assigned agents and members of their own organisation; staff see the tenant.
* Page spec flag `realtime.presence: true|false` (PAP-114), default true for staff surfaces, false for customer surfaces.
* Same principal in several windows appears once with an `x2` badge (PAP-145 aggregates).
* Accessibility: stack `aria-label`, cursors `aria-hidden`, live region announces joins at most once per 10 s.""",
"Interface contract": """Exposes: `PresenceState` type and Zod schema in `packages/collab/presence/schema.ts` (extended by PAP-146 with `agent?`), `PresenceProvider`, hooks above, components above, `presenceColor(principalId)`, DOM attribute `data-presence-surface=“<id>”` that PAP-149 and PAP-142 reuse for coordinates, awareness message kinds `presence.request` reserved for PAP-149. Consumes: `createDocProvider(..., { ephemeral: true })` and awareness from PAP-140, `AvatarStack` and `Badge` (PAP-71), palette tokens (PAP-66), `can('presence.view')` (PAP-59), display names from PAP-55, page flag from PAP-114.""",
"Definition of done": """* Two browsers on one page show each other's avatar within 1 s and cursor movement under 100 ms on localhost.
* Storybook stories for four components in light, dark and high contrast; axe clean.
* `docs/platform/realtime/presence.md` with payload schema and page flag; changelog; Linear comment with Storybook and staging links.""",
"Test plan": """* Vitest: payload validation, colour hashing stability across 1,000 ids, idle transitions with fake timers, dedupe of one principal across windows, 50-viewer overflow text.
* Integration: `can('presence.view')` matrix through `callAs` for customer, staff and agent contexts; customer never receives another customer's state (server filters awareness by policy).
* Playwright, two contexts: avatars and selection highlights render at 375, 1024 and 1920; cursor latency measured with `performance.now()` stamps under 100 ms; disconnect dims after 5 s and removes after 30 s.
* Visual: Storybook stories captured by Gate 3 in three themes; reduced-motion story has no animation.""",
"Demo": "Open the records page in two browsers with different users, move the mouse in one and watch the labelled cursor in the other; select a row and see the coloured outline; hover the avatar stack to read the names. Under two minutes.",
"Edge cases": """* 50 viewers: 5 avatars plus `+45`, tooltip lists 20.
* Scrolled container: surface-relative coordinates.
* Long names truncate at 24 characters.
* Reduced motion: no animation or pulse.""",
"Dependencies": "PAP-140 (hard, encoded). Soft: PAP-71, PAP-66, PAP-59, PAP-55, PAP-114. Blocks PAP-146, PAP-149; consumed by PAP-165, PAP-132, PAP-142.",
"Agent": "Builder: Nova (CRDT Engineer). Reviewer: Iris (Component Crafter) for components; Sentinel (Visual Inspector) across the matrix.",
"Size": "M: several components plus permission-aware presence semantics.",
}

R["PAP-142"] = {
"Goal": "Ship one collaborative rich-text editor every surface reuses: docs, comments, issue descriptions, notes fields. Tiptap binds to a Yjs document on Hocuspocus so people and agents edit together with live carets, and it degrades to a local editor when a field is not shared.",
"Scope": """In:

* `packages/collab/src/editor/` exporting `<RichTextEditor room? value? onChange? readOnly placeholder mentions attachments variant />` on `@tiptap/react` 3.x with starter kit, collaboration and caret extensions, mention, link, placeholder, task lists, tables, `lowlight` code blocks and image nodes uploading via PAP-37.
* Modes: `room` → Yjs via `createDocProvider` (PAP-140); no room → controlled JSON value, same schema.
* Toolbar and bubble menu from PAP-67 primitives; every action registered in PAP-151 (`editor.bold`, `editor.link`, ...).
* Mentions of users, agents and entities via `@` and `#` through a `MentionSource` interface; agents render `ActorBadge` (PAP-60).
* Markdown paste and export via `prosemirror-markdown`; Storybook: local, collaborative (mock provider), read-only, `comment` variant.

Out: anchoring and threads (PAP-131), docs pages (PAP-128), version history UI, AI assistance.""",
"Spec": """* `Y.XmlFragment` named `default`; other fragments may share the room.
* Caret colours and names from PAP-141; dashed caret for `principalType === 'agent'`.
* `readOnly` follows `connection.readOnly`; toolbar hides and a badge reads "View only".
* `richTextSchema` (Zod) in `packages/core` for `jsonb` columns; `renderRichText(json)` server renderer with `sanitize-html`.
* Undo via `y-undo-manager` scoped to `trackedOrigins`, bound to `edit.undo|redo`.
* `role="textbox"`, toolbar roving tabindex from PAP-152; collaborative chunk under 250 KB gzipped, lazy-loaded; 100k-character doc types at 60 fps.""",
"Interface contract": """Exposes: `RichTextEditor` props above (`variant: 'full'|'comment'|'inline'`), `richTextSchema` and `RichTextJson` type, `renderRichText(json) -> string`, `richTextToPlain(json)` (used by PAP-131 `body_text` and PAP-138 indexing), `MentionSource { search(q, kinds) -> Mention[] }` and `Mention { kind: user|agent|entity, id, label, avatarUrl? }`, `markdownToRichText()` and `richTextToMarkdown()`, registry command ids `editor.*`. Consumes: provider and room grammar (PAP-140), presence colours (PAP-141), primitives `Button`, `Menu`, `Tooltip`, `Dialog` (PAP-236 to PAP-238), `defineCommand` (PAP-151), roving tabindex (PAP-152), signed uploads (PAP-37), `ActorBadge` (PAP-60), library choice (PAP-127).""",
"Definition of done": """* Two browsers converge with visible carets; offline edits merge on reconnect.
* Toolbar actions appear in the palette with shortcuts.
* Storybook stories at 320, 768 and 1280 with axe passing; `docs/platform/realtime/editor.md`; changelog; Linear comment with Storybook link and a 20-second two-cursor video (PAP-83).""",
"Test plan": """* Vitest: markdown round-trip fixtures, mention insertion and serialisation, `richTextSchema` accepts stories and rejects unknown nodes, `renderRichText` strips `<script>` and `javascript:` links, `richTextToPlain` snapshot.
* Integration: mock provider emits remote updates and the editor renders them; `readOnly` toggles with `connection.readOnly`.
* Playwright, two contexts: type in both, assert convergence within 1 s and caret labels; set context A offline, type, reconnect, assert merge; IME composition via `keyboard.insertText` keeps text intact; paste a 5 MB HTML fixture truncates with a toast.
* Performance: 100k-character fixture, measure keydown-to-paint under 16 ms p95 via CDP.
* Visual: Gate 3 captures of the four stories in three themes.""",
"Demo": "Open a doc in two browsers, type in both and watch carets; press `mod+k`, run “Bold”; toggle one user to view-only and see the badge; paste a markdown list and see it convert. Under two minutes.",
"Edge cases": """* Image upload fails: placeholder node with retry.
* Mentioned user loses access: plain text with a tooltip.
* Room switch while mounted: provider recreated, no stale flash.
* Read-only user types: no-op, one toast per session.""",
"Dependencies": "PAP-127, PAP-140 (hard, encoded). Soft: PAP-141, PAP-67, PAP-151, PAP-152, PAP-37, PAP-60. Blocks PAP-131 and the planned runtime docs store; consumed by PAP-164, PAP-100, PAP-159.",
"Agent": "Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Code Reviewer, Security Auditor for the renderer); Iris reviews toolbar styling.",
"Size": "M: Tiptap does the heavy lifting; integration, accessibility and two modes remain.",
}

R["PAP-143"] = {
"Goal": "Umbrella: make every table, list and detail page update live when any human or agent changes a record, without per-feature socket code. Electric shapes (PAP-270, PAP-271) stream rows into PGlite; this issue reconciles them with optimistic writes and tells the UI when data changed under it. Planned as three work packages; the umbrella owns the lag measurement and docs.",
"Scope": """Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Live record hooks and shape registry additions** — `useRecord`, `useRecordChanges`, reference-counted subscriptions on top of PAP-271's `useShape`/`useLiveQuery`, shape entries for `records`, `fields`, `views` (PAP-161) and PM entities (PAP-100) with tenant and permission predicates, per-frame batching, LRU cap of 50 shapes.
2. **Reconciler for optimistic writes and conflict events** — `mutation_id` and `updated_by` stamping in PAP-35 middleware, `_pending` rows, echo matching, `expect` comparison, `conflict` event emission consumed by PAP-144 and PAP-148.
3. **Permission-driven resubscribe and lag measurement** — `409 shape-invalid` handling, drop and resubscribe, dev inspector `window.__paperosSync`, Playwright lag test with Electric in CI.

Parent owns `docs/platform/realtime/record-sync.md` with data-flow diagram, staging lag measurement and the grid demo page.

Out: transport (PAP-270), Yjs documents, retry policy (PAP-148), conflict visuals (PAP-144).""",
"Spec": """* Libraries `@electric-sql/client` 1.x, `@electric-sql/pglite` 0.3.x with `live`, `@electric-sql/react`; shapes through `/api/sync/shape` with the session (PAP-270).
* Lag budget 500 ms p95 on staging; ordering by server `lsn`, never client clocks.
* Shapes unsubscribe 30 s after the last consumer unmounts.""",
"Interface contract": """Exposes: `useRecord(table, id)`, `useRecordChanges(id) -> { changedFields, actor, at } | null`, `subscribeShape(def) -> unsubscribe`, `ShapeDef { table, where, columns? }` registry `registerShape()`, `mutate(proc, input, { optimistic, expect })` extension, event `sync.conflict { recordId, table, conflictingFields, mine, theirs, actor, at }` and `sync.remoteChange { recordId, changedFields, actor }` on a local `EventTarget` in `packages/sync/events.ts`, inspector shape `{ shapes[], lagMs, outboxLength }`. Consumes: `useShape`, `useLiveQuery`, PGlite client (PAP-271), shape proxy and predicates (PAP-270, PAP-228), oRPC middleware hooks for stamping `mutation_id uuid` and `updated_by` (PAP-267), outbox from PAP-272, view model tables (PAP-161), PM tables (PAP-100).""",
"Definition of done": """* All three work packages merged; grid demo: a cell edited in browser A updates B within 500 ms; screenshot pair at 768 and 1440.
* Integration test with a real Electric container in CI.
* Docs with diagram; changelog; Linear comment with staging demo link and lag measurement.""",
"Test plan": """* Integration (parent): `ops/compose/test.yml` with Postgres and Electric; Playwright writes via API and polls the DOM in a second context; asserts p95 under 500 ms over 50 writes; revokes a role via `/__test` (PAP-240) and asserts rows disappear within one resubscribe.
* Unit tests per work package (echo match drops optimistic row, mismatch emits conflict with correct fields, out-of-order arrival, duplicate echo idempotent, LRU eviction warning, 409 handling).
* Visual: grid demo captured at 768 and 1440 in both themes with the 5 s change flash.""",
"Demo": "Open the grid demo in two browsers, edit a cell in one and watch it flash in the other with the actor avatar; go offline in one, edit, come back and see it reconcile; open `window.__paperosSync` in devtools. Under two minutes.",
"Edge cases": """* Offline an hour, 300 outbox writes vs 2,000 remote rows: remote first, then replay, conflicts per row.
* Row deleted while editing: keep editor with a "deleted by X" banner and restore via PAP-38.
* 500k-row shape: refused without a bounding predicate.
* Schema migration: PGlite hash mismatch resets with a toast.""",
"Dependencies": "PAP-36 (hard, encoded; children PAP-270 to PAP-272). Soft: PAP-35, PAP-59, PAP-163, PAP-240. Blocks PAP-144, PAP-148, PAP-147 and the planned push transport; consumed by PAP-165, PAP-102, PAP-131, PAP-136.",
"Agent": "Builder: Nova (CRDT Engineer) with Forge (Schema Wright) on stamping columns. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for ordering).",
"Size": "L, planned as three M/S work packages (child issues pending the issue limit).",
}

R["PAP-144"] = {
"Goal": "Specify how PaperOS tells a user that someone else changed what they are looking at or editing, and what they can do about it. Output: a UX spec, five component definitions with spec IDs and static Storybook mocks, so record sync, offline queue and the tables engine implement one behaviour.",
"Scope": """In:

* `docs/platform/realtime/conflict-ux.md`: field-level stale indicators, "updated by X just now" attribution, merge banner for form conflicts, last-writer-wins rules per field type, undo of a remote overwrite, pending and failed-write states.
* Component definitions (props, states, copy) for `StaleFieldIndicator`, `ConflictBanner`, `RemoteChangeFlash`, `PendingWriteBadge`, `FailedWriteDialog`, mapped to spec IDs `ui.conflictBanner` etc. in PAP-74's registry.
* Decision table per PAP-164 field type: auto-merge (rich text via Yjs, multi-select union), last-writer-wins with attribution (number, date, single select), manual resolution (currency over a threshold, status transitions).
* Copy deck `packages/collab/src/copy/conflicts.ts`; static stories at 375 and 1280.

Out: implementation (follow-ups filed here), Yjs merge, server merge logic.""",
"Spec": """* Untouched field: remote change applies silently with a 5 s flash and tooltip "Changed by Ada 3 s ago". Dirty field: inline `ConflictBanner` with "Keep mine", "Use theirs", "Compare"; never block typing.
* Undo of a remote overwrite via command `edit.undoRemote` (PAP-151) writes the previous value as a new write.
* Offline: `PendingWriteBadge`, resolves to a check for 2 s; failures open `FailedWriteDialog`.
* Agent actors use `ActorBadge` linking to the prompt log session (PAP-135).
* Banner `role="alert"` once per record per 10 s; icon plus text, never colour alone.""",
"Interface contract": """Exposes: TypeScript interfaces `StaleFieldIndicatorProps { field, actor, at }`, `ConflictBannerProps { conflict: SyncConflict, onKeepMine, onUseTheirs, onCompare }`, `RemoteChangeFlashProps`, `PendingWriteBadgeProps { state: queued|sending|failed }`, `FailedWriteDialogProps` in `packages/collab/src/conflicts/types.ts`; `resolutionPolicy(fieldType) -> 'merge'|'lww'|'manual'` table exported as JSON; spec IDs registered in `registry.json` (PAP-74); copy keys. Consumes: `sync.conflict` and `sync.remoteChange` event shapes from PAP-143, field type list from PAP-164, `ActorBadge` (PAP-60), `Timeline` and `Badge` (PAP-71), ADR format (PAP-130), permalink grammar from PAP-135.""",
"Definition of done": """* Spec merged with the decision table covering every PAP-164 field type (unknowns marked TBD with owner).
* Five definitions with props, copy and spec IDs registered; static stories at 375 and 1280, axe clean, screenshots attached.
* Follow-up issues filed in tables, realtime and spec-builder and linked; ADR for last-writer-wins vs manual recorded (PAP-130).
* Docs changelog entry; Linear comment summarising the rules in ten lines; rules ride in the next release digest (PAP-89), no separate Needs Justin item.""",
"Test plan": """* Unit: `resolutionPolicy()` returns a value for every field type in PAP-164's enum (test fails when a new type is added without a row); copy deck has no untranslated keys.
* Component: static stories render each state (default, hover, focus, dense, RTL); axe on each; `role="alert"` present exactly once.
* Visual: Gate 3 captures of the five stories at 375 and 1280 in both themes serve as the approved reference for PAP-148 and PAP-165 implementations.
* Review: Nova confirms the event shapes match PAP-143's `sync.conflict` type by importing it in the story fixtures.""",
"Demo": "Open Storybook “Conflicts”, step through the five states, open the RTL and dense variants, then open the spec's decision table and find “currency” to read why it requires manual resolution. Under two minutes.",
"Edge cases": """* Three edits in a second: banner shows the latest actor "and 1 other".
* Conflict on a hidden column: row-level indicator.
* Open dropdown: defer applying until closed.
* Agent wrote later than the human: "Keep mine" wins and posts a comment mentioning the agent.
* Invalid status transition after remote change: validation error, not a conflict banner.""",
"Dependencies": "PAP-143 (hard, encoded). Soft: PAP-164, PAP-74, PAP-71, PAP-130. Blocks PAP-148; consumed by PAP-165, PAP-120.",
"Agent": "Builder: Quill (Page Spec Writer) with Iris (Component Crafter) for mock stories. Reviewer: Nova and Sentinel (Edge Case Hunter).",
"Size": "S: a spec and mock stories, no production code.",
}

R["PAP-145"] = {
"Goal": "Keep every window and tab of one user coherent: a record edited in a detached inspector on monitor two reflects instantly in the main window, selection and navigation can be shared, and the app never fights itself with duplicate connections. This makes the PAP-21 window manager feel like one application.",
"Scope": """In:

* `packages/collab/src/windows/`: `WindowBus` over `BroadcastChannel` (same-origin web and Tauri webviews) with a Tauri `emit`/`listen` fallback; Zod message schema.
* Leader election reusing PAP-272's `navigator.locks` election: one window holds Hocuspocus and Electric connections, followers proxy through it; re-election within 2 s.
* Channels: `selection`, `navigation` (with `follow` flag), `presence` (single awareness entry per user for PAP-141), `auth` (sign-out), `theme`, `keymap` (PAP-153), `dnd.transfer` (PAP-155).
* Yjs relay: leader forwards `encodeStateAsUpdate` diffs over the bus; every window keeps `y-indexeddb`.
* UI: `WindowChip` in the status bar listing detached windows with focus and dock; "Follow main window selection" toggle in detached windows; dev overlay.

Out: cross-device sync, cross-user follow (PAP-149), OS window placement (PAP-262).""",
"Spec": """* Channel `paperos:<tenantId>:<userId>`; messages `{ type, from: windowId, ts, payload }`; `windowId` in `sessionStorage`.
* Followers send writes to the leader, which forwards to the API; if the bus is unavailable each window uses its own connections (logged degraded).
* Rich text in two windows shares one Yjs doc; form fields use last-blur-wins and show `RemoteChangeFlash` (PAP-144).
* Mobile: single window, bus is a no-op.
* Relaying 1,000 Yjs updates/s across three windows under 10 percent leader CPU.""",
"Interface contract": """Exposes: `WindowBus` with `publish(type, payload)`, `subscribe(type, cb)`, `useWindowBus()`, `useIsLeader()`, `useWindows() -> { id, title, route, isLeader }[]`, message types above with Zod schemas in `packages/collab/windows/messages.ts` (other packages add types via `declare module` augmentation), `WindowChip`. Consumes: `WindowManager` `detach`, `dock`, `list_displays` and `panel-<id>` naming (PAP-262), leader election helper (PAP-272), `createDocProvider` (PAP-140), shape subscriptions (PAP-143), `PresenceProvider` aggregation hook (PAP-141), sign-out event (PAP-223), `RemoteChangeFlash` (PAP-144).""",
"Definition of done": """* Three same-context pages hold one WebSocket to the collab server; edits propagate under 50 ms; closing the leader re-elects without loss.
* Tauri Linux run with a detached inspector on a second display recorded (PAP-83).
* Screenshots at 1280 and 1920 with `WindowChip`; `docs/platform/realtime/multi-window.md` with election and relay diagram; changelog; Linear comment with video.""",
"Test plan": """* Vitest: message schema (valid, unknown type), leader election with simulated lock loss, heartbeat conflict picks lowest `windowId`, fallback when `BroadcastChannel` is undefined, tenant-scoped channel isolation.
* Playwright: three pages in one context; count WebSocket connections via CDP `Network.webSocketCreated` equals one; edit propagation under 50 ms measured with `performance.now()`; close the leader page and assert re-election within 2 s and a queued follower write lands; sign-out in one page redirects all three within 500 ms.
* Performance: CDP profiler while relaying 1,000 updates/s for 10 s, leader CPU under 10 percent.
* Visual: main window plus detached panel captured at 1280 and 1920, both themes.""",
"Demo": "Detach the inspector to a second window, edit a record there and watch the main grid update; enable “Follow main window selection” and click rows in the main window; close the main window and keep editing in the panel. Under two minutes.",
"Edge cases": """* Two leaders after sleep: lowest `windowId` wins within one heartbeat.
* Private tab without `locks`: standalone with a warning.
* Follower writes during leader reconnect: queue 1,000 then `PendingWriteBadge`.
* Second window on another tenant: bus does not talk; switcher warns.""",
"Dependencies": "PAP-21, PAP-140 (hard, encoded). Soft: PAP-262, PAP-272, PAP-143, PAP-141, PAP-223, PAP-144. Blocks PAP-23; consumed by PAP-153, PAP-155, PAP-149.",
"Agent": "Builder: Nova (CRDT Engineer) with Forge (Tauri Smith) for the Tauri fallback. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).",
"Size": "M: election and relay are subtle but bounded.",
}

R["PAP-146"] = {
"Goal": "Make Claude agents visible collaborators wherever a human would be: an agent editing a spec, typing a comment or reviewing a PR appears in presence with a distinct identity, its activity and a link to what it is doing, so machine work is seen while it happens.",
"Scope": """In:

* Extend the PAP-141 payload with `agent?: { character, subAgent?, issueKey?, activity: reading|editing|typing|reviewing|waiting, sessionId }`.
* `packages/agents/src/presence-client.ts`: Node client used by PAP-107 hooks to join rooms with the agent's `pos_agent_` key, set activity from tool calls and leave on session end.
* `packages/ui`: `AgentAvatar` (square, character glyph and colour from PAP-103, "AI" mark), dashed cursor and caret, `ActivityChip` ("Forge is editing page.spec.yaml · PAP-42"), `AgentActivityPanel` in the staff console listing active agents with issue and prompt-log links.
* Page spec flag `realtime.agentPresence: staff|all|none` (default `staff`).

Out: agent chat, controlling agents (PAP-113), customer-facing disclosure copy.""",
"Spec": """* `toolCallToActivity(tool, args)` is pure; unknown tools → `waiting`; resets after 30 s.
* Rooms: `page:<tenant>:<route>` when the tool touches a file mapped by PAP-115's route index, else `issue:<tenant>:<issueKey>` so PAP-102 cards can show agents.
* Customers see only an "Assistant" avatar when `all`; never cursors.
* `aria-label="Forge (agent), editing"`; live region announces once.""",
"Interface contract": """Exposes: `AgentPresence` Zod extension merged into `PresenceState`; `createAgentPresenceClient({ apiKey, tenantId }) -> { join(room), setActivity(a), leave() }` for PAP-107 and PAP-96; `toolCallToActivity()`; components above; `useAgentsHere()`; flag in the page spec schema (PAP-114). Consumes: awareness transport and schema (PAP-141), `pos_agent_` keys and “Assistant” mapping (PAP-60, PAP-55), `characters.json` glyphs and colours (PAP-103, PAP-104), tool-call hook events (PAP-107), route index (PAP-115), board card slot (PAP-102), `promptlog.read` permission (PAP-129).""",
"Definition of done": """* An orchestrator session against staging shows the agent avatar on the target page and issue card within 2 s of the first tool call; screenshots at 1024 and 1920.
* Storybook stories for the three components in three themes; axe clean.
* `docs/platform/realtime/agent-presence.md` and handbook note (PAP-112); changelog; Linear comment with a video of an agent editing beside a human.""",
"Test plan": """* Vitest: `toolCallToActivity` table (Edit → editing, Read → reading, PR review → reviewing, unknown → waiting), payload validation, visibility per audience, 30 s reset with fake timers, `sessionId` keying for the same character twice.
* Integration: presence client joins a local Hocuspocus room with a test agent key and a customer `callAs` context sees only `{ name: 'Assistant' }`.
* Playwright: mocked awareness source injects two agents and one human; panel lists both with links; a customer context on the same page sees no cursors; run at 1024 and 1920.
* Visual: Gate 3 captures of `AgentAvatar` states and the panel in three themes; reduced motion has no pulse.""",
"Demo": "Start a `pnpm agent:demo-edit PAP-42` session; open the spec page and the PM board as staff; watch the square avatar and activity chip appear and change from reading to editing; click it and open the session in the prompt log. Under two minutes.",
"Edge cases": """* 20 sessions on one issue: three avatars plus a count.
* Crash without leave: awareness timeout after 30 s, panel marks "lost".
* File without route mapping: shows on the issue only.
* Renamed character: neutral glyph.""",
"Dependencies": "PAP-141, PAP-60 (hard, encoded). Soft: PAP-103, PAP-104, PAP-107, PAP-102, PAP-115. Consumed by PAP-113, PAP-96.",
"Agent": "Builder: Nova (CRDT Engineer) with Atlas (Dispatcher) wiring hooks. Reviewer: Iris (Component Crafter); Sentinel (Security Auditor) for audience rules.",
"Size": "S: payload extension and components over existing presence.",
}

R["PAP-147"] = {
"Goal": "Find the real limits of the collab server and record sync before a tenant does: 500 users in one room and 10,000 active rooms, with p95 latency and memory measured. Tune persistence, compaction and scaling until targets pass, and run the harness nightly so regressions are caught.",
"Scope": """In:

* Harness `apps/collab-server/load/`: k6 with `xk6-websockets` for connection load plus a Node worker pool of Yjs-aware clients (`@hocuspocus/provider` with `ws`).
* Scenarios: (a) one room, 500 clients typing 2 chars/s for 10 minutes; (b) 10,000 rooms × 2 clients, one edit per 10 s; (c) reconnect storm of 2,000 clients within 5 s after a restart; (d) 1,000 awareness-only clients at 20 Hz; (e) Electric: 1,000 clients on a 100k-row `records` shape at 50 writes/s.
* Targets: p95 propagation under 250 ms (a) and 500 ms (b); RSS under 4 GB (b); zero dropped updates; storm recovered under 60 s.
* Tuning knobs documented per commit with before and after numbers; Grafana dashboard `ops/grafana/collab-load.json`; nightly job on a staging-sized VPS posting results to Linear (PAP-97 comment format).

Out: multi-region, CDN, client performance (PAP-87).""",
"Spec": """* `pnpm load:collab --scenario a --target wss://collab-staging.<domain> --duration 10m --out results/`; JSON summary plus HTML report.
* Clients authenticate with a `loadtest`-scoped agent key (PAP-60) in tenant `loadtest`, truncated after each run.
* Correctness: each client appends `${clientId}:${seq}`; after quiescence every client's text contains every token once.
* Metrics from `/metrics` (PAP-140) and `pg_stat_statements`; regression over 20 percent versus `load/baseline.json` fails the nightly job.
* A second generator host is required for (a) and (c); the harness refuses to run a scenario whose generator CPU exceeds 70 percent.""",
"Interface contract": """Exposes: `load/baseline.json` `{ scenario, metric, p50, p95, max, unit }[]`, `load/REPORT.md` template with the scaling formula (rooms per GB, connections per vCPU), `docs/platform/realtime/capacity.md`, Grafana dashboard JSON, nightly workflow `.forgejo/workflows/collab-load.yml` posting a comment `Load <date>: <pass|fail> <link>`. Consumes: server metrics and admin route (PAP-140), Grafana and Prometheus (PAP-40), agent keys (PAP-60), Electric shapes (PAP-143, PAP-270), Linear comment API (PAP-97), a second runner or VPS from PAP-50 for the generator.""",
"Definition of done": """* All five scenarios run against staging; results committed under `load/results/<date>/`.
* Targets met or an ADR (PAP-130) records the accepted limit with a follow-up issue.
* Nightly job green three consecutive nights with a summary comment here; dashboard screenshot on the PR; docs; changelog; Linear comment with the report link.""",
"Test plan": """* Unit: token-set correctness checker on synthetic client texts (missing, duplicated, all present); baseline comparison flags a 25 percent regression and passes 15 percent.
* Smoke in CI: scenario (a) scaled to 20 clients for 30 s against the compose stack proves the harness, auth and cleanup work on every PR.
* Full runs: each scenario executed against staging with the generator on a separate host; generator p95 reported alongside server p95.
* Ops: Caddy idle timeout survives 10 minutes of quiet in (b); `yjs_updates` stays under 1M rows during (b); vacuum observed.""",
"Demo": "Run `pnpm load:collab --scenario a --duration 1m --clients 50` against staging, open the Grafana collab-load dashboard and watch connections and propagation p95, then open the generated HTML report. Under two minutes.",
"Edge cases": """* Generator saturates first: split across two hosts, report generator p95.
* Redis fan-out adds latency single-instance: document the break-even.
* Client clock drift: server-echoed timestamps.
* Dirty `loadtest` tenant: refuse to start until cleanup.""",
"Dependencies": "PAP-140, PAP-143 (hard, encoded). Soft: PAP-40, PAP-60, PAP-97, PAP-50 (second generator host).",
"Agent": "Builder: Sentinel (Edge Case Hunter) writes the harness; Forge (Ops Runner) applies tuning. Reviewer: Nova signs off on limits and the ADR.",
"Size": "M: harness is straightforward; tuning iterations vary.",
}

R["PAP-148"] = {
"Goal": "Let customers keep working on a train or a flaky connection: writes queue locally in order, retry intelligently, and the UI always tells the truth about what has reached the server. This hardens the PAP-272 outbox into a product-grade feature with visible sync status.",
"Scope": """In:

* `packages/sync/src/outbox/` hardening of PAP-272: PGlite table `outbox(id, seq, mutation_id, procedure, input jsonb, depends_on, status: queued|sending|failed|conflict, attempts, last_error, created_at)`, strict FIFO per entity, concurrency 4 across entities.
* Retry: exponential 1 s → 60 s with jitter, 20 attempts then `failed`; network errors while offline retry forever; 4xx other than 409 and 429 fail immediately; 429 honours `Retry-After`.
* Dependency tracking: create-then-update chains; `tmp_` ids remapped from server responses.
* `SyncStatusIndicator` (synced, syncing n, offline n queued, attention n failed) and `SyncQueueSheet` (retry, discard, copy details); `useSyncStatus()`; captive-portal detection via `HEAD /api/health`.
* Tauri and PWA: queue survives restart; flush on `visibilitychange` and via the PAP-20 background shim.

Out: conflict UI (PAP-144, consumed), Yjs offline (`y-indexeddb`), uploads over 25 MB (PAP-37).""",
"Spec": """* Server idempotency: `idempotency_keys(tenant_id, mutation_id, response, expires_at 24h)` middleware in PAP-35 (the planned shared rate-limit and idempotency issue owns the table; this issue ships the middleware call) replays stored responses; batches of up to 25 via `POST /api/rpc/batch`.
* 409 carries `{ code: 'conflict', server: row }` → item `conflict`, emits `sync.conflict`.
* Indicator `role="status"`, icon plus text, announces at most once per 30 s.
* Storage guard: refuse new writes above 5,000 items or 50 MB with a blocking dialog.
* Spans `sync.flush` with queue depth (PAP-40).""",
"Interface contract": """Exposes: `enqueue({ procedure, input, entity: { table, id }, optimistic })`, `flush()`, `retry(id)`, `discard(id)`, `subscribe(cb)`, `useSyncStatus() -> { state, queued, failed, lastSyncedAt }`, `SyncStatusIndicator`, `SyncQueueSheet`, `OutboxItem` type, copy in `packages/collab/src/copy/sync.ts`; header `Idempotency-Key: <mutation_id>` and batch endpoint contract `{ calls: [{ id, procedure, input }] } -> { results: [{ id, ok, data | error }] }`. Consumes: PGlite and existing outbox (PAP-271, PAP-272), oRPC client and middleware (PAP-267, PAP-268), reconciler and events (PAP-143), `PendingWriteBadge` and `FailedWriteDialog` definitions (PAP-144), PWA lifecycle (PAP-18), mobile background shim (PAP-259), session refresh (PAP-223).""",
"Definition of done": """* Screenshots of the four indicator states and the sheet at 320, 768 and 1280.
* Tauri desktop restart test: queued writes persist and flush on relaunch (video).
* `docs/platform/realtime/offline.md` with state diagram; changelog; Linear comment with demo link.""",
"Test plan": """* Vitest: backoff schedule with jitter bounds, attempt counting only when online, dependency chaining and `tmp_` remap, 4xx classification, storage guard thresholds, monotonic timers under a clock jump.
* Integration: mock server replays a stored response for a duplicate `mutation_id`; a 409 moves the item to `conflict` and emits the event; batch of 25 splits correctly.
* Playwright: go offline, make 20 edits across 3 entities including create-then-update, reconnect, assert order and remapped ids in the DOM; captive portal (200 with HTML body) treated as offline; sign-out with queued writes prompts confirmation; run at 375 and 1280.
* Visual: indicator states and sheet captured at 320, 768 and 1280, both themes.""",
"Demo": "Toggle devtools offline, create a record and edit it twice, watch the indicator show “offline (3 queued)”, open the sheet, go online and see items drain with the real id appearing in the grid; kill one call with a 500 mock and retry from the sheet. Under two minutes.",
"Edge cases": """* Session expired offline: refresh first, else "Sign in to sync" with the queue kept.
* Schema rejects an old write: `failed` with message, never dropped.
* Two devices offline: server arrival order; later one gets 409.
* Failed create: optimistic row stays with an error badge until discarded.""",
"Dependencies": "PAP-143, PAP-144 (hard, encoded). Soft: PAP-272, PAP-35, PAP-18, PAP-259, PAP-223, planned shared idempotency middleware (data-layer).",
"Agent": "Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Edge Case Hunter for network scenarios, Code Reviewer).",
"Size": "M: focused package with many failure paths to test.",
}

R["PAP-149"] = {
"Goal": "Let a support agent or reviewer guide someone live: follow a person so your view mirrors their navigation, scroll and selection, or start a shared cursor session where both see each other's pointer and a highlighted element. Replaces screen sharing for support and pair review, for humans and agents.",
"Scope": """In:

* `packages/collab/src/follow/`: `useFollow(targetPrincipalId)` and leader broadcasting `{ route, params, scroll: { surfaceId, x, y }, selection, zoom, highlightedElement }` over the PAP-141 awareness room.
* Consent: staff follow customers only after acceptance or during an active support session (PAP-197); staff and agents follow each other freely; customers follow staff in a shared session.
* Shared cursor session: bidirectional cursors, "point" ping (modifier click), persistent highlight ring on any `[data-spec-component]`.
* UI: `FollowBar`, leader banner, request dialog; entry points in the presence popover and the support inbox.
* `follow_sessions(id, tenant_id, leader, follower, started_at, ended_at, reason, consented_at)` written to PAP-38.

Out: audio and video, remote control, recording.""",
"Spec": """* Leader emits at most 10 updates/s; scroll relative to `[data-presence-surface]`; follower scrolls the matching surface and shows an "out of view" arrow.
* Navigation via TanStack Router `navigate`; no permission → "Ada is on a page you cannot view".
* Follower interaction pauses following for 10 s, then "Resume".
* Requests are awareness messages `presence.request` with a 60 s timeout.
* View-only; acting for the customer requires PAP-61 impersonation.
* Commands `follow.start|stop|ping` (PAP-151); all state changes announced.""",
"Interface contract": """Exposes: `FollowState` Zod schema added to `PresenceState`, awareness messages `presence.request`, `presence.accept`, `presence.decline`, `presence.ping`, hooks `useFollow()`, `useLeaderState()`, components `FollowBar`, `FollowRequestDialog`, `LeaderBanner`, table `follow_sessions`, oRPC `follow.canFollow(target) -> { allowed, reason }`, commands above; `startFollow(principalId)` entry point used by PAP-197. Consumes: awareness and `data-presence-surface` (PAP-141), `can('presence.follow')` policies and impersonation boundary (PAP-59, PAP-61), `audit_event` writer (PAP-38), router `navigate` (PAP-16), `defineCommand` (PAP-151), window aggregation (PAP-145), `data-spec-component` attributes (PAP-120).""",
"Definition of done": """* Screenshots at 375 (customer, mobile) and 1440 (staff); Storybook stories for the three components in three themes.
* Audit entries verified for start and end; `docs/platform/realtime/follow-mode.md` with a support runbook; changelog; Linear comment with a 30-second video.""",
"Test plan": """* Vitest: consent matrix (staff→customer without consent denied, with active support session allowed, agent→customer denied, customer→staff in session allowed), 10 updates/s throttle, 60 s request timeout, 10 s pause and resume.
* Integration: `follow.canFollow` through `callAs` for each audience pair; audit rows written on start and end.
* Playwright, two contexts: staff requests, customer accepts, navigation and scroll mirror within 300 ms, follower scrolls and pauses, resumes, ends; leader navigates to a page the follower cannot view and the bar shows the notice; run at 375 and 1440.
* Visual: Gate 3 captures of the three components in three themes.""",
"Demo": "As staff, open a customer's presence avatar, click “Follow”, have the customer accept; navigate and scroll in the customer window and watch the staff window mirror it; press the ping modifier-click to ripple a button on both; stop. Under two minutes.",
"Edge cases": """* Leader offline: "Ada disconnected", session ends after 30 s.
* Leader opens a modal: mirrored via highlighted element id.
* Phone following a 1920 desktop: horizontal clamp, ring still targets the element.
* Two staff follow one customer: banner lists both.
* External URL: following pauses with a notice.""",
"Dependencies": "PAP-141 (hard, encoded). Soft: PAP-59, PAP-61, PAP-38, PAP-151, PAP-16, PAP-145, PAP-197.",
"Agent": "Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Security Auditor for consent, Visual Inspector).",
"Size": "M: consent rules and mirroring across layouts add subtlety.",
}
