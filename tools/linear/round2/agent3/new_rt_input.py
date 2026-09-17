"""New issues for realtime and input: children of PAP-143, PAP-151, PAP-155 and the push transport gap."""
CHILDREN = {
"PAP-143": [
 {"key": "realtime/record-sync/live-hooks-registry", "type": "Build", "title": "Live record hooks and shape registry additions", "sections": {
  "Goal": "Turn PAP-271's raw shape hooks into the record-level API every view uses (PAP-143): `useRecord`, `useRecordChanges`, reference-counted subscriptions, per-frame batching, and shape definitions for tables and PM entities with tenant and permission predicates.",
  "Scope": """In:

* `packages/sync/src/live/`: `useRecord(table, id)`, `useRecordChanges(id)` (5 s window with `changedFields`, `actor`, `at`), `subscribeShape(def)` with reference counting, 30 s idle unsubscribe, LRU cap of 50 shapes with a console warning.
* Shape registry entries: `records`, `fields`, `views` (PAP-161) and PM entities (PAP-100), each with `where` built from tenant and PAP-228 predicates on the proxy side.
* Batching: incoming rows applied per animation frame; live queries suspended for off-screen virtualised rows via a `visible` flag.

Out: reconciliation (sibling 2), resubscribe and inspector (sibling 3).""",
  "Spec": """* Change window uses server `updated_at` and `updated_by`; the actor is resolved through the `users` shape.
* `ShapeDef { table, where, columns? }`; identical defs share one subscription.""",
  "Interface contract": "Exposes hooks above, `registerShape()`, `ShapeDef`, `sync.remoteChange` event. Consumes `useShape`, `useLiveQuery`, PGlite client (PAP-271), proxy `/api/sync/shape` (PAP-270), predicate compiler (PAP-228), table definitions (PAP-161, PAP-100).",
  "Definition of done": """* Grid demo cells flash with the actor avatar on remote change; shape count stays under 50 in a 60-view stress story; Linear comment with a 768 and 1440 screenshot pair.""",
  "Test plan": """* Vitest: ref counting (two consumers, one unsubscribe keeps the shape), idle timer, LRU eviction and warning, change window expiry with fake timers, batching coalesces 100 rows into one render.
* Integration: Electric container; registering a `records` shape returns only the tenant's rows; permission predicate excludes restricted rows.
* Playwright: two contexts, remote edit flashes within 500 ms.""",
  "Demo": "Open the grid demo in two browsers, edit a cell in one and watch the flash and avatar in the other; open React DevTools and confirm one shape per table. Under two minutes.",
  "Edge cases": """* Same shape requested with different column lists: separate subscriptions.
* Actor row not yet synced: flash without avatar, filled when it arrives.""",
  "Dependencies": "PAP-271, PAP-270 (hard). PAP-161, PAP-100, PAP-228 (soft). Blocks siblings 2 and 3.",
  "Agent": "Built by Nova (CRDT Engineer). Reviewed by Sentinel (Code Reviewer).",
  "Size": "M: hooks and registry with careful lifecycle tests.",
 }},
 {"key": "realtime/record-sync/reconciler", "type": "Build", "title": "Reconciler for optimistic writes and conflict events", "sections": {
  "Goal": "Make optimistic writes and incoming shape rows agree (PAP-143): stamp every write with a `mutation_id`, drop optimistic rows when their echo arrives, compare expected and actual state field by field, and emit the `sync.conflict` event PAP-144 and PAP-148 consume.",
  "Scope": """In:

* API middleware in PAP-267 stamping `mutation_id uuid` and `updated_by principal_id` on written rows (Forge adds the columns to synced tables).
* Client: optimistic rows carry `_pending: true`; `mutate(proc, input, { optimistic, expect: (before) => after })` from PAP-272 extended; echo matching by `mutation_id`; mismatch emits `sync.conflict { recordId, table, conflictingFields, mine, theirs, actor, at }`.
* Ordering by server `lsn`; duplicate echoes dropped idempotently; out-of-order arrival handled by version comparison.

Out: hooks (sibling 1), UI (PAP-144), retry (PAP-148).""",
  "Spec": """* Comparison is per field with type-aware equality (dates, decimals as strings, arrays order-insensitive for multi-select).
* Remote rows apply before outbox replay after a reconnect.""",
  "Interface contract": "Exposes `mutate()` extension, `Reconciler` class, `sync.conflict` event type in `packages/sync/events.ts`. Consumes outbox (PAP-272), oRPC middleware chain (PAP-267), synced table columns (PAP-32), hooks (sibling 1).",
  "Definition of done": """* Optimistic edit resolves without flicker; a forced mismatch emits a conflict with the right fields; Linear comment with the test output.""",
  "Test plan": """* Vitest: echo match drops the optimistic row, mismatch lists exactly the conflicting fields, out-of-order `lsn` handled, duplicate echo idempotent, type-aware equality fixtures, reconnect applies remote before replay.
* Integration: API middleware stamps columns on a real write; `updated_by` matches the `callAs` principal.""",
  "Demo": "Edit a cell, watch the pending style clear when the echo arrives; in devtools run `__paperosSync.forceConflict('records', id)` and see the conflict event logged with `conflictingFields`. Under two minutes.",
  "Edge cases": """* Server rejects the write: optimistic row reverted, event `sync.rejected`.
* Row deleted remotely before the echo: conflict with `theirs: null`.""",
  "Dependencies": "Sibling 1, PAP-272, PAP-267 (hard). Blocks sibling 3; consumed by PAP-144, PAP-148.",
  "Agent": "Built by Nova (CRDT Engineer) with Forge (Schema Wright) for columns. Reviewed by Sentinel (Edge Case Hunter).",
  "Size": "M: subtle ordering semantics with a thorough unit suite.",
 }},
 {"key": "realtime/record-sync/resubscribe-lag", "type": "Build", "title": "Permission-driven resubscribe and lag measurement", "sections": {
  "Goal": "Close PAP-143: when a permission change invalidates a shape the client drops and resubscribes, developers can inspect sync state, and the 500 ms p95 lag budget is measured with a real Electric container in CI.",
  "Scope": """In:

* `409 shape-invalid` handling: drop local rows for the shape, resubscribe, replay pending writes.
* Dev inspector `window.__paperosSync` listing shapes, row counts, `lsn` lag, outbox length and `forceConflict()`.
* Playwright lag test in `ops/compose/test.yml` (Postgres, Electric, API): 50 API writes, DOM polled in a second context, p95 asserted under 500 ms; result JSON committed.
* `docs/platform/realtime/record-sync.md` with data-flow diagram.

Out: hooks and reconciler (siblings).""",
  "Spec": """* Resubscribe within one cycle (under 2 s); rows the user lost access to disappear without a reload.
* Inspector is tree-shaken out of production builds unless `?debug=sync`.""",
  "Interface contract": "Exposes inspector shape `{ shapes[], lagMs, outboxLength }`, compose test stack reused by PAP-147 and PAP-148, docs. Consumes siblings 1 and 2, proxy 409 semantics (PAP-270), `/__test` role change endpoint (PAP-240).",
  "Definition of done": """* Revoking a role removes rows within one resubscribe cycle; lag test green in CI with p95 under 500 ms; docs merged; Linear comment with the measurement.""",
  "Test plan": """* Vitest: 409 handler drops and resubscribes once, pending writes replayed after resubscribe.
* Integration: role revoked via `/__test` (PAP-240) and rows vanish within 2 s.
* Playwright: lag measurement as described; inspector shows a non-zero shape list.""",
  "Demo": "Open the grid demo with `?debug=sync`, read `__paperosSync.shapes`, revoke your role in another tab and watch rows disappear; run `pnpm test:e2e --grep lag` and read the p95. Under two minutes.",
  "Edge cases": """* Repeated 409s (flapping role): back off to 30 s and show a toast.
* Electric restart mid-test: subscription resumes from the last offset.""",
  "Dependencies": "Siblings 1 and 2 (hard). PAP-270, PAP-240 (soft).",
  "Agent": "Built by Nova. Reviewed by Sentinel (Code Reviewer).",
  "Size": "S: handler, inspector and one measured test.",
 }},
],
"PAP-151": [
 {"key": "input/commands/registry-core", "type": "Build", "title": "Command registry core, scoping and chord matcher", "sections": {
  "Goal": "Build the heart of PAP-151: `defineCommand`, a registry with a scope stack, chord and sequence matching on PAP-150's `Chord`, `when` guards, conflict warnings and a build-time manifest that fails on duplicate IDs.",
  "Scope": """In:

* `packages/input/src/commands/`: `defineCommand({ id, title, description?, icon?, keywords?, scope, shortcut?, when?, permission?, argsSchema?, agentCallable?, voice?, run })`, `CommandRegistry { register, unregister, execute, list, setBindingsResolver }`, hooks `useCommand`, `useCommands`, `useShortcut`.
* `CommandScopeProvider` scope stack (global → page route id → focused component); innermost match wins.
* Matcher: chords, sequences (`g i`, 1 s timeout), platform display, browser-reserved warnings, `allowInInput` guard.
* `pnpm commands:manifest` → `commands.manifest.json`; Vitest fails on duplicate IDs.

Out: palette UI (sibling 2), agent endpoint and defaults (sibling 3).""",
  "Spec": """* IDs dot-namespaced; `when(ctx)` receives `{ route, selection, focusedScope, permissions, capabilities, isEditing }`.
* `permission` checked with `can()`; hidden commands excluded from `list`.
* Letters matched on `event.code`, symbols on `event.key`.""",
  "Interface contract": "Exposes the API above, `CommandDef` and `CommandContext` types, `commands.manifest.json` schema, `setBindingsResolver` seam for PAP-153. Consumes `parseChord`, `matchChord`, `formatChord` (PAP-150), `can()` (PAP-227), spec `commands:` section (PAP-114, optional).",
  "Definition of done": """* Registry used by a sample page with spec-declared commands; manifest committed; Linear comment with test summary.""",
  "Test plan": """* Vitest: chord parsing on macOS and Linux mocks, sequences and timeout, scope precedence with sibling scopes, `when` guards, `allowInInput` inside a contenteditable, duplicate-ID failure, permission hiding, reserved-chord warning, non-Latin layout matching.
* Bench: `list()` over 2,000 commands under 2 ms.""",
  "Demo": "In the sample page press `g i` and watch navigation; register a duplicate ID in a scratch file and run `pnpm commands:manifest` to see the failure. Under two minutes.",
  "Edge cases": """* Async `run` throws: error toast hook, registry healthy.
* Same chord in sibling scopes: focused wins.""",
  "Dependencies": "PAP-150 (hard). PAP-59, PAP-114 (soft). Blocks siblings 2 and 3.",
  "Agent": "Built by Nova. Reviewed by Sentinel (Code Reviewer).",
  "Size": "M: the core API and matcher with a wide unit suite.",
 }},
 {"key": "input/commands/palette-help-ui", "type": "Build", "title": "Command palette and help sheet UI", "sections": {
  "Goal": "Give PAP-151 its face: a `CommandPalette` with fuzzy search, grouped and virtualised results, shortcut hints, recents and argument prompts, plus the `?` shortcuts sheet and a `CommandButton` that exposes any command with `aria-keyshortcuts`.",
  "Scope": """In:

* `CommandPalette` on PAP-70 `CommandBar` and PAP-237 `Dialog`: `fuse.js` 7 scoring over title and keywords, grouped by scope, at most 50 virtualised results, recents in `localStorage`, argument prompts from `argsSchema` (typed inputs and entity pickers via a `pickers` slot), opened with `mod+k`; full-screen sheet under `md`.
* Help sheet on `?` or `mod+/` listing active commands by scope with effective chords.
* `CommandButton commandId` and `ShortcutHint`.
* Storybook: empty, results, argument prompt, help sheet in three themes.

Out: registry (sibling 1), endpoint (sibling 3).""",
  "Spec": """* `role="combobox"`, results `role="listbox"`, `aria-activedescendant`; results update under 16 ms for 2,000 commands.
* Palette stacks above an open Dialog and restores focus.""",
  "Interface contract": "Exposes components above and `usePaletteProvider()` slot for PAP-138's search mode. Consumes registry `list(ctx)` and `execute` (sibling 1), `CommandBar`, `Dialog`, `Combobox` (PAP-70, PAP-237, PAP-238), effective chords via the resolver seam (PAP-153).",
  "Definition of done": """* Palette opens on every page; screenshots at 375 and 1280; Storybook stories axe clean; Linear comment.""",
  "Test plan": """* Vitest: scorer ranking fixtures, grouping, recents persistence, argument prompt validation from Zod.
* Component: keyboard navigation, `aria-activedescendant` updates, focus restore after close, stacking over a Dialog.
* Playwright: `mod+k`, type, `Enter` executes at 375 (sheet) and 1280; `?` opens the sheet.
* Performance: 2,000-command filter under 16 ms.
* Visual: Gate 3 captures, three themes.""",
  "Demo": "Press `mod+k`, type “theme”, run it; press `?` to browse shortcuts; run a command with an argument prompt and pick an entity. Under two minutes.",
  "Edge cases": """* No results: empty state with "Search everything" hint.
* Very long titles: truncated with tooltip.""",
  "Dependencies": "Sibling 1, PAP-70 (hard). PAP-237, PAP-238, PAP-153 (soft).",
  "Agent": "Built by Nova with Iris on visuals. Reviewed by Sentinel (Visual Inspector).",
  "Size": "M: one complex component and a sheet.",
 }},
 {"key": "input/commands/agent-endpoint-defaults", "type": "Build", "title": "Agent execution endpoint, telemetry and default commands", "sections": {
  "Goal": "Complete PAP-151: agents run commands through an audited oRPC endpoint limited to `agentCallable` commands, every execution emits telemetry, and the default global commands ship so every app has navigation, layout and help commands from day one.",
  "Scope": """In:

* oRPC `commands.execute({ id, args })` for principals with scope `commands:execute`; checks `agentCallable`, `permission` via `can()`, validates `args` with `argsSchema`; audit row in PAP-38 `{ commandId, principal, args hash, result }`.
* Telemetry `command.executed { id, source: keyboard|palette|menu|voice|gamepad|api }` and `command.failed` to PAP-40; failures toast.
* Defaults: `nav.*` from spec-declared navigation, `ui.toggleSidebar|toggleInspector|toggleTheme`, `edit.undo|redo`, `help.shortcuts`, `search.open`.
* Docs page generated from the manifest.

Out: registry and palette (siblings).""",
  "Spec": """* Server-side commands run in a headless registry with the agent's principal context; UI-only commands are marked `agentCallable: false` and rejected with `NOT_CALLABLE`.
* Rate limit per key from PAP-60 applies.""",
  "Interface contract": "Exposes `commands.execute` contract `{ id, args } -> { ok, result | error: { code } }`, telemetry event types, default command IDs. Consumes registry (sibling 1), oRPC and `callAs` (PAP-267, PAP-268), audit writer (PAP-38), agent scopes (PAP-60), observability (PAP-40).",
  "Definition of done": """* Agent key executes an allowed command and is denied on a non-callable one with audit rows; defaults work in the template; docs page committed; Linear comment.""",
  "Test plan": """* Vitest: allow and deny matrix (callable, permission, scope, schema), telemetry payloads.
* Integration: `callAs(agent)` executes `nav.goToInbox` and receives `NOT_CALLABLE` for `ui.toggleTheme`; audit rows present; `callAs(customer)` lacks scope → 403.
* Playwright: defaults toggle sidebar and theme from the palette.""",
  "Demo": "Run `pnpm agent:cmd nav.goToInbox` with a test key and see `{ ok: true }` plus the audit row; try `ui.toggleTheme` and read `NOT_CALLABLE`. Under two minutes.",
  "Edge cases": """* Args fail schema: 400 with field errors.
* Command throws server-side: audited as failed, no retry.""",
  "Dependencies": "Sibling 1, PAP-35 children (hard). PAP-38, PAP-60, PAP-40 (soft).",
  "Agent": "Built by Nova. Reviewed by Sentinel (Security Auditor).",
  "Size": "S: an endpoint, telemetry and a handful of commands.",
 }},
],
"PAP-155": [
 {"key": "input/dnd/sensors-sortable-list", "type": "Build", "title": "dnd-kit sensors on the input abstraction and SortableList", "sections": {
  "Goal": "Start PAP-155 with the engine: a dnd-kit wrapper whose sensors come from the input abstraction so mouse, touch and pen behave consistently, a `SortableList` with optimistic reorder and revert, and the fractional-indexing helper consumers use for `sort_key`.",
  "Scope": """In:

* `packages/input/src/dnd/`: `@dnd-kit/core` 6.x and `@dnd-kit/sortable` wrapper; `PointerSurfaceSensor` on `usePointerSurface` (PAP-150): mouse drag after 4 px, touch after 250 ms long-press with `haptic('selection')` (PAP-154), pen immediately with barrel button or after 4 px.
* `SortableList items getId onReorder renderItem strategy`; `onReorder({ from, to, item, items })` optimistic with revert on rejected promise; `DragHandle`, `DragOverlay`.
* `between(a, b)` from `fractional-indexing` 3.x exported for `sort_key` storage.
* Auto-scroll near edges; `closestCenter` collision.

Out: keyboard grammar (sibling 2), kanban, grid, drop zone, cross-window (sibling 3).""",
  "Spec": """* Overlay and two neighbours are the only re-rendering items during a drag (React Profiler assertion).
* Reduced motion: no transform animation.""",
  "Interface contract": "Exposes `DndProvider`, `PointerSurfaceSensor`, `SortableList`, `DragHandle`, `DragOverlay`, `between()`, `ReorderEvent` type. Consumes `usePointerSurface` and `THRESHOLDS` (PAP-150), `haptic()` and long-press (PAP-154), primitives (PAP-67).",
  "Definition of done": """* Sample list reorders by mouse, touch and pen; Storybook stories; Linear comment with screenshots at 375 and 1280.""",
  "Test plan": """* Vitest: `between()` ordering across 1,000 inserts without precision loss, revert on rejected promise, sensor activation thresholds per pointer type.
* Playwright: pointer drag at 1280; touch long-press drag on `hasTouch` while a plain swipe scrolls at 375.
* Performance: profiler assertion in a 10,000-row virtual list.""",
  "Demo": "Drag an item with the mouse, then long-press and drag on the touch emulator, watch the order persist via the mocked callback. Under two minutes.",
  "Edge cases": """* Drag within nested scroll containers: innermost auto-scrolls first.
* Alt-tab mid-drag: cancel and restore.""",
  "Dependencies": "PAP-150 (hard). PAP-154, PAP-67 (soft). Blocks siblings 2 and 3.",
  "Agent": "Built by Nova (Views Engineer). Reviewed by Sentinel (Code Reviewer).",
  "Size": "M: sensors plus one component with performance constraints.",
 }},
 {"key": "input/dnd/keyboard-announcements", "type": "Build", "title": "Keyboard alternative, announcements and focus restore", "sections": {
  "Goal": "Make drag-and-drop (PAP-155) work for everyone: a keyboard grammar to pick up, move and drop, screen-reader announcements through the shared announcer, focus restored after drop or cancel, and registry commands so keymaps and voice can trigger the same moves.",
  "Scope": """In:

* Customised `KeyboardSensor`: `Space`/`Enter` pick up, arrows move, `PageUp/PageDown` change container, `Home/End`, `Space` drops, `Escape` cancels; instructions announced on pickup.
* Announcement templates in `packages/input/src/copy/dnd.ts` ("Moved Task A to position 3 of 8 in Doing", denied reasons) via `LiveAnnouncer` (PAP-152).
* `useFocusRestore` to the moved item's handle after drop, original handle after cancel.
* Commands `dnd.pickUp|drop|cancel` (PAP-151).
* Snapshot tests of every announcement string.

Out: sensors (sibling 1), high-level components (sibling 3).""",
  "Spec": """* Off-screen targets in virtualised lists scroll into view before announcing.
* RTL flips arrow semantics.""",
  "Interface contract": "Exposes `KeyboardSensor`, `announceDnd(event)`, copy keys, commands. Consumes `LiveAnnouncer`, `useFocusRestore` (PAP-152), `defineCommand` (PAP-151), sibling 1's provider.",
  "Definition of done": """* Keyboard-only reorder and cross-container move work on the sample pages; announcement snapshots committed; NVDA and VoiceOver spot check recorded for PAP-156; Linear comment.""",
  "Test plan": """* Vitest: grammar state machine (pick up, move, drop, cancel, invalid keys ignored), announcement templates incl. plurals and RTL, focus restore targets.
* Playwright: `Tab` to a handle, `Space`, arrows, `Space`, assert order and `aria-live` text; `Escape` restores focus to the original handle; virtualised off-screen target scrolls into view.""",
  "Demo": "Tab to a card handle, press `Space`, `ArrowDown` twice, `Space`, and read the live region text in the devtools a11y panel; press `Escape` on another pickup and see focus return. Under two minutes.",
  "Edge cases": """* Item deleted during a keyboard drag: cancel with announcement.
* Screen reader in browse mode: handle exposes instructions via `aria-describedby`.""",
  "Dependencies": "Sibling 1, PAP-152 (hard). PAP-151 (soft). Blocks sibling 3; feeds PAP-156.",
  "Agent": "Built by Iris (Motion and Input Stylist) with Nova. Reviewed by Sentinel (Edge Case Hunter).",
  "Size": "S: grammar, strings and focus handling.",
 }},
 {"key": "input/dnd/kanban-grid-dropzone-crosswindow", "type": "Build", "title": "KanbanDnd, SortableGrid, DropZone and cross-window drag", "sections": {
  "Goal": "Finish PAP-155 with the components views use: cross-column kanban moves with `canDrop` reasons and WIP limits, a 2D sortable grid, a drop zone for files and items, multi-select drags with a count overlay, and drags between the main window and a detached panel.",
  "Scope": """In:

* `KanbanDnd columns cards onMove canDrop` with `rectIntersection`, WIP limit check, denied cursor plus tooltip plus announcement.
* `SortableGrid` (2D) and `DropZone accept onDrop` (files and items).
* Multi-select: selected items from PAP-165 move together; overlay shows "3 items".
* Cross-window: pointer leaves the window → `dnd.transfer { payload, sourceWindowId }` over PAP-145 `WindowBus`; target shows a drop hint and completes; web pop-out fallback (PAP-263) supported.
* Template sample pages using all three; Storybook stories with reduced motion.

Out: sensors and keyboard (siblings).""",
  "Spec": """* `canDrop(source, target) -> true | { reason }`; reason shown in tooltip and announcement.
* Remote list changes during a drag keep it alive and recompute on drop.""",
  "Interface contract": "Exposes `KanbanDnd`, `SortableGrid`, `DropZone`, `CanDropResult`, window message `dnd.transfer`. Consumes siblings 1 and 2, `WindowBus` (PAP-145), grid selection (PAP-165), file upload hooks (PAP-37), primitives (PAP-67).",
  "Definition of done": """* Kanban, grid and drop zone in template pages; cross-window drag on Tauri Linux recorded; screenshots at 375, 1024 and 1440; docs `docs/platform/input/drag-drop.md`; changelog; Linear comment.""",
  "Test plan": """* Vitest: `canDrop` handling, multi-select payloads, WIP limit reason, transfer message schema.
* Playwright: cross-column move, denied drop onto a full column with reason, file drop onto `DropZone`, multi-select drag overlay count, cross-window drag via two pages in one context using the web fallback.
* Visual: Gate 3 captures of overlay and denied state, three themes.""",
  "Demo": "Drag a card into a full column and read the reason, select three rows and drag them together, drop a file on the zone, pop out the inspector and drag a row into it. Under two minutes.",
  "Edge cases": """* Target window closes mid-transfer: source shows "drop target closed".
* File over 25 MB: rejected with a notice (PAP-37 limit).""",
  "Dependencies": "Siblings 1 and 2 (hard). PAP-145, PAP-165, PAP-37 (soft). Consumed by PAP-167, PAP-173, PAP-102.",
  "Agent": "Built by Nova (Views Engineer). Reviewed by Sentinel (Code Reviewer); Iris reviews overlay styling.",
  "Size": "M: three components and the cross-window path.",
 }},
],
}

GAPS = [
 {"key": "realtime/push-transport", "project": "realtime", "title": "Build the push transport: server-to-client notification and job-progress channel (Electric shape or SSE) plus Web Push and Tauri mobile push (APNs/FCM)",
  "phase": "P2", "type": "Build", "priority": 3, "surfaces": ["Customer", "Staff"], "milestone": "Scale and offline tested", "state": "Backlog",
  "blockedBy": ["PAP-143"], "blocks": [],
  "sections": {
  "Goal": "Replace polling with one live event channel: `useLiveEvents()` delivers notifications, import and job progress and agent status to open clients over an Electric shape (SSE fallback), and Web Push plus Tauri mobile push reach users when the app is closed. PAP-136, PAP-199, PAP-113 and PAP-20 currently fall back to polling or bundle a plugin with no server side.",
  "Scope": """In:

* Table `live_event(id uuidv7, tenant_id, user_id?, kind, payload jsonb, created_at, expires_at)` with a 24 h TTL job (PAP-43); producers write through `publishLiveEvent()`; Electric shape per user (PAP-143, PAP-270); SSE `GET /api/live` fallback when shapes are unavailable (Firefox private mode, corporate proxies).
* `useLiveEvents(kinds?)` and `useJobProgress(jobId)` in `packages/sync/live/`; `LiveEventKind` registry: `notification.created`, `job.progress`, `job.finished`, `agent.status`, `import.progress`.
* Web Push: `push_subscription(user_id, endpoint, keys, ua, created_at)`, VAPID keys via PAP-17, service worker handler in PAP-18's PWA, permission prompt only after an explicit user action.
* Tauri mobile: `tauri-plugin-notification` (PAP-260) device tokens registered to `push_device(user_id, platform, token)`; server sender adapters for APNs and FCM behind a `PushProvider` interface; APNs credentials are a Needs Justin ask filed by PAP-20's children, not here.
* Sender job: for `notification.created` events with `channels.push`, deliver to subscriptions and devices with retry and pruning of dead endpoints.

Out: in-app UI (PAP-136), marketing push, SMS.""",
  "Spec": """* Delivery to open clients within 2 s; push within 30 s.
* Payloads under 4 KB; push bodies contain only title, body and deep link, never PII beyond the title.
* Dead endpoint (410) pruned after one failure; FCM invalid token pruned on `UNREGISTERED`.""",
  "Interface contract": "Exposes: `publishLiveEvent({ kind, tenantId, userId?, payload })`, `useLiveEvents()`, `useJobProgress()`, `LiveEventKind` registry, `PushProvider { send(device, message) }` with `WebPushProvider`, `ApnsProvider`, `FcmProvider`, oRPC `push.subscribe|unsubscribe`, tables above. Consumes: shape subscriptions (PAP-143, PAP-270), API and SSE route (PAP-267), jobs (PAP-43), service worker (PAP-18), mobile plugin and tokens (PAP-260), secrets (PAP-17), notification rows (PAP-136 work package 1, the notification core) as the main producer, job progress hooks (PAP-43, PAP-199).",
  "Definition of done": """* Import progress bar in PAP-199's UI updates live without polling; a notification created while the tab is closed arrives as a Web Push on Chrome desktop and Android; Tauri Android receives an FCM push (APNs documented, pending credentials).
* `docs/platform/realtime/push.md` with the decision matrix (shape vs SSE vs push); changelog; Linear comment with a video.""",
  "Test plan": """* Vitest: kind registry, payload size guard, endpoint pruning rules, provider selection per device, SSE reconnect with `Last-Event-ID`.
* Integration (compose stack): `publishLiveEvent` reaches a subscribed client within 2 s via shape and via forced SSE fallback; TTL job deletes expired rows; Web Push sent to a mock push service (`web-push` test server) and 410 prunes the subscription.
* Playwright: job progress bar on the import page updates from 0 to 100 without network polling (assert no repeated `GET` calls); permission prompt appears only after clicking "Enable notifications".
* Manual: Android emulator FCM delivery recorded.""",
  "Demo": "Start a CSV import and watch the progress bar move without refresh; enable push, close the tab, trigger a mention from another account and see the desktop notification; click it to land on the thread. Under two minutes.",
  "Edge cases": """* Shape unavailable: SSE fallback with identical hook output.
* 10,000 events in a burst: coalesced per kind per second.
* User revokes browser permission: subscription marked `revoked` on the next 410.
* Tauri desktop: OS notifications via the plugin, no push service needed.""",
  "Dependencies": "PAP-143 (hard). Soft: PAP-43, PAP-18, PAP-260, PAP-17, PAP-267, PAP-136 work package 1 (notification core). Consumed by PAP-136, PAP-199, PAP-113, PAP-96.",
  "Agent": "Built by Nova (CRDT Engineer) with Forge (Ops Runner) for providers and keys. Reviewed by Sentinel (Security Auditor for push payloads and VAPID handling).",
  "Size": "M: one table and hook family plus three provider adapters behind an interface.",
 }},
]
