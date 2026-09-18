---
identifier: "PAP-611"
title: "Ephemeral signals over awareness: typing indicators for comments and chat, cursor chat bubbles and emoji reaction bursts with throttling, privacy rules and reduced-motion behaviour"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-605"]
blocks: []
key: "r4/realtime/ephemeral-signals"
url: "https://linear.app/paperos/issue/PAP-611/ephemeral-signals-over-awareness-typing-indicators-for-comments-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:16.640Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-611: Ephemeral signals over awareness: typing indicators for comments and chat, cursor chat bubbles and emoji reaction bursts with throttling, privacy rules and reduced-motion behaviour

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Build S

**Goal**

The small signals that make multiplayer feel alive and that Figma, Slack and Google Docs all ship: 'Ada is typing' under a comment box, a short message attached to a cursor, and a burst of emoji over a canvas or record. They ride on the presence payload, cost nothing on the server, and are needed by the support chat (PAP-411) and comments (PAP-318) before they invent their own.

**Scope**

In: `PresenceState.signals?: { typing?: { anchorKey, until }, cursorChat?: { text, until }, reactions?: [{ emoji, x, y, surfaceId, at }] }` extension in `packages/collab/src/presence/signals.ts`; hooks `useTyping(anchorKey)`, `useCursorChat()`, `useReactions(surfaceId)`; components `TypingIndicator`, `CursorChatBubble` (attached to `LiveCursor`), `ReactionBurst`; command `presence.react` and the `/` shortcut for cursor chat (PAP-151, soft); throttles: typing at most one update per 2 s with a 5 s expiry, cursor chat 300 ms, reactions 5 per 10 s per principal; privacy inherits the presence matrix (PAP-605); reduced motion replaces bursts with a static badge; docs section.

Out: Persistent reactions on comments (PAP-131 `comments.react`), chat messages (PAP-411), notification of typing.

**Spec**

* Typing is keyed by `anchorKey` (PAP-131 grammar) so the indicator appears under the right thread or chat; expires client-side even if the peer disconnects.
* Cursor chat text is capped at 80 characters, sanitised as plain text, shown for 5 s after the last keystroke; never stored.
* Reactions render at surface-relative coordinates with a 1.2 s animation; bursts from many peers stack with a count; screen readers get one polite announcement per burst.
* Customers see staff typing but not other customers' signals, per the presence matrix; agents (PAP-146) may set `typing` from the presence client.

**Interface contract**

Provides: Signals schema extension, hooks and components above, command `presence.react`.

Consumes: Presence data path and privacy (PAP-605), `LiveCursor` (PAP-606), anchor grammar (PAP-131, soft), command registry (PAP-151, soft), reduced motion (PAP-72, soft). Consumed by PAP-318, PAP-411, PAP-146, PAP-321.

**Definition of done**

* Typing under a comment box appears in the other browser within 1 s and expires after 5 s of silence; cursor chat shows on the peer's cursor; reactions burst on a canvas surface (Playwright, two contexts).
* Throttles proven with fake timers; customer never sees another customer's signals; reduced-motion story static; docs; changelog.

**Test plan**

* Unit: throttle and expiry timers, text cap and sanitisation, reaction rate limit, announcement throttling.
* E2E: two contexts on a comment thread and a canvas; privacy check with a customer context.

**Demo**

Type in a comment box and watch 'Ada is typing' in the other window, press `/` and type a cursor message, then press the reaction shortcut over a record. Under a minute.

**Edge cases**

* Peer crashes mid-typing: indicator expires by timer.
* Fifty peers reacting at once: bursts coalesce into counts.
* Touch devices: cursor chat unavailable; reactions via a long-press menu (PAP-154, soft).

**Dependencies**

Blocked by PAP-605 (hard). Soft: PAP-606, PAP-131, PAP-151, PAP-72, PAP-154. Consumed by PAP-318, PAP-411, PAP-146.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/realtime/presence-components` = PAP-606, `r4/realtime/presence-core` = PAP-605.
