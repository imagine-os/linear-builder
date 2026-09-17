---
key: "growth/social/model-queue-calendar"
title: "Social schema, approval state machine, composer with per-platform variants, approval queue and calendar"
project: "growth"
parent: "PAP-190"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: []
milestone: "Campaigns and social"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent4/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012"
status: "pending"
---

# Social schema, approval state machine, composer with per-platform variants, approval queue and calendar

**Goal**

Model posts and accounts, enforce the approval state machine, and give staff the composer, queue and calendar they plan from, before any adapter exists.

**Scope**

In: `social/schema.ts`, `social.posts.*`, `social.accounts.list` (connect in sibling), composer with variant tabs and live limit counters, approval queue with diff of edits, calendar view bound to `social_post` (list fallback). Out: adapters, worker, OAuth (siblings).

**Spec**

* Tables per the parent; transitions the only writes to `status`; approval stores `approved_hash`; edits after approval return to `pending_approval`.
* Composer previews platform-faithful cards from `packages/ui`; media via PAP-37; limits from `validatePost` (mock adapter limits until siblings land).
* `social.approve` for owner and admin only; agents create `pending_approval`.
* `scheduled_at` UTC, displayed in tenant timezone.

**Interface contract**

Provides: schema, `social.posts.*`, `SocialPostStatus` machine, composer, queue, calendar route, `drafted_by` slot for PAP-192. Consumes: PAP-187, PAP-37, PAP-168 (soft), PAP-38.

**Definition of done**

* State machine tests; Playwright draft, submit, approve, edit-returns-to-pending; screenshots at seven widths in light and dark; axe clean.

**Test plan**

* Unit: transitions, hash binding, permission checks.
* E2E: the flow above; calendar and list fallback at 375 px.

**Demo**

Write a post with two variants, submit it, approve as admin, see it on the calendar.

**Edge cases**

* Past `scheduled_at` on approval asks to publish now; media over limits blocks scheduling.

**Dependencies**

PAP-187, PAP-37 (hard), PAP-168 (soft). Blocks siblings.

**Agent**

Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
