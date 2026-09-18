---
identifier: "PAP-874"
title: "Build the feedback and feature request board: public and portal board, upvotes, statuses synced to PM entities, duplicates merge, changelog linkage and notifications on status change"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Memberships, loyalty, announcements and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-100", "PAP-131", "PAP-133", "PAP-136", "PAP-319", "PAP-725"]
blocks: []
key: "r4/engagement/feedback-board"
url: "https://linear.app/paperos/issue/PAP-874/build-the-feedback-and-feature-request-board-public-and-portal-board"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-874: Build the feedback and feature request board: public and portal board, upvotes, statuses synced to PM entities, duplicates merge, changelog linkage and notifications on status change

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Close the loop with users: a feedback board where customers post ideas and problems, upvote and comment, staff triage, merge duplicates and link posts to PM issues (PAP-100) whose status flows back, and shipped items link to the changelog entry (PAP-133) with a notification to everyone who voted.

**Scope**

In: `feedback_post` (title, body, author contact or anonymous email, status open|planned|in_progress|shipped|declined, votes, category, linked pm_issue, merged_into), `feedback_vote`; comments via PAP-131 anchors; public `/feedback` and portal `/portal/feedback` (spec) on the list view with sort by votes and recency; anti-spam via `CaptchaPort` and rate limits. Staff triage view: merge, categorise, link or create a PM issue (PAP-100 entities; Linear sync PAP-101 carries it), set status; status changes notify voters (`feedback.status_changed` kind) with digest batching (PAP-324). Changelog linkage: when a linked issue ships and PAP-133 publishes the entry, the post moves to `shipped` with the entry link.

Out: Roadmap page beyond a status-grouped board view. Internal-only idea management (use PM).

**Spec**

* Anonymous posts require email verification (one-time link) before appearing; verified authors can edit for 15 minutes
* Votes are one per principal or verified email; merging moves votes without duplicates and redirects the old URL
* Board visibility is per tenant setting: public, portal-only or off; RLS predicate matches

**Interface contract**

Provides: `FeedbackPort.post|vote|link`, tables, board pages, triage view, `feedback.posted|voted|status_changed` events. Consumes: PM entities and sync (PAP-100, PAP-101), comments (PAP-131), changelog (PAP-133), notifications and digests (PAP-136, PAP-324), list view (PAP-169), `CaptchaPort` (PAP-855, soft). Consumed by: pm-linear (feedback-derived issues), growth (feedback as segment attribute), assistant (summaries of top requests).

**Definition of done**

* Demo board with 20 posts; a customer posts and votes on a phone; staff merges two, links one to a PM issue, ships it via changelog and voters are notified
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: vote uniqueness and merge; status flow from PM; visibility predicate.
* E2E: anonymous post with verification; triage actions; digest of status changes.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Post "Add Apple Pay" on the demo portal board, upvote from another account, link it to a PM issue in the console, mark shipped through a changelog entry and show the notification.

**Edge cases**

* Linked PM issue deleted in Linear: the post keeps its status and shows the link as broken for staff to fix
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-100, PAP-131, PAP-133, PAP-136 (hard), PAP-101, PAP-324, PAP-169 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/workflows/forms-publishing` = PAP-855.
