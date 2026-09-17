---
identifier: "PAP-149"
title: "Add follow mode and shared cursor sessions for support and pair review"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Scale and offline tested"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-141"]
blocks: []
key: "realtime/followmode"
url: "https://linear.app/paperos/issue/PAP-149/add-follow-mode-and-shared-cursor-sessions-for-support-and-pair-review"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-149: Add follow mode and shared cursor sessions for support and pair review

**Goal**

Let a support agent or reviewer guide someone through the app live: click a person in presence and "follow" them so your view mirrors their navigation, scroll position and selection, or start a shared cursor session where both parties see each other's pointer and a highlighted element. This replaces screen-sharing for support and pair review, and it works between humans and agents.

**Scope**

In:
- `packages/collab/src/follow/`: `useFollow(targetPrincipalId)` (follower) and leader broadcasting of `{ route, params, scroll: { surfaceId, x, y }, selection, viewport zoom, highlightedElement }` through the presence awareness room from `realtime/presence`.
- Consent model: staff can follow customers only after the customer accepts a request ("Ada from support wants to view along with you") or when an active support session exists; staff and agents can follow each other freely; customers can follow staff during a shared session.
- Shared cursor session: bidirectional cursors with name labels, "point" ping (click with modifier) that ripples an element for both, and a persistent highlight ring on any `[data-spec-component]` element.
- UI: `FollowBar` pinned at top ("Following Ada · Stop"), leader banner ("Bo is following you · End"), request dialog, and entry points in the presence avatar popover and the support inbox (`growth/support-inbox`).
- Session record `follow_sessions(id, tenant_id, leader, follower, started_at, ended_at, reason)` written to `data-layer/audit-log`.

Out: audio/video, remote control (follower cannot act as the leader), recording replays (`quality/video-replays` covers tests, not support).

**Spec**

- Leader emits at most 10 updates/s; scroll positions are relative to `[data-presence-surface]` ids so different window sizes still align; the follower scrolls the matching surface with `scrollTo` and shows an "out of view" arrow when the leader's highlighted element is off-screen.
- Navigation mirroring uses TanStack Router `navigate` with the leader's route and params; if the follower lacks permission for that route, `FollowBar` shows "Ada is on a page you cannot view" and waits.
- Follower interactions pause following for 10 s (local exploration), then a "Resume following" button appears; explicit Stop ends the session.
- Requests are awareness messages with a 60 s timeout; acceptance is recorded with `consentedAt`; customers can end at any time from the banner.
- Impersonation interplay: following is view-only; acting on behalf of the customer requires `identity/impersonation` and is a separate, audited action.
- Agents as leaders: an agent running a walkthrough (future onboarding character) can lead; agents cannot follow customers.
- Accessibility: all state changes announced via a live region; every control keyboard reachable; commands `follow.start`, `follow.stop`, `follow.ping` in `input/command-registry`.

**Definition of done**

- Playwright test with two contexts: staff requests, customer accepts, navigation and scroll mirror within 300 ms, follower explores and resumes, session ends; screenshots at 375 (customer, mobile) and 1440 px (staff).
- Vitest tests for consent rules per audience and rate limiting.
- Permission test: staff cannot follow a customer without consent or an active support session.
- Audit entries verified for start and end.
- Storybook stories for `FollowBar`, leader banner and request dialog in three themes.
- Docs `docs/platform/realtime/follow-mode.md` including a support runbook.
- Changelog entry and Linear comment with a 30-second demo video.

**Edge cases**

- Leader goes offline: follower sees "Ada disconnected" and the session ends after 30 s.
- Leader opens a modal: follower mirrors modal open state via the highlighted element id, not by replaying clicks.
- Leader in a detached Tauri window (`realtime/multi-window-sync`): the leader's aggregated presence reports the focused window's route.
- Follower on a phone following a 1920 px desktop leader: horizontal positions clamp; highlight ring still targets the same element.
- Two staff follow one customer: both receive updates; the customer banner lists both names.
- Leader navigates to an external URL: following pauses with a notice.

**Dependencies**

- `realtime/presence` (transport and avatars), `identity/rbac-abac` and `identity/impersonation` (consent and boundaries), `data-layer/audit-log`, `input/command-registry`, `app-shell/router-layouts` (navigate API). Optional entry point in `growth/support-inbox`.

**Agent**

Builder: Nova (CRDT Engineer sub-agent). Reviewer: Sentinel (Security Auditor for consent model, Visual Inspector for screenshots).

**Size**

M: consent rules and mirroring across layouts add subtlety to an otherwise small feature.
