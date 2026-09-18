---
identifier: "PAP-319"
title: "Live updates, deep links and Linear escalation"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-131"
children: []
blockedBy: ["PAP-318"]
blocks: ["PAP-136", "PAP-137", "PAP-197", "PAP-323", "PAP-411", "PAP-725", "PAP-736", "PAP-840", "PAP-874"]
key: "collab/comments/live-deeplinks-linear"
url: "https://linear.app/paperos/issue/PAP-319/live-updates-deep-links-and-linear-escalation"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:24.025Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-319: Live updates, deep links and Linear escalation

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Finish comments (PAP-131): threads refresh live for everyone on the same anchor, `?thread=` links open and scroll to a thread, and one click turns a thread into a Linear issue with a back-link.

**Scope**

In:

* Live: Electric shape on `comment_thread` and `comment` scoped by tenant and anchor prefix through PAP-143's `subscribeShape`; fallback TanStack Query polling every 5 s when shapes are unavailable; typing indicator via awareness room `thread:<id>` (PAP-141).
* Deep link `?thread=<id>`: opens the panel, scrolls the anchor into view, shows "element moved" when the anchor is missing.
* Escalation: `comments.threads.createIssue({ threadId, label: Bug|Improvement })` calling PAP-101's client (or the Linear SDK directly until it lands) with title from the first comment, description containing the deep link, stores `linear_issue_id`; thread shows the issue state.

Out: notifications (PAP-136 work package 1), screenshot crops (PAP-137).

**Spec**

* Shape `where`: `tenant_id = $1 and anchor_key like $2`; unsubscribe 30 s after the panel closes.
* Issue title capped at 120 characters; description template in `packages/collab/comments/escalate.md`.
* Deep link resolution happens after data load; scroll uses `scrollIntoView({ block: 'center' })`.

**Interface contract**

Exposes `threads.createIssue` procedure, `useThreadLink(threadId)`, deep-link param `thread`, `LinearIssueBadge`. Consumes `subscribeShape` and `useLiveQuery` (PAP-143, PAP-271), awareness (PAP-141), Linear client `createIssue({ title, description, labels, project })` (PAP-101) with SDK fallback, siblings' procedures and components.

**Definition of done**

* Two contexts see each other's comments within 1 s; deep link opens the right thread; test issue created in Linear (mocked in CI, one real in staging) and linked back.
* Linear comment with the created test issue link.

**Test plan**

* Vitest: deep-link parser, issue title and description builders, fallback selection when shapes are unavailable.
* Integration: shape subscription filters by anchor prefix (Electric container); polling fallback activates when the proxy returns 503.
* Playwright, two contexts: A posts, B sees within 1 s; open `?thread=<id>` in a fresh tab and assert scroll and panel; create issue against a mocked Linear endpoint and assert the badge.

**Demo**

Post a comment in one browser and watch it appear in another; copy the thread link, open it in a private window after signing in and land on the thread; click Create issue and open the Linear link. Under two minutes.

**Edge cases**

* Linear API down: `createIssue` fails with a retry toast; nothing stored.
* Thread deleted while a deep link is open: "no longer available".
* Shape invalidated by a permission change: resubscribe (PAP-143).

**Dependencies**

Siblings 1 and 2 (hard). PAP-143, PAP-141, PAP-101 (soft with fallbacks).

**Agent**

Built by Nova (CRDT Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

S: wiring over existing pieces.
