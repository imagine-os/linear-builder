---
identifier: "PAP-409"
title: "Portal referral page, console program and referral grids and the rewards approval queue"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: "PAP-196"
children: []
blockedBy: ["PAP-408"]
blocks: []
key: "growth/referral/portal-console-ui"
url: "https://linear.app/paperos/issue/PAP-409/portal-referral-page-console-program-and-referral-grids-and-the"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:52.000Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-409: Portal referral page, console program and referral grids and the rewards approval queue

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Give customers a place to share and track, and staff a queue to approve, on top of the referral data model.

**Scope**

In: `_portal/referrals` (code, link, share buttons, status list, rewards, Connect CTA); console programs page, referrals grid, approval queue. Deferred with the parent.

**Spec**

* Portal page uses PAP-64 shell and tenant branding; console grids are PAP-165 views; approval queue shows fraud flags with reasons.

**Interface contract**

Provides: routes above. Consumes: both siblings, PAP-64, PAP-165, PAP-181 onboarding link.

**Definition of done**

* Playwright share flow and approval; screenshots at seven widths in light and dark; permission tests (customers see only their own).

**Test plan**

* E2E: portal share and status; staff approve; customer denied on `/referrals/admin`.

**Demo**

Copy the code from the portal, then approve a reward in the console queue.

**Edge cases**

* Program paused shows a notice on the portal page.

**Dependencies**

Both siblings (hard), PAP-64, PAP-165.

**Agent**

Builder: Beacon. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session, deferred.
