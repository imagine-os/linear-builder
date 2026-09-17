---
identifier: "PAP-141"
title: "Build the presence layer: cursors, avatars, selections and 'who is viewing' across pages"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-140"]
blocks: ["PAP-146", "PAP-149"]
key: "realtime/presence"
url: "https://linear.app/paperos/issue/PAP-141/build-the-presence-layer-cursors-avatars-selections-and-who-is-viewing"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:30.425Z"
---

# PAP-141: Build the presence layer: cursors, avatars, selections and 'who is viewing' across pages

**Goal**

Make every PaperOS page show who is here: live cursors, selection highlights, avatar stacks and a who-is-viewing indicator on any page, not only inside editors. Presence rides on Hocuspocus awareness and is the foundation for agent presence (PAP-146) and follow mode (PAP-149).

**Scope**

In:

* `packages/collab/src/presence/`: `PresenceProvider` joining `page:<tenantId>:<routeId>` (ephemeral room from PAP-140) and optional entity rooms; hooks `usePresence()`, `useMyPresence()`, `useViewers(entityId)`.
* Awareness payload (Zod): `{ principalId, principalType: 'human'|'agent', name, avatarUrl?, color, cursor?: { x, y, surfaceId }, selection?: { entityId, fieldId? } | { from, to }, viewport?, focusedRoute, lastActive, idle }`.
* Components in `packages/ui` on PAP-71 `AvatarStack`: `PresenceAvatars` (5 plus overflow), `LiveCursor` (fades after 4 s, hidden on touch), `SelectionHighlight`, `ViewersBadge`.
* Colours: 12 accessible tokens from PAP-66 chosen by hashing `principalId`; idle after 60 s or hidden tab.

Out: agent visuals (PAP-146), follow mode, chat, history.

**Spec**

* Cursor throttled to 50 ms; selection and route immediate; coordinates relative to the nearest `[data-presence-surface]`.
* Privacy: `presence.view` policy (PAP-59): customers see staff, assigned agents and members of their own organisation; staff see the tenant.
* Page spec flag `realtime.presence: true|false` (PAP-114), default true for staff surfaces, false for customer surfaces.
* Same principal in several windows appears once with an `x2` badge (PAP-145 aggregates).
* Accessibility: stack `aria-label`, cursors `aria-hidden`, live region announces joins at most once per 10 s.

**Interface contract**

Exposes: `PresenceState` type and Zod schema in `packages/collab/presence/schema.ts` (extended by PAP-146 with `agent?`), `PresenceProvider`, hooks above, components above, `presenceColor(principalId)`, DOM attribute `data-presence-surface=“<id>”` that PAP-149 and PAP-142 reuse for coordinates, awareness message kinds `presence.request` reserved for PAP-149. Consumes: `createDocProvider(..., { ephemeral: true })` and awareness from PAP-140, `AvatarStack` and `Badge` (PAP-71), palette tokens (PAP-66), `can('presence.view')` (PAP-59), display names from PAP-55, page flag from PAP-114.

**Definition of done**

* Two browsers on one page show each other's avatar within 1 s and cursor movement under 100 ms on localhost.
* Storybook stories for four components in light, dark and high contrast; axe clean.
* `docs/platform/realtime/presence.md` with payload schema and page flag; changelog; Linear comment with Storybook and staging links.

**Test plan**

* Vitest: payload validation, colour hashing stability across 1,000 ids, idle transitions with fake timers, dedupe of one principal across windows, 50-viewer overflow text.
* Integration: `can('presence.view')` matrix through `callAs` for customer, staff and agent contexts; customer never receives another customer's state (server filters awareness by policy).
* Playwright, two contexts: avatars and selection highlights render at 375, 1024 and 1920; cursor latency measured with `performance.now()` stamps under 100 ms; disconnect dims after 5 s and removes after 30 s.
* Visual: Storybook stories captured by Gate 3 in three themes; reduced-motion story has no animation.

**Demo**

Open the records page in two browsers with different users, move the mouse in one and watch the labelled cursor in the other; select a row and see the coloured outline; hover the avatar stack to read the names. Under two minutes.

**Edge cases**

* 50 viewers: 5 avatars plus `+45`, tooltip lists 20.
* Scrolled container: surface-relative coordinates.
* Long names truncate at 24 characters.
* Reduced motion: no animation or pulse.

**Dependencies**

PAP-140 (hard, encoded). Soft: PAP-71, PAP-66, PAP-59, PAP-55, PAP-114. Blocks PAP-146, PAP-149; consumed by PAP-165, PAP-132, PAP-142.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Iris (Component Crafter) for components; Sentinel (Visual Inspector) across the matrix.

**Size**

M: several components plus permission-aware presence semantics.
