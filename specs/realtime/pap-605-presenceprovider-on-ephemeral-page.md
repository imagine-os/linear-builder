---
identifier: "PAP-605"
title: "`PresenceProvider` on ephemeral page rooms, the awareness payload schema, `usePresence`, `useMyPresence` and `useViewers`, `presence.view` policy filtering on the server and the page-spec flag"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: "PAP-141"
children: []
blockedBy: ["PAP-140"]
blocks: ["PAP-146", "PAP-149", "PAP-481", "PAP-606", "PAP-611"]
key: "r4/realtime/presence-core"
url: "https://linear.app/paperos/issue/PAP-605/presenceprovider-on-ephemeral-page-rooms-the-awareness-payload-schema"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:15.322Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-605: `PresenceProvider` on ephemeral page rooms, the awareness payload schema, `usePresence`, `useMyPresence` and `useViewers`, `presence.view` policy filtering on the server and the page-spec flag

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M

**Goal**

First half of PAP-141: the presence data path with its privacy rule. Every page joins an ephemeral room, publishes a validated awareness payload, and reads who else is here, while the collab server ensures a customer never receives another customer's state. Components are the sibling; agents (PAP-146) and follow mode (PAP-149) extend this payload.

**Scope**

In: `packages/collab/src/presence/{provider,schema,hooks}.ts(x)`: `PresenceProvider` joining `page:<tenantId>:<routeId>` (`ephemeral: true`, PAP-140) and optional entity rooms; Zod `PresenceState` `{ principalId, principalType: 'human'|'agent', name, avatarUrl?, color, cursor?: { x, y, surfaceId }, selection?: { entityId, fieldId? } | { from, to }, viewport?, focusedRoute, lastActive, idle }`; hooks `usePresence()`, `useMyPresence()`, `useViewers(entityId)`; throttle 50 ms for cursors, immediate for selection and route; idle after 60 s or hidden tab; dedupe of one principal across windows (`x2` count, PAP-145 aggregates); server-side awareness filtering by `presence.view` policy (PAP-227) implemented as a Hocuspocus extension that rewrites awareness updates per recipient, or audience-partitioned rooms `page:<tenant>:<route>:<audienceClass>` when per-recipient filtering proves too costly (decision recorded in the doc); page-spec flag `realtime.presence: true|false` (PAP-114) default true for staff surfaces, false for customer surfaces; DOM attribute `data-presence-surface`.

Out: Avatars, cursors, highlights and badges (sibling PAP-606), agent visuals (PAP-146), follow mode (PAP-149), typing indicators (PAP-611).

**Spec**

* Privacy matrix: customers see staff, assigned agents and members of their own organisation; staff see the tenant; anonymous guests (PAP-589) see nobody and appear as 'Guest' to staff; enforced on the server, never only in the client.
* Hocuspocus awareness broadcasts to every connection in a room, so filtering needs either the extension (`onAwarenessUpdate` hook rewriting the update per connection using `context.principal`) or partitioned rooms; this issue benchmarks both on 200 connections and picks one; the choice is an ADR note.
* Coordinates are relative to the nearest `[data-presence-surface]`; payload validated on send and on receive (invalid remote state ignored and counted).
* Same principal in several windows: PAP-145's window bus elects one publisher; the provider exposes `windowCount` for the `x2` badge.
* Disconnect: peer dims after 5 s and is removed after 30 s (awareness timeout); reconnect restores state without a flash.
* Presence never carries emails, only display names from PAP-55.

**Interface contract**

Provides: `PresenceProvider`, `PresenceState` schema (extended by PAP-146 with `agent?` and PAP-149 with `FollowState`), hooks above, `presenceColor(principalId)`, attribute `data-presence-surface`, server filtering extension or room partition rule, spec flag.

Consumes: Ephemeral rooms and awareness (PAP-140), `can('presence.view')` (PAP-227, soft: allow-all in dev), display names (PAP-55), page flag (PAP-114), window bus (PAP-145, soft), tokens for colours (PAP-66). Consumed by the sibling, PAP-146, PAP-149, PAP-165, PAP-132, PAP-142, PAP-411, PAP-481.

**Definition of done**

* Two browsers on one page see each other's state within 1 s and cursor movement under 100 ms on localhost (Playwright).
* Privacy: customer context never receives another customer's state; staff sees both; guest sees nobody (integration through `callAs` contexts against the compose collab server).
* Benchmark of filtering versus partitioning at 200 connections committed with the decision; `docs/platform/realtime/presence.md` with the payload schema and flag; changelog; Linear comment.

**Test plan**

* Unit: payload validation, colour hashing stability across 1,000 ids, idle transitions with fake timers, dedupe across windows, privacy matrix decision table.
* E2E: two contexts at 375, 1024 and 1920: join, move, idle, disconnect; customer versus staff visibility.

**Demo**

Open the records page in two browsers with different users and watch the raw presence list update in the dev overlay; sign the second in as a customer and see the staff entry but not another customer. Under two minutes.

**Edge cases**

* 50 viewers: hooks return all; the sibling truncates the display.
* Reduced motion: no effect on the data path.
* Route with `realtime.presence: false`: provider mounts nothing; hooks return empty arrays.

**Dependencies**

Blocked by PAP-140 (hard). Soft: PAP-227, PAP-55, PAP-114, PAP-145, PAP-66. Blocks PAP-146, PAP-149, PAP-481 and the sibling PAP-606.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Security Auditor for the privacy path; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/identity/resource-grants` = PAP-589, `r4/realtime/ephemeral-signals` = PAP-611, `r4/realtime/presence-components` = PAP-606.
