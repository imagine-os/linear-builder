# Round 4 digest: Multiplayer & Realtime (`realtime`)

Benchmarks: Liveblocks (presence, comments, history, notifications), Yjs / Hocuspocus (rooms, awareness, persistence), PartyKit (rooms, broadcast, hibernation), Figma multiplayer (cursors, cursor chat, reactions, version history), Google Docs (presence, version history, offline), Notion (page history, mentions, offline), Linear sync engine (single connection state, optimistic writes), ElectricSQL / Zero / Replicache (record sync), Supabase Realtime / Ably (channels, push), tldraw sync (snapshots, headless clients)

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| CRDT choice with benchmark and ADR | covered | PAP-139 |  |
| Hocuspocus server with auth hook, persistence, room grammar | covered | PAP-140 |  |
| Yjs offline persistence (`y-indexeddb`) | covered | PAP-140, PAP-145 | provider wraps it |
| Document version history, snapshots, restore, diff | gap | r4/realtime/doc-history | Google Docs/Notion/Liveblocks parity; PAP-379 assumes it |
| Presence data path and privacy filtering | partial | PAP-141, r4/realtime/presence-core | split child; awareness filtering decision added |
| Presence components (avatars, cursors, selection, viewers) | partial | PAP-141, r4/realtime/presence-components | split child |
| Typing indicators, cursor chat, reactions | gap | r4/realtime/ephemeral-signals | Figma/Slack parity; chat and comments need typing |
| Agents as live participants | covered | PAP-146 |  |
| Follow mode and shared cursor sessions | covered | PAP-149 | deferred |
| Collaborative rich text core (Tiptap + Yjs) | partial | PAP-142, r4/realtime/editor-core | split child on the zero-slack chain |
| Editor toolbar, commands, mentions, markdown, images | partial | PAP-142, r4/realtime/editor-features | split child |
| Headless Yjs client for agents and jobs | gap | r4/realtime/headless-client | importers and agents need to write docs, not only appear |
| Live record hooks and shape registry | covered | PAP-326 |  |
| Reconciler for optimistic writes and conflict events | covered | PAP-327 | amendment: `syncMeta()` column helper |
| Permission-driven resubscribe and lag measurement | covered | PAP-328 |  |
| Permission change propagation to rooms and shapes | gap | r4/identity/permission-propagation | owned by identity in round 4 |
| Conflict UX specification | covered | PAP-144 | spec and mocks only |
| Conflict UX implementation wired to reconciler events | gap | r4/realtime/conflict-ux-impl | PAP-144 names follow-ups that did not exist |
| Offline write queue with retry, ordering, status | covered | PAP-148, PAP-272 | amendment: adopt PAP-304 batch shape |
| Unified connection status and reconnect policy | gap | r4/realtime/connection-status | four transports, three indicators today |
| Multi-window and tab sync via BroadcastChannel and Yjs relay | covered | PAP-145 |  |
| Push transport: live events channel (shape + SSE) | partial | PAP-381, r4/realtime/live-events-channel | split child |
| Web Push and desktop OS notifications | partial | PAP-381, r4/realtime/web-push | split child |
| Mobile push (APNs, FCM) | partial | PAP-381, r4/app-shell/native-push-registration | owned by app-shell in round 4 (deferred); plugs into `PushProvider` from `r4/realtime/web-push` |
| Load harness and CI smoke | partial | PAP-147, r4/realtime/load-harness | split child |
| Staging load runs, tuning, baseline, nightly regression | partial | PAP-147, r4/realtime/load-runs-tuning | split child; second host is soft |
| Horizontal scaling of the collab server (Redis fan-out, replicas) | partial | PAP-140, PAP-147 | behind a flag; break-even documented by the load child |
| WebSocket message and document size limits, throttling | covered | PAP-140 |  |
| Room-level authorization and read-only connections | covered | PAP-140 |  |
| Impersonation and guest identities in rooms | partial | PAP-61, r4/identity/resource-grants | amendment on PAP-61; guest presence rule in presence-core |
| Realtime test kit (memory provider, chaos, fixtures) | gap | r4/realtime/test-kit | every consumer project rebuilds scaffolding |
| Conformance suite and golden fixtures | covered | PAP-478 |  |
| Realtime contract and kernel wiring | covered | PAP-475, PAP-481 |  |
| Sync inspector and dev tooling | covered | PAP-328 |  |
| Realtime metrics and dashboards | covered | PAP-140, PAP-40 |  |
| Canvas collaboration overlay | covered | PAP-321 | collab consumes rooms |
| Comments live updates | covered | PAP-319 | collab |
| Support chat with live sync | covered | PAP-411 | growth |
| Cross-device draft autosave for non-shared fields | partial | PAP-142 | local mode only; a `draft:` room convention could add it in v0.2 |
| Peer-to-peer or WebRTC transport | gap | - | non-goal per project description |
| Voice, video or screen share | gap | - | non-goal; follow mode replaces screen share for support |
| Sleep, wake and token refresh handling in transports | partial | r4/realtime/connection-status, PAP-140 | amendment on PAP-140 plus the new hook |
| Local data wipe on sign-out and revocation for Yjs stores | covered | r4/data-layer/local-data-protection | data-layer owns; wipes `y-indexeddb` |
| Per-user shapes in the proxy | partial | PAP-270, r4/realtime/live-events-channel | amendment on PAP-381 and proxy support |

## New issues

| Key | Title | Parent | Size | Model | Deferred |
|---|---|---|---|---|---|
| `r4/realtime/live-events-channel` | `live_event` table, `publishLiveEvent()`, per-user Electric shape with SSE fallback, `useLiveEvents()` and `useJobProgress()` hooks, TTL job and the `LiveEventKind` registry | PAP-381 | M | Sonnet 5 / high |  |
| `r4/realtime/web-push` | Web Push and desktop notifications: VAPID keys, `push_subscription`, service-worker handler, permission prompt after an explicit action, sender job with 410 pruning and Tauri desktop OS notifications | PAP-381 | M | Sonnet 5 / medium |  |
| `r4/realtime/load-harness` | Collab load harness: k6 `xk6-websockets` connection load, Node pool of Yjs-aware clients, five scenario definitions, token-set correctness checker and the 30-second CI smoke | PAP-147 | M | Opus 5 / high |  |
| `r4/realtime/load-runs-tuning` | Staging load runs against the five scenarios, tuning knobs with before and after numbers, `load/baseline.json`, the Grafana collab-load dashboard and the nightly regression job | PAP-147 | M | Opus 5 / high |  |
| `r4/realtime/editor-core` | `RichTextEditor` core: Tiptap 3 with Yjs collaboration and carets, room and local modes, `richTextSchema`, `renderRichText`, `richTextToPlain`, undo manager and read-only binding | PAP-142 | M | Opus 5 / high |  |
| `r4/realtime/editor-features` | Editor features: toolbar and bubble menu on design-system primitives, `editor.*` commands with shortcuts, mentions of users, agents and entities through `MentionSource`, markdown round-trip, image upload and the comment-variant stories | PAP-142 | M | Sonnet 5 / high |  |
| `r4/realtime/presence-core` | `PresenceProvider` on ephemeral page rooms, the awareness payload schema, `usePresence`, `useMyPresence` and `useViewers`, `presence.view` policy filtering on the server and the page-spec flag | PAP-141 | M | Opus 5 / medium |  |
| `r4/realtime/presence-components` | `PresenceAvatars`, `LiveCursor`, `SelectionHighlight` and `ViewersBadge` on `AvatarStack` with colour tokens, idle and reduced-motion rules, accessibility labels and stories in three themes | PAP-141 | S | Sonnet 5 / medium |  |
| `r4/realtime/doc-history` | Yjs document history: periodic and named snapshots, a version list with authors derived from the updates log, restore as a new update, rich-text diff rendering and retention | - | M | Opus 5 / medium |  |
| `r4/realtime/conflict-ux-impl` | Implement the conflict UX: `useConflicts()` on reconciler events, `ConflictBanner`, `StaleFieldIndicator`, `RemoteChangeFlash`, `PendingWriteBadge` and `FailedWriteDialog` with keep-mine, use-theirs, compare and `edit.undoRemote` | - | M | Sonnet 5 / high |  |
| `r4/realtime/connection-status` | Unified connection status: `useConnectionStatus()` composing Hocuspocus, Electric, SSE and outbox states, one `ConnectionIndicator`, jittered reconnect policy, token refresh on `4401` and sleep or wake handling | - | S | Sonnet 5 / medium |  |
| `r4/realtime/headless-client` | Headless Yjs client for agents and jobs: `openRoomHeadless(room, credential)` in Node with transaction-origin attribution, batch edit helpers, a `doc.edit` job wrapper and the import writer used by Notion and template imports | - | S | Sonnet 5 / medium |  |
| `r4/realtime/ephemeral-signals` | Ephemeral signals over awareness: typing indicators for comments and chat, cursor chat bubbles and emoji reaction bursts with throttling, privacy rules and reduced-motion behaviour | - | S | Sonnet 5 / low |  |
| `r4/realtime/test-kit` | Realtime test kit: in-memory Yjs provider, awareness simulator, fake shape stream, network chaos helpers and two-context Playwright fixtures published from the realtime contract | - | S | Sonnet 5 / medium |  |

## Amendments to existing specs

* **PAP-148** (Interface contract): Align with PAP-304 (now `r4/data-layer/idempotency-batch`): the batch endpoint is `POST /api/v1/rpc/batch { mutations: [{ id, procedure, input, idempotencyKey }] } -> { results: [{ id, ok, data | error }] }` (not `{ calls: [...] }`), the batch itself carries an `Idempotency-Key`, and 409 bodies are `{ code: 'CONFLICT', server: row }` per Contracts §4. Server-side the `idempotency_keys` table is owned there; this issue only sends the header and persists keys in `_outbox`.
* **PAP-141** (Spec): Awareness privacy needs a mechanism, not only a policy: Hocuspocus broadcasts awareness to every connection in a room, so "server filters awareness by policy" requires either an `onAwarenessUpdate` extension that rewrites the update per recipient using `context.principal`, or audience-partitioned ephemeral rooms `page:<tenant>:<route>:<audienceClass>`. `r4/realtime/presence-core` benchmarks both at 200 connections and records the choice; until then customer surfaces default to `realtime.presence: false`. Work is split into `r4/realtime/presence-core` and `r4/realtime/presence-components`.
* **PAP-140** (Spec): Add: (1) `createDocProvider` takes `getToken()` and on `4401` refreshes once and reconnects without losing buffered edits; (2) the provider listens to `visibilitychange`, `online` and Tauri `resume` and probes before retrying, using the shared `reconnectPolicy` from `r4/realtime/connection-status`; (3) permission re-check subscribes to the `permission.changed` topic (`r4/identity/permission-propagation`) in addition to the 5-minute timer; (4) `verifySessionToken()` and `verifyApiKey()` come from PAP-223 and `r4/identity/agent-keys` (amendment on PAP-223); (5) `yjs_updates` gains `principal_id` and `origin jsonb` so `r4/realtime/doc-history` can attribute versions.
* **PAP-327** (Spec): Column ownership: `packages/db` ships a `syncMeta()` column helper (from PAP-32 conventions) that adds `mutation_id uuid` and `updated_by uuid` to a table; the shape registry lint (PAP-326) refuses to register a table without it. The stamping middleware sets both from the request context; PAP-43 jobs stamp `updated_by = actorId ?? service id` so worker writes reconcile too.
* **PAP-381** (Spec): Per-user shapes need proxy support: PAP-270 appends only `tenant_id`; the registry entry for `live_events` declares `perUser: true` and the proxy then also appends `user_id = <principal>`; tenant-wide events are a separate audience-filtered shape. SSE fallback uses `Last-Event-ID` with the uuidv7 ordering. Work is split into `r4/realtime/live-events-channel` and `r4/realtime/web-push`; the Tauri mobile bullet (APNs, FCM, `push_device`) moves to `r4/app-shell/native-push-registration` (deferred), which implements the `PushProvider` interface from `r4/realtime/web-push`.
* **PAP-147** (Definition of done): Make the second-host dependency explicit: if the PAP-50 second runner host is not available before 2026-09-30, scenarios (a) and (c) run at 50 percent scale from the VPS, are marked `partial` in `load/baseline.json`, and a follow-up issue schedules the full run; the nightly job still runs (b), (d) and (e) at full scale. Work is split into `r4/realtime/load-harness` and `r4/realtime/load-runs-tuning`.
* **PAP-144** (Dependencies): The implementation follow-up in realtime is `r4/realtime/conflict-ux-impl` (five components, `useConflicts()`, `ConflictBoundary`, `edit.undoRemote`); tables (PAP-342, PAP-333) and spec-builder (PAP-120) consume that issue rather than reimplementing the mocks. The approved Gate 3 references from this issue are the visual contract it must match.
* **PAP-142** (Dependencies): Work is split into `r4/realtime/editor-core` (binding, schema, renderer, plain text, undo, read-only; blocks PAP-131) and `r4/realtime/editor-features` (toolbar, commands, mentions, markdown, images). PAP-131 and PAP-317 depend on the core only, which shortens the zero-slack chain 140 → 142 → 131 by roughly one session.

## Cross-project suggestions

* **collab**: Docs History pane (PAP-128) and tenant docs `docs.versions.*` (PAP-379) consume `r4/realtime/doc-history` — Both promise version lists and restore; the primitive now lives in realtime with authors and diff.
* **tables**: Grid editing (PAP-342) and record page (PAP-333) mount `ConflictBoundary` from `r4/realtime/conflict-ux-impl` — Removes per-cell conflict wiring from the grid and gives the record page field attribution for free.
* **identity**: Hocuspocus and the shape proxy subscribe to `permission.changed` — Already filed as `r4/identity/permission-propagation`; realtime consumes it in PAP-140 and PAP-328.
* **migration**: Notion (PAP-419) and template (PAP-426) importers write documents through `r4/realtime/headless-client` `doc.edit` jobs — Gives imports attribution, idempotency and the server store acknowledgement instead of raw provider code.
* **agents**: PAP-107 hooks use `openRoomHeadless` for agent edits and PAP-146 presence together — Agents currently appear in rooms but cannot write into them from Node.
* **app-shell**: `OfflineBanner` (PAP-234) and the shells (PAP-62, PAP-63) render `ConnectionIndicator` from `r4/realtime/connection-status` — One connection state across the app instead of three indicators.
* **app-shell**: `r4/app-shell/native-push-registration` implements `PushProvider` from `r4/realtime/web-push` and reuses the `push.deliver` job — Round-4 dedup: realtime dropped its own mobile-push child so APNs, FCM and `push_device` have one owner; the sender job and payload rules stay in realtime.
* **quality**: PAP-86 realtime presence flows and PAP-246 projects adopt `@paperos/contract-realtime/testing` fixtures — `twoContexts` and `measurePropagation` make the presence and lag budgets comparable across suites.

## What was missing and why it matters

1. Version history was assumed by collab (PAP-379 `docs.versions.*`, PAP-128 History pane) and owned by nobody; the updates log existed but no snapshots, authors, restore or diff, which every multiplayer product treats as table stakes.
2. The conflict UX was a spec with static mocks and a promise of follow-ups that were never filed, so the grid, record page and offline queue had interfaces to consume but no components behind them.
3. Four transports each reported their own health and reconnect policy (Hocuspocus provider, Electric shapes, SSE, outbox); a user would see disagreeing indicators and twenty tabs would reconnect in a herd; one hook and one policy fixes both, including token refresh and laptop wake.
4. Agents could be seen in rooms but could not write into them from Node, and importers would each open raw providers; a headless client with attribution, chunking and a job wrapper serves migration, agents and canvas resets.
5. Two zero-slack or capacity-critical M issues (PAP-142 editor, PAP-141 presence) and two multi-part ones (PAP-381 push, PAP-147 load) hid two or three sessions each; splitting lets the editor core unblock comments a session earlier, makes the awareness privacy mechanism an explicit decision, and hands mobile push to app-shell's deferred registration issue instead of duplicating it.
