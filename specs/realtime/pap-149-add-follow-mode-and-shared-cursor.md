---
identifier: "PAP-149"
title: "Add follow mode and shared cursor sessions for support and pair review"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-141", "PAP-475", "PAP-605", "PAP-606"]
blocks: []
key: "realtime/followmode"
url: "https://linear.app/paperos/issue/PAP-149/add-follow-mode-and-shared-cursor-sessions-for-support-and-pair-review"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:38.824Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-149: Add follow mode and shared cursor sessions for support and pair review

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Let a support agent or reviewer guide someone live: follow a person so your view mirrors their navigation, scroll and selection, or start a shared cursor session where both see each other's pointer and a highlighted element. Replaces screen sharing for support and pair review, for humans and agents.

**Scope**

In:

* `packages/collab/src/follow/`: `useFollow(targetPrincipalId)` and leader broadcasting `{ route, params, scroll: { surfaceId, x, y }, selection, zoom, highlightedElement }` over the PAP-141 awareness room.
* Consent: staff follow customers only after acceptance or during an active support session (PAP-197); staff and agents follow each other freely; customers follow staff in a shared session.
* Shared cursor session: bidirectional cursors, "point" ping (modifier click), persistent highlight ring on any `[data-spec-component]`.
* UI: `FollowBar`, leader banner, request dialog; entry points in the presence popover and the support inbox.
* `follow_sessions(id, tenant_id, leader, follower, started_at, ended_at, reason, consented_at)` written to PAP-38.

Out: audio and video, remote control, recording.

**Spec**

* Leader emits at most 10 updates/s; scroll relative to `[data-presence-surface]`; follower scrolls the matching surface and shows an "out of view" arrow.
* Navigation via TanStack Router `navigate`; no permission → "Ada is on a page you cannot view".
* Follower interaction pauses following for 10 s, then "Resume".
* Requests are awareness messages `presence.request` with a 60 s timeout.
* View-only; acting for the customer requires PAP-61 impersonation.
* Commands `follow.start|stop|ping` (PAP-151); all state changes announced.

**Interface contract**

Exposes: `FollowState` Zod schema added to `PresenceState`, awareness messages `presence.request`, `presence.accept`, `presence.decline`, `presence.ping`, hooks `useFollow()`, `useLeaderState()`, components `FollowBar`, `FollowRequestDialog`, `LeaderBanner`, table `follow_sessions`, oRPC `follow.canFollow(target) -> { allowed, reason }`, commands above; `startFollow(principalId)` entry point used by PAP-197. Consumes: awareness and `data-presence-surface` (PAP-141), `can('presence.follow')` policies and impersonation boundary (PAP-59, PAP-61), `audit_event` writer (PAP-38), router `navigate` (PAP-16), `defineCommand` (PAP-151), window aggregation (PAP-145), `data-spec-component` attributes (PAP-120).

**Definition of done**

* Screenshots at 375 (customer, mobile) and 1440 (staff); Storybook stories for the three components in three themes.
* Audit entries verified for start and end; `docs/platform/realtime/follow-mode.md` with a support runbook; changelog; Linear comment with a 30-second video.

**Test plan**

* Vitest: consent matrix (staff→customer without consent denied, with active support session allowed, agent→customer denied, customer→staff in session allowed), 10 updates/s throttle, 60 s request timeout, 10 s pause and resume.
* Integration: `follow.canFollow` through `callAs` for each audience pair; audit rows written on start and end.
* Playwright, two contexts: staff requests, customer accepts, navigation and scroll mirror within 300 ms, follower scrolls and pauses, resumes, ends; leader navigates to a page the follower cannot view and the bar shows the notice; run at 375 and 1440.
* Visual: Gate 3 captures of the three components in three themes.

**Demo**

As staff, open a customer's presence avatar, click “Follow”, have the customer accept; navigate and scroll in the customer window and watch the staff window mirror it; press the ping modifier-click to ripple a button on both; stop. Under two minutes.

**Edge cases**

* Leader offline: "Ada disconnected", session ends after 30 s.
* Leader opens a modal: mirrored via highlighted element id.
* Phone following a 1920 desktop: horizontal clamp, ring still targets the element.
* Two staff follow one customer: banner lists both.
* External URL: following pauses with a notice.

**Dependencies**

PAP-141 (hard, encoded). Soft: PAP-59, PAP-61, PAP-38, PAP-151, PAP-16, PAP-145, PAP-197.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Security Auditor for consent, Visual Inspector).

**Size**

M: consent rules and mirroring across layouts add subtlety.
