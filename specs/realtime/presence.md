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
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-141: Build the presence layer: cursors, avatars, selections and 'who is viewing' across pages

**Goal**

Make every PaperOS page show who is here: live cursors, selection highlights, avatar stacks and a "who is viewing" indicator that works on any page, not only inside editors. Presence rides on Hocuspocus awareness so it needs no extra infrastructure, and it is the foundation for agent presence and follow mode.

**Scope**

In:
- `packages/collab/src/presence/` with a `PresenceProvider` (React context) that joins an awareness room per page (`page:<tenantId>:<routeId>`) and optional per-entity rooms.
- Awareness payload schema (Zod): `{ principalId, principalType: 'human'|'agent', name, avatarUrl?, color, cursor?: { x, y, elementId? }, selection?: { entityId, fieldId? } | { from, to }, viewport?, focusedRoute, lastActive, idle: boolean }`.
- Components in `packages/ui` (built on `design-system/data-display` AvatarStack): `PresenceAvatars` (max 5 + overflow count, tooltip with names), `LiveCursor` (name label, fades after 4 s idle, hidden on touch devices), `SelectionHighlight` (outline colour per user around a row, cell or block), `ViewersBadge` ("3 viewing" pill for list items).
- Colour assignment: deterministic palette of 12 accessible colours from `design-system/tokens` chosen by hashing `principalId`.
- Hooks: `usePresence()` (others), `useMyPresence()` (set cursor/selection), `useViewers(entityId)`.
- Idle detection after 60 s without input; tab hidden marks `idle: true`; leaving the route removes the state.

Out: agent-specific visuals (`realtime/agent-presence`), follow mode, chat, presence history.

**Spec**

- Awareness updates throttled to 50 ms for cursor, immediate for selection and route changes; cursor coordinates are relative to the nearest `[data-presence-surface]` element so they survive resizes and different window sizes.
- Presence rooms authenticate through the same provider as `realtime/yjs-server`; the room stores no persistent document (server flag `ephemeral: true` skips persistence).
- Privacy: customers see only staff and agents assigned to them plus other members of their own organisation, decided by `packages/permissions` action `presence.view`; staff see everyone in the tenant. Names shown are display names from `identity/audience-model`.
- Per-page opt-in via page spec field `realtime.presence: true|false` (default true for staff surfaces, false for customer surfaces) read from `spec-builder/schema`.
- Accessibility: avatar stack has `aria-label="3 people viewing: Ada, Bo, Forge (agent)"`; cursors are `aria-hidden`; a visually hidden live region announces joins and leaves at most once per 10 s.
- Multi-window: the same user in two windows appears once (dedupe by `principalId`, show a small "x2" badge).
- Storybook stories for all four components in light, dark and high-contrast themes, with a mocked awareness source.

**Definition of done**

- Two browsers on the same page show each other's avatar within 1 s and cursor movement under 100 ms on localhost.
- Vitest tests for payload validation, colour hashing stability, idle transitions and dedupe.
- Playwright test with two contexts asserting avatars and selection highlights render at 375, 1024 and 1920 px; screenshots attached.
- Storybook stories published; axe passes on each.
- Permission test: customer context cannot see another customer's presence.
- Docs page `docs/platform/realtime/presence.md` with the payload schema and page-spec flag.
- Changelog entry and Linear comment with a demo link (GitHub Pages Storybook and staging URL).

**Edge cases**

- 50+ viewers on one page: stack shows 5 avatars + "+45" and the tooltip lists the first 20 with "and 25 more".
- Cursor over a scrolled container: coordinates are surface-relative, so scrolling in one window does not move cursors in another.
- User loses connection: their avatar dims after 5 s and disappears after 30 s (awareness timeout).
- Very long display names truncate to 24 characters with full name in the tooltip.
- Reduced motion: cursor movement is not animated; joins do not pulse.
- Same principal in three windows and a tab that is hidden: counts as one active viewer if any window is active.

**Dependencies**

- `realtime/yjs-server` (awareness transport), `design-system/data-display` (AvatarStack, Badge), `design-system/tokens` (palette), `identity/rbac-abac` (`presence.view`), `spec-builder/schema` (page flag, optional at first). Consumed by `realtime/agent-presence`, `realtime/followmode`, `tables/grid-view`, `collab/canvas-view`.

**Agent**

Builder: Nova (CRDT Engineer sub-agent). Reviewer: Iris (Component Crafter) for the components; Sentinel (Visual Inspector) for screenshots across the matrix.

**Size**

M: several components plus permission-aware presence semantics.
