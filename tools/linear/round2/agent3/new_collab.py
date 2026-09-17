"""New issues for collab: children of PAP-131, PAP-132, PAP-136 and three gap issues."""
P = "collab"
# children: key -> (parent, type, size-tag, sections)
CHILDREN = {
"PAP-131": [
 {"key": "collab/comments/schema-rls-rpc", "type": "Build", "title": "Comment schema, anchors, RLS and oRPC procedures", "sections": {
  "Goal": "Ship the data and API half of comments (PAP-131): two tables, five anchor kinds with a stable key grammar, tenant RLS plus visibility policies, and the `comments.*` procedures every UI and agent uses.",
  "Scope": """In:

* Drizzle schema `packages/db/src/schema/comments.ts`: `comment_thread` (`id`, `tenant_id`, `workspace_id`, `anchor_type`, `anchor jsonb`, `anchor_key` generated, `status: open|resolved`, `visibility: internal|shared`, `created_by`, `resolved_by`, `resolved_at`, `linear_issue_id`, `last_activity_at`), `comment` (`id`, `thread_id`, `body_json`, `body_text`, `author_id`, `author_kind: human|agent`, `mentions uuid[]`, `reactions jsonb`, `edited_at`, `deleted_at`); indexes `(tenant_id, anchor_key, status)`.
* `anchorKey(anchor)` and Zod `CommentAnchor` union in `packages/collab/comments/anchors.ts`.
* RLS by tenant (PAP-228 helpers) and policies `comment.read|create|update|delete|resolve` in PAP-59's policy format; `internal` hidden from `customer.*`.
* oRPC `comments.threads.list|create|resolve|reopen`, `comments.create|update|delete|react`; mention resolution for users, agents and characters; events `comment.created`, `comment.mentioned`, `thread.resolved` emitted on `packages/core/events`.

Out: UI, live updates, Linear escalation (siblings).""",
  "Spec": """* Key grammar: `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<canvasId>:<nodeId>`, `shot:<fileId>:<frame>`.
* Body limit 10k characters; `body_text` derived with `richTextToPlain` (PAP-142) for search.
* Agents may create, never resolve customer threads; deleted comments keep the row with `deleted_at`.""",
  "Interface contract": "Exposes tables, `CommentAnchor`, `anchorKey()`, the procedures above with `Thread` and `Comment` types in the API contract package (PAP-268), and the three event payloads `{ threadId, commentId, anchor, actorId, mentions[] }`. Consumes migrations and RLS helpers (PAP-32, PAP-228), `can()` (PAP-227), oRPC router registration and `callAs` (PAP-267, PAP-268), `richTextSchema` and `richTextToPlain` (PAP-142).",
  "Definition of done": """* Migration applied on staging; policies registered; procedures documented in the OpenAPI output (PAP-269).
* Event payloads validated against `packages/contracts/events.ts`.
* Linear comment with the `callAs` matrix results.""",
  "Test plan": """* Vitest: `anchorKey` for all five kinds, invalid anchors rejected, mention parsing of `@name` and `#entity`.
* Integration (Postgres): `callAs` matrix for customer, staff, agent across read, create, resolve on `internal` and `shared` threads; RLS blocks cross-tenant reads with a forged `anchor_key`; body over 10k rejected; events emitted once per mutation.""",
  "Demo": "Run `pnpm api:play` and call `comments.threads.create` with an entity anchor, then `comments.create` with a mention; call `threads.list` as a customer and see the internal thread missing. Under two minutes.",
  "Edge cases": """* Anchor for a deleted entity: thread stays; `list` marks `orphaned: true`.
* Mention of a user without access: stored; `comment.mentioned` carries `suppressed: true`.
* Duplicate reaction: idempotent.""",
  "Dependencies": "PAP-59 and PAP-142 (hard). PAP-32, PAP-35 children (soft). Blocks the UI and live-update children.",
  "Agent": "Built by Forge (Schema Wright) with Nova. Reviewed by Sentinel (Security Auditor).",
  "Size": "M: two tables, policies and eight procedures with a full permission matrix.",
 }},
 {"key": "collab/comments/panel-pins-composer", "type": "Build", "title": "Comment panel, pins and composer UI", "sections": {
  "Goal": "Build the visible half of comments (PAP-131): a provider that makes any page commentable, pins positioned on anchored elements, a panel listing threads for the current page or entity, and a composer with mentions built on the shared editor.",
  "Scope": """In:

* `packages/collab/comments/`: `CommentableRoot` provider, `data-comment-anchor` handling (codegen's `data-spec-key` doubles as the element anchor), pin overlay positioned from `getBoundingClientRect` and re-anchored on resize and scroll, clustering above 12 pins per viewport.
* `CommentsPanel` for the inspector slot (drawer under `lg`), `ThreadView`, `ResolveButton`, `CreateIssueButton` slot (wired by the sibling), reactions.
* Composer: `RichTextEditor` (PAP-142) in local `comment` variant with `MentionSource` for users, agents and entities; `Cmd+Enter` sends; attachments via PAP-37 signed uploads.
* Keyboard: command `comment.new` on `c` (PAP-151) targeting the focused element.

Out: data layer and procedures (sibling 1), live refresh and deep links (sibling 3).""",
  "Spec": """* Pins are `button`s with `aria-label="Comment thread, 3 replies, open"`; panel lists open first then resolved.
* Storybook stories: pin states, cluster, panel empty and populated, composer with mention popup, at 320, 768 and 1280.
* Uses TanStack Query over the sibling's procedures; optimistic insert of the author's own comment.""",
  "Interface contract": "Exposes `CommentableRoot`, `useThreads(anchor)`, `useComposer()`, `CommentsPanel`, `CommentPin`, `ThreadView`, DOM attribute `data-comment-anchor`. Consumes `comments.*` procedures and `CommentAnchor` (sibling 1), `RichTextEditor` and `MentionSource` (PAP-142), `Inspector` slot and `Drawer` (PAP-70, PAP-237), `defineCommand` (PAP-151), `AvatarStack` (PAP-71), signed uploads (PAP-37).",
  "Definition of done": """* Sample page is commentable end to end against the sibling's API; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* axe clean; composer keyboard-only; Storybook published; Linear comment with screenshots.""",
  "Test plan": """* Vitest: pin position math on resize and scroll fixtures, clustering threshold, optimistic insert and rollback.
* Component: composer mention popup opens on `@`, `Cmd+Enter` sends, empty body blocked; axe on every story.
* Playwright: press `c` on a focused field, type, send, see the pin and panel entry; resolve and reopen; drawer behaviour at 375.
* Visual: Gate 3 baselines for pins, panel and drawer.""",
  "Demo": "Open the sample records page, press `c` on a field, type a comment mentioning @Bo, send, watch the pin appear; open the panel, resolve it, reopen it. Under two minutes.",
  "Edge cases": """* Element removed after mount: pin hidden, thread listed under Unanchored.
* 50 pins: clusters with a count.
* Composer offline: pending state via PAP-148.""",
  "Dependencies": "Sibling 1 (schema and procedures), PAP-142, PAP-70 (hard). PAP-151, PAP-37 (soft). Blocks sibling 3.",
  "Agent": "Built by Iris (Component Crafter) with Nova. Reviewed by Sentinel (Visual Inspector).",
  "Size": "M: several components plus positioning and composer integration.",
 }},
 {"key": "collab/comments/live-deeplinks-linear", "type": "Build", "title": "Live updates, deep links and Linear escalation", "sections": {
  "Goal": "Finish comments (PAP-131): threads refresh live for everyone on the same anchor, `?thread=` links open and scroll to a thread, and one click turns a thread into a Linear issue with a back-link.",
  "Scope": """In:

* Live: Electric shape on `comment_thread` and `comment` scoped by tenant and anchor prefix through PAP-143's `subscribeShape`; fallback TanStack Query polling every 5 s when shapes are unavailable; typing indicator via awareness room `thread:<id>` (PAP-141).
* Deep link `?thread=<id>`: opens the panel, scrolls the anchor into view, shows "element moved" when the anchor is missing.
* Escalation: `comments.threads.createIssue({ threadId, label: Bug|Improvement })` calling PAP-101's client (or the Linear SDK directly until it lands) with title from the first comment, description containing the deep link, stores `linear_issue_id`; thread shows the issue state.

Out: notifications (PAP-136 work package 1), screenshot crops (PAP-137).""",
  "Spec": """* Shape `where`: `tenant_id = $1 and anchor_key like $2`; unsubscribe 30 s after the panel closes.
* Issue title capped at 120 characters; description template in `packages/collab/comments/escalate.md`.
* Deep link resolution happens after data load; scroll uses `scrollIntoView({ block: 'center' })`.""",
  "Interface contract": "Exposes `threads.createIssue` procedure, `useThreadLink(threadId)`, deep-link param `thread`, `LinearIssueBadge`. Consumes `subscribeShape` and `useLiveQuery` (PAP-143, PAP-271), awareness (PAP-141), Linear client `createIssue({ title, description, labels, project })` (PAP-101) with SDK fallback, siblings' procedures and components.",
  "Definition of done": """* Two contexts see each other's comments within 1 s; deep link opens the right thread; test issue created in Linear (mocked in CI, one real in staging) and linked back.
* Linear comment with the created test issue link.""",
  "Test plan": """* Vitest: deep-link parser, issue title and description builders, fallback selection when shapes are unavailable.
* Integration: shape subscription filters by anchor prefix (Electric container); polling fallback activates when the proxy returns 503.
* Playwright, two contexts: A posts, B sees within 1 s; open `?thread=<id>` in a fresh tab and assert scroll and panel; create issue against a mocked Linear endpoint and assert the badge.""",
  "Demo": "Post a comment in one browser and watch it appear in another; copy the thread link, open it in a private window after signing in and land on the thread; click Create issue and open the Linear link. Under two minutes.",
  "Edge cases": """* Linear API down: `createIssue` fails with a retry toast; nothing stored.
* Thread deleted while a deep link is open: "no longer available".
* Shape invalidated by a permission change: resubscribe (PAP-143).""",
  "Dependencies": "Siblings 1 and 2 (hard). PAP-143, PAP-141, PAP-101 (soft with fallbacks).",
  "Agent": "Built by Nova (CRDT Engineer). Reviewed by Sentinel (Code Reviewer).",
  "Size": "S: wiring over existing pieces.",
 }},
],
"PAP-132": [
 {"key": "collab/canvas/nodes-edges-loader", "type": "Build", "title": "Canvas node and edge types with graph loader", "sections": {
  "Goal": "Lay the foundation of the canvas view (PAP-132): React Flow node and edge types for the spec graph, the oRPC loader that serves the generated `FlowGraph` with a hash, and locked spec-derived elements that cannot be deleted.",
  "Scope": """In:

* `packages/collab/canvas/` on `@xyflow/react` 12: nodes `PageNode` (title, route, surface colour, audience chips, status badge, thumbnail, open-spec and open-page actions), `EntityNode`, `ExternalNode`, `StartNode`, `GroupNode`, `NoteNode`, `RegionNode`; edges `navigate`, `mutation`, `integration`, `reads`, `writes` with labels `on` and `guard`.
* oRPC `canvas.graph.get(appId) -> { graph, specHash, generatedAt }` reading `specs/.generated/flow-graph.json` (PAP-123).
* `registerNodeType(kind, component)` registry (PAP-113 adds `CharacterNode`).
* Layout: generated positions from the graph; locked flag on spec-derived nodes and edges.

Out: Yjs overlay, filters, export, performance run (siblings).""",
  "Spec": """* Node colours and typography from PAP-66 tokens; dark theme; minimum readable label at zoom 0.6.
* Edge styles distinct per kind; `reads`/`writes` dashed.
* Storybook story per node type in light and dark.""",
  "Interface contract": "Exposes `PaperCanvas` (read-only mode), node and edge components, `registerNodeType`, `canvas.graph.get`, `CanvasGraph` TypeScript type mirroring `FlowGraph`. Consumes `FlowGraph` JSON (PAP-123), spec schema (PAP-114), tokens (PAP-66), `Badge` and chips (PAP-71), PAP-127's library decision.",
  "Definition of done": """* Example graph renders with all node and edge kinds; Storybook stories published; axe clean on toolbar-less canvas focus order.
* Linear comment with 1280 screenshots in both themes.""",
  "Test plan": """* Vitest: loader maps every `FlowGraph` node and edge kind, unknown kinds fall back to a generic node with a warning, locked elements reject `onNodesDelete`.
* Component: each node type story renders and passes axe.
* Playwright: load the example graph at 1280, click a page node's open-spec action, assert navigation.""",
  "Demo": "Open `/_app/dev/canvas`, see the generated map with coloured surfaces, hover an edge label, click a page node and open its spec. Under two minutes.",
  "Edge cases": """* Node thumbnail 404: placeholder with surface icon.
* Graph with zero edges: renders nodes in a grid.
* `specHash` missing: treated as stale.""",
  "Dependencies": "PAP-123, PAP-114, PAP-127 (hard). Blocks siblings 2 and 3.",
  "Agent": "Built by Nova (Canvas Cartographer). Reviewed by Iris (visual consistency) and Sentinel (Code Reviewer).",
  "Size": "M: seven node types, five edge types and a loader.",
 }},
 {"key": "collab/canvas/yjs-overlay", "type": "Build", "title": "Collaborative overlay: notes, regions, overrides in Yjs", "sections": {
  "Goal": "Make the canvas (PAP-132) collaborative: position overrides, sticky notes, regions, hidden sets and viewport bookmarks live in a Yjs document on Hocuspocus, with presence cursors, undo and a per-selection reset to the generated layout.",
  "Scope": """In:

* Yjs doc `canvas:<appId>` (PAP-140 room) with `Y.Map`s `positions`, `notes`, `regions`, `hidden`, `viewportBookmarks`; `useCanvasOverlay(room)` merging overrides onto the generated graph.
* Presence cursors and selections via PAP-141 on `[data-presence-surface="canvas"]`.
* Undo and redo with `y-undomanager` scoped to the local user; commands `edit.undo|redo` (PAP-151).
* "Reset layout" clears overrides for selected nodes only; orphan cleanup action for overrides whose node id no longer exists.

Out: node rendering (sibling 1), filters and export (sibling 3).""",
  "Spec": """* Merge rule: generated position unless an override exists.
* Room authorised for tenant staff by PAP-140's auth hook; read-only from JSON with a banner when Hocuspocus is down.
* Notes are markdown rendered with `renderMdx` (PAP-128).""",
  "Interface contract": "Exposes `CanvasOverlayDoc` schema, `useCanvasOverlay(room) -> { positions, notes, regions, hidden, bookmarks, setPosition, addNote, reset }`, `OverlayLayer` component reused by PAP-137. Consumes `createDocProvider` (PAP-140), presence payload (PAP-141), node registry (sibling 1), `defineCommand` (PAP-151).",
  "Definition of done": """* Two contexts move a node and see it within 1 s; note added in one appears in the other; undo works per user.
* Linear comment with a two-context screenshot at 1280.""",
  "Test plan": """* Vitest: override merge (with and without override), reset for selection only, orphan detection, undo scope excludes remote changes.
* Integration: two `Y.Doc`s connected through a local Hocuspocus converge on `positions` after concurrent drags.
* Playwright, two contexts: drag in A, assert B position within 1 s; add a note; undo in A does not undo B's change.""",
  "Demo": "Open the canvas in two browsers, drag a node and add a sticky note in one, watch both appear in the other, press `mod+z` to undo only your move, click Reset layout on a selection. Under two minutes.",
  "Edge cases": """* Two users drag one node: last writer wins with a cursor highlight.
* Hocuspocus down: read-only with a banner.
* Renamed page id: orphan override listed for cleanup.""",
  "Dependencies": "Sibling 1, PAP-140 (hard). PAP-141, PAP-151, PAP-128 (soft). Blocks sibling 3.",
  "Agent": "Built by Nova (CRDT Engineer). Reviewed by Sentinel (Code Reviewer).",
  "Size": "M: Yjs schema, merge and undo semantics.",
 }},
 {"key": "collab/canvas/filters-export-perf", "type": "Build", "title": "Filters, deep links, export and 300-node performance run", "sections": {
  "Goal": "Finish the canvas view (PAP-132) as a usable tool: audience and surface filters, edge-kind toggles, search and focus, minimap, deep links, PNG and SVG export, a stale banner when specs changed, and measured 55 fps or better on a 300-node graph.",
  "Scope": """In:

* Route `/_app/dev/canvas` toolbar: audience filter, surface filter, edge kind toggles (`reads` hidden by default above 500 edges), search and focus node, fit view, minimap, reset layout, export.
* Deep link `?node=<id>&audience=<id>` restoring filter and focus; keyboard: arrows move selection, `Enter` opens spec, `/` search.
* Export via `html-to-image`: current viewport or selected region, capped at 8k pixels.
* Stale banner when `specHash` differs from the loaded graph with a reload action.
* Performance: `onlyRenderVisibleElements`, memoised nodes, edge simplification below zoom 0.4; CDP fps trace committed.
* Comment anchors on nodes (`canvas_node`) via PAP-131.

Out: pen tool (PAP-157), org chart (PAP-113).""",
  "Spec": """* Filters compose (audience AND surface AND edge kinds); URL is the single source of filter state.
* 320 and 375 render read-only with a "larger screen recommended" notice.
* Export file name `<app>-canvas-<date>.png|svg`.""",
  "Interface contract": "Exposes route, `CanvasToolbar`, `useCanvasFilters()` (URL-backed), `exportCanvas({ format, region })`, comment anchor `canvas:<canvasId>:<nodeId>`. Consumes siblings 1 and 2, `useThreads` (PAP-131), touch pan and pinch (PAP-154), thumbnails from PAP-82 when present.",
  "Definition of done": """* Filters, deep links, export and stale banner work; fps ≥ 55 on a generated 300-node graph with numbers in the comment.
* Screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; `docs/collab/canvas.md`; CHANGELOG entry.""",
  "Test plan": """* Vitest: filter composition, URL round-trip, stale detection, export bounds clamp.
* Playwright: filter by audience and assert hidden nodes; open a deep link and assert focus; export PNG and assert non-empty file; mock a new `specHash` and assert the banner; run at 1280 and 1920, read-only notice at 375.
* Performance: CDP trace while panning 5 s on a 300/600 generated graph, mean fps ≥ 55.
* Visual: Gate 3 baselines at five widths, both themes.""",
  "Demo": "Filter to customer pages, hide `reads` edges, search “Invoice” and focus it, copy the URL and open it in a new tab, export PNG. Under two minutes.",
  "Edge cases": """* Thousands of `reads` edges: hidden by default.
* 20k-pixel export: viewport or selection only.
* Deep link to a filtered-out node: filter widened with a notice.""",
  "Dependencies": "Siblings 1 and 2 (hard). PAP-131, PAP-154, PAP-82 (soft).",
  "Agent": "Built by Nova (Canvas Cartographer). Reviewed by Sentinel (Visual Inspector, Code Reviewer).",
  "Size": "M: toolbar features plus the performance pass.",
 }},
],
"PAP-136": [
 {"key": "collab/notifications/inbox-preferences", "type": "Build", "title": "Inbox UI, bell badge and preferences page", "sections": {
  "Goal": "Give users the visible half of notifications (PAP-136): a bell with a live unread badge, a popover of the latest items, a full inbox with filters, and a preferences page where each kind is mapped to channels, all over the tables of PAP-136 work package 1 (the notification core).",
  "Scope": """In:

* `NotificationBell` with popover (latest 10, mark read, archive) in the console and portal shells (PAP-62, PAP-63).
* `/_app/inbox`: filters by kind and unread, grouped by day, keyboard navigation, bulk mark read.
* `/_app/settings/notifications`: matrix of kinds by channel (in-app, email, Slack), test send button.
* Live badge via Electric shape on `notification` for the current user (PAP-143) with 30 s polling fallback.
* oRPC `notifications.list|markRead|archive`, `preferences.get|set` (thin wrappers over core repositories).

Out: digests and quiet hours (sibling 2), Slack (sibling 3), delivery (core).""",
  "Spec": """* Rows use the core's `Notification` type; no second schema.
* Popover `role="dialog"`; badge `aria-live="polite"` announcing counts at most once per 30 s.
* Under `md` the inbox is a full-screen list.""",
  "Interface contract": "Exposes `NotificationBell`, `InboxList`, `PreferenceMatrix`, procedures above. Consumes `Notification`, `NotificationKind` registry and `resolvePreferences()` from PAP-136 work package 1 (the notification core), `subscribeShape` (PAP-143), shells (PAP-62, PAP-63), primitives (PAP-67).",
  "Definition of done": """* Badge updates within 2 s of a core insert; inbox and settings at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; Linear comment with screenshots.""",
  "Test plan": """* Vitest: unread count derivation, day grouping across timezones, matrix state to preference rows.
* Integration: `callAs(userA)` cannot list userB's notifications.
* Playwright, two contexts: mention triggers a badge within 2 s; mark read clears it; toggle a kind off in settings and confirm the core suppresses the next one (via `/__test` clock and job run).
* Visual: Gate 3 baselines at the seven widths.""",
  "Demo": "Get mentioned from a second account, watch the bell, open the popover, mark read, open the inbox and filter to mentions, open settings and switch email off for mentions. Under two minutes.",
  "Edge cases": """* 1,000 unread: badge shows 99+.
* Deleted source: item stays with "no longer available".
* Shape unavailable: polling fallback, no visible difference.""",
  "Dependencies": "Notification core (hard). PAP-143, PAP-62, PAP-63 (soft). Blocks siblings 2 and 3 for UI slots.",
  "Agent": "Built by Nova with Iris on components. Reviewed by Sentinel (Visual Inspector).",
  "Size": "M: three screens over an existing API.",
 }},
 {"key": "collab/notifications/digests-quiet-hours", "type": "Build", "title": "Digests, quiet hours and burst collapse", "sections": {
  "Goal": "Make notifications (PAP-136) calm: per-kind hourly or daily digests, quiet hours in the user's timezone, collapse of bursts from one source, and per-tenant preferences with a global fallback.",
  "Scope": """In:

* `notification_preference.digest: none|hourly|daily` and `quiet_hours jsonb { start, end, tz }` columns and settings controls (added to sibling 1's matrix).
* Worker jobs (PAP-43): `notifications.digest.hourly`, `notifications.digest.daily` grouping held items per user and kind into one email (PAP-235 `renderEmail`) and one in-app row; quiet-hours hold and release job.
* Collapse rule in the core's pipeline hook: same kind and source within 10 minutes becomes one row with a count.
* Preference resolution: per-tenant row, else global row, else kind defaults.

Out: channels, inbox UI, Slack (siblings and core).""",
  "Spec": """* Quiet hours computed with `@date-fns/tz`, DST-safe; a digest holds at most 50 items with a link to the inbox.
* Digest idempotency key `(user, kind, bucket)`.
* Collapse never merges items from different sources.""",
  "Interface contract": "Exposes `resolvePreferences(userId, tenantId, kind)` extension with digest and quiet hours, jobs above, `collapse(notification, existing)` hook. Consumes the core's pipeline hooks and `notification_delivery`, `defineJob` and cron (PAP-43), `renderEmail` (PAP-235), settings controls (sibling 1).",
  "Definition of done": """* A mention during quiet hours is held and delivered at the window end; a daily digest email renders the grouped items; Linear comment with delivery logs.""",
  "Test plan": """* Vitest: quiet hours across midnight and a DST change, digest grouping and the 50-item cap, collapse within and outside 10 minutes, preference fallback order, idempotency key stability.
* Integration: `/__test` clock (PAP-240) advanced past the window releases held items; digest job run twice produces one email.
* Snapshot: digest email HTML.""",
  "Demo": "Set quiet hours to now, trigger a mention, see nothing arrive, advance the test clock past the window and watch it land; switch mentions to daily digest and run the job to receive one grouped email in Mailpit. Under two minutes.",
  "Edge cases": """* Timezone missing: fall back to tenant default.
* 300 items in a digest: 50 plus a link.
* User in two tenants: separate rows.""",
  "Dependencies": "Notification core, PAP-43 (hard). PAP-235, PAP-240, sibling 1 (soft).",
  "Agent": "Built by Forge (Ops Runner) with Nova. Reviewed by Sentinel (Edge Case Hunter for time rules).",
  "Size": "S: jobs and rules over the core.",
 }},
 {"key": "collab/notifications/slack-channel", "type": "Build", "title": "Slack channel and tenant Slack configuration", "sections": {
  "Goal": "Deliver notifications (PAP-136) to Slack: tenant admins configure an incoming webhook, each kind renders a Block Kit message, deliveries retry through the core, and a revoked webhook is surfaced in settings.",
  "Scope": """In:

* `tenant_slack_config(tenant_id, webhook_url encrypted, default_channel, kind_channels jsonb, status)`; settings section in `/_app/settings/notifications` (admin only) with "Test send".
* `SlackChannel implements Channel` registered with the core; Block Kit templates per kind in `packages/collab/notifications/templates/slack/`.
* Revoked or failing webhook: `status: broken` after three failures and a banner for admins.
* oRPC `slack.configure`, `slack.test`.

Out: Slack app and OAuth (later), interactive buttons.""",
  "Spec": """* Webhook URL encrypted with the server-side secret helper (data-layer gap; fall back to `SecretStore` from PAP-17 until it lands).
* Templates keep payloads under 40 blocks; links use the deep-link grammar of the source.
* Deliveries recorded in the core's `notification_delivery` with `channel: 'slack'`.""",
  "Interface contract": "Exposes `SlackChannel`, `tenant_slack_config`, procedures above, Block Kit template snapshots. Consumes `Channel { send(notification, recipient) }` interface and `registerChannel()` from the core, secret encryption helper, admin permission `notifications.admin` (PAP-59), settings page slot (sibling 1).",
  "Definition of done": """* Test webhook receives a Block Kit message for `comment.mentioned` and `issue.needs_justin`; broken webhook shows the banner; Linear comment with a screenshot of the Slack message.""",
  "Test plan": """* Vitest: template snapshots for every kind, block count limit, status transition after three failures.
* Integration: mock Slack server asserts payload schema and returns 410 to trigger `broken`; `callAs(staff)` cannot read the webhook URL.
* Playwright: admin configures the webhook, clicks Test send, sees success; run at 1280.""",
  "Demo": "Paste a test webhook in settings, click Test send, see the message in Slack, revoke the webhook, trigger a mention and watch the broken banner appear. Under two minutes.",
  "Edge cases": """* Slack rate limit 429: honour `Retry-After` via the core.
* Kind routed to a channel that no longer exists: default channel.
* Webhook URL not on `hooks.slack.com`: rejected.""",
  "Dependencies": "Notification core (hard). Sibling 1, PAP-59, PAP-17 or the secret helper (soft).",
  "Agent": "Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor for the webhook secret).",
  "Size": "S: one channel adapter and a settings section.",
 }},
],
}

GAPS = [
 {"key": "collab/notification-core", "title": "Build notification core independent of comments: kinds registry, delivery worker, in-app badge and email channel, `issue.needs_justin` and gate kinds",
  "phase": "P1", "type": "Build", "priority": 1, "surfaces": ["Staff", "Agent"], "milestone": "Comments and canvas", "state": "Backlog",
  "blockedBy": ["PAP-43"], "blocks": ["PAP-136"],
  "sections": {
  "Goal": "Provide the delivery engine the Justin queue (PAP-94), gates (PAP-88, PAP-89), changelog (PAP-133) and imports (PAP-199) already assume, without waiting for comments: a kinds registry, a worker that turns domain events into notification rows, an in-app channel and an email channel. PAP-136 adds the inbox UI, digests and Slack on top.",
  "Scope": """In:

* Drizzle schema `packages/db/src/schema/notifications.ts`: `notification` (`id uuidv7`, `tenant_id`, `user_id`, `kind`, `title`, `body_md`, `link`, `source jsonb`, `actor_id`, `actor_kind`, `seen_at`, `read_at`, `archived_at`, `created_at`), `notification_preference` (`user_id`, `tenant_id`, `kind`, `channels jsonb`), `notification_delivery` (`notification_id`, `channel`, `status: queued|sent|failed|suppressed`, `attempts`, `provider_id`, `error`, `sent_at`).
* Kinds registry `packages/collab/notifications/kinds.ts`: `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `changelog.published`, `agent.blocked`, `import.finished`, `comment.mentioned`, `comment.replied`, `thread.resolved`; each with default channels per audience and templates (markdown in-app, React Email via PAP-235).
* Worker (PAP-43 jobs): subscribes to `packages/core/events`, expands recipients (user ids or audience segments via PAP-55, cap 500), applies preferences, writes rows, enqueues deliveries with 3 retries; idempotency key `(kind, source, recipient, bucket)`.
* Channels: `InAppChannel` (row insert; badge consumers subscribe via PAP-143) and `EmailChannel` (provider adapter from the transactional email package gap, Mailpit in dev, per-kind one-click unsubscribe JWT).
* `notify(kind, { recipients, payload })` helper and `Channel` interface for PAP-136's Slack.

Out: inbox UI, preferences page, digests, quiet hours, Slack (PAP-136 children), push (realtime push transport).""",
  "Spec": """* Actor never notified of own action; recipients without access to the source are `suppressed`.
* Latency: in-app row within 2 s of emit; email within 60 s.
* `issue.needs_justin` applies the PAP-94 batching rule (max five open, one message per batch).
* Templates render tokens from PAP-66 inline; plain-text alternative generated.""",
  "Interface contract": "Exposes: `Notification`, `NotificationKind`, `defineKind({ id, audiences, defaultChannels, template })`, `registerChannel(name, impl)`, `Channel { send(n, recipient) -> DeliveryResult }`, `notify()`, `resolvePreferences(userId, tenantId, kind)`, event subscriptions for the kinds above, unsubscribe route `/n/unsubscribe/:token`. Consumes: `emit()`/`subscribe()` from `packages/core/events` (data-layer event bus gap; until it lands, an in-process emitter in `packages/collab/notifications/bus.ts` with the same signature), `defineJob` (PAP-43), audience segments (PAP-55), email adapter (`packages/email` gap or Resend directly with an allowlist), `renderEmail` (PAP-235), tenant and user tables (PAP-33).",
  "Definition of done": """* A `review.gate_failed` event produces an in-app row and a Mailpit email in CI; `issue.needs_justin` reaches Justin's user with batching.
* Vitest and integration tests green; `docs/collab/notifications.md` core section explaining how to add a kind; CHANGELOG entry; Linear comment with delivery logs.""",
  "Test plan": """* Vitest: kind registry validation, recipient expansion with the 500 cap, suppression rules (self, no access, unsubscribed kind), idempotency on retry, template rendering snapshots (email HTML, in-app markdown), unsubscribe token verify.
* Integration (Postgres, pg-boss, Mailpit): emit `review.gate_failed` and assert the row within 2 s and the email within 60 s; a failing provider retries three times then `failed`; `callAs(userB)` cannot read userA's rows.
* Contract: event payloads for every kind validated against `packages/contracts/events.ts`.""",
  "Demo": "Run `pnpm notify:demo review.gate_failed --to justin`, watch the row appear in the `notification` table (or the dev inbox page) and the email land in Mailpit; click unsubscribe in the email and re-run to see `suppressed`. Under two minutes.",
  "Edge cases": """* Provider outage: deliveries queued up to 24 h, then failed with an ops alert (PAP-40).
* Event with 5,000 recipients: digest-only mode, capped.
* Duplicate event after retry: idempotent.
* Kind emitted before registration: rejected with a logged error.""",
  "Dependencies": "PAP-43 (hard). Soft: PAP-55, PAP-235, PAP-33, event bus and email package gaps (data-layer), PAP-94. Blocks PAP-136; consumed by PAP-88, PAP-89, PAP-133, PAP-199, PAP-97.",
  "Agent": "Built by Forge (Ops Runner) with Nova on channel interfaces. Reviewed by Sentinel (Security Auditor for unsubscribe tokens) and Atlas for the Justin batching rule.",
  "Size": "M: schema, registry, worker and two channels, all testable in CI.",
 }},
 {"key": "collab/runtime-docs-store", "title": "Build a runtime docs store for tenant-authored documents: Yjs-backed pages in Postgres with the same routes, search registration and comment anchors as repo MDX",
  "phase": "P2", "type": "Build", "priority": 3, "surfaces": ["Customer", "Staff"], "milestone": "Knowledge surfaced everywhere", "state": "Backlog",
  "blockedBy": ["PAP-128", "PAP-142"], "blocks": [],
  "sections": {
  "Goal": "Give tenants Notion-style documents without a git commit: pages authored in the collaborative editor, stored per tenant in Postgres as Yjs state plus a rendered snapshot, served through the same docs routes, search kind and comment anchors as repo MDX. PAP-203 (Notion import) writes here.",
  "Scope": """In:

* Schema `doc_page(id, tenant_id, workspace_id, parent_id, slug, title, icon, audience[], status: draft|published|archived, yjs_room, snapshot_json, snapshot_text, created_by, updated_by, updated_at)` and `doc_page_version(page_id, version, snapshot_json, author_id, created_at)`; RLS by tenant; policies `doc.view|edit|publish`.
* Editing: `RichTextEditor` (PAP-142) in room `doc:<tenant>:doc_page:<id>` on PAP-140; snapshot written on room unload and every 60 s; version saved on publish.
* Routes `/_app/docs/t/$slug` (staff) and `/_public/docs/t/$slug` (published customer pages) inside PAP-128's docs shell with the same sidebar tree (tenant section) and TOC.
* Search: registered as kind `doc` with `source: tenant` (PAP-138); comment anchors `doc:<pageId>#<blockId>` (PAP-131) using Tiptap block ids.
* Import API `docs.import({ pages: [{ slug, title, richText }] })` used by PAP-203.

Out: templates gallery, page-level permissions beyond audience, publishing to external sites.""",
  "Spec": """* Slugs unique per workspace; moves keep a redirect row.
* `snapshot_text` from `richTextToPlain` for search; render uses `renderRichText` for public pages (no editor bundle).
* Version history drawer reuses PAP-128's History UI with versions instead of commits.""",
  "Interface contract": "Exposes: tables above, oRPC `docs.pages.list|get|create|update|publish|move|import`, `docs.versions.list|restore`, `TenantDocPage` component, sidebar tree contribution `useTenantDocsTree()`. Consumes: `RichTextEditor`, `renderRichText`, `richTextToPlain` (PAP-142), rooms (PAP-140), docs shell, sidebar and History UI (PAP-128), `registerSearchable` (PAP-39, PAP-138), `CommentAnchor` (PAP-131), `can()` (PAP-59).",
  "Definition of done": """* Staff creates, edits collaboratively, publishes; customer sees the published page publicly; search finds it; a comment anchors to a block.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; `docs/collab/runtime-docs.md`; CHANGELOG entry; Linear comment.""",
  "Test plan": """* Vitest: slug uniqueness and redirect on move, snapshot debounce, version creation on publish, import mapping.
* Integration (Postgres): RLS and `doc.view` matrix via `callAs`; public route returns only `published` pages with `customer` audience.
* Playwright, two contexts: co-edit a page, publish, open the public URL anonymously, search for a phrase, comment on a paragraph; restore a version.
* Visual: Gate 3 baselines for editor and public page at the seven widths.""",
  "Demo": "Create “Onboarding checklist”, type with a colleague in another browser, publish, open the public link in a private window, search “checklist” from the palette, comment on the second paragraph. Under two minutes.",
  "Edge cases": """* Publish while others edit: snapshot from the current Yjs state; editing continues.
* Slug collision on import: suffix `-2` and report.
* 5 MB page: images via PAP-37, text capped at 1 MB with a notice.
* Hocuspocus down: read-only from the last snapshot.""",
  "Dependencies": "PAP-128, PAP-142 (hard). Soft: PAP-140, PAP-138, PAP-131, PAP-59, PAP-37. Consumed by PAP-203 and the in-app help issue.",
  "Agent": "Built by Nova (CRDT Engineer) with Quill on content conventions. Reviewed by Sentinel (Security Auditor for public routes, Visual Inspector).",
  "Size": "M: schema plus glue between editor, docs shell, search and comments.",
 }},
 {"key": "collab/in-app-help", "title": "Add contextual in-app help: help panel bound to page spec `purpose` and docs deep links, first-visit product tour, keyboard hint overlay",
  "phase": "P2", "type": "Build", "priority": 3, "surfaces": ["Customer", "Staff"], "milestone": "Knowledge surfaced everywhere", "state": "Backlog",
  "blockedBy": ["PAP-128"], "blocks": [],
  "sections": {
  "Goal": "Connect the docs engine to the page the user is on: a help panel that shows the page spec's `purpose`, linked docs and related commands; a first-visit tour built from spec annotations; and a keyboard hint overlay from the command manifest. Part of the onboarding golden path for PAP-5.",
  "Scope": """In:

* `HelpPanel` in the inspector slot (`?` or `help.open` command): page `purpose` from the spec (PAP-114), `docs[]` links resolved through PAP-128 (repo or tenant pages), related commands from `commands.manifest.json` (PAP-151) with effective chords (PAP-153), "Ask a question" that opens a comment thread on the page (PAP-131).
* Tour: spec section `tour: [{ target: specKey, title, body }]` rendered with popovers anchored to `data-spec-key`; shown once per user per page version (`user_tour_seen`), replayable from the panel.
* Keyboard hint overlay: hold `alt` for 600 ms to show chord badges on visible `CommandButton`s; `help.shortcuts` opens the full sheet (PAP-151).
* Spec validator rule (PAP-115): `docs[]` paths must exist; warn when `purpose` is missing.

Out: chat assistant, video tutorials, third-party tour libraries.""",
  "Spec": """* Panel content cached per route; tour steps limited to 7; overlay excluded under reduced motion (static badges instead).
* Tour respects `FocusScope` (PAP-152) and is keyboard navigable.
* Customer pages show only `customer` audience docs.""",
  "Interface contract": "Exposes: `HelpPanel`, `useHelpForRoute()`, `TourProvider`, spec fields `help.docs[]`, `help.tour[]` (added to PAP-114 schema), table `user_tour_seen(user_id, route, version, seen_at)`, command `help.open`. Consumes: spec loader and `purpose` (PAP-114, PAP-120), docs resolution and `renderMdx` (PAP-128), manifest and `CommandButton` (PAP-151), chords (PAP-153), `Popover` (PAP-237), `Inspector` slot (PAP-70), comments (PAP-131), audience (PAP-55).",
  "Definition of done": """* Template pages show purpose and docs in the panel; the sample page's tour runs once and replays; `alt` overlay shows chords.
* Screenshots at 375, 1024 and 1440 in light and dark; axe clean; `docs/collab/in-app-help.md`; CHANGELOG entry; Linear comment.""",
  "Test plan": """* Vitest: docs path resolution (repo, tenant, missing), tour step limit, seen-state versioning, chord badge mapping.
* Integration: validator fails a spec with a missing doc path.
* Playwright: first visit shows the tour, complete it, reload shows nothing, replay from the panel; press `?` and open a linked doc; hold `alt` and assert badges; customer context sees only customer docs; run at 375 and 1440.
* Visual: Gate 3 baselines for panel, tour popover and overlay.""",
  "Demo": "Open the records page as a new user, step through the three-step tour, press `?` to read the purpose and open the linked doc, hold `alt` to see shortcut badges, click “Ask a question” and post it. Under two minutes.",
  "Edge cases": """* Tour target missing after a layout change: step skipped with a console warning.
* Page without spec: panel shows the app-level help doc.
* Overlay while a Dialog is open: badges only inside the dialog.""",
  "Dependencies": "PAP-128 (hard). Soft: PAP-114, PAP-151, PAP-153, PAP-131, PAP-152, PAP-115, runtime docs store.",
  "Agent": "Built by Quill (Page Spec Writer) with Iris on the panel and tour. Reviewed by Sentinel (Visual Inspector).",
  "Size": "S: panel, tour and overlay over existing data.",
 }},
]


# FIX-6 (2026-09-17): collab/notification-core is merged into PAP-136 work package 1; never create it.
MERGED = {"collab/notification-core": "PAP-136"}
GAPS = [g for g in GAPS if g["key"] not in MERGED]
