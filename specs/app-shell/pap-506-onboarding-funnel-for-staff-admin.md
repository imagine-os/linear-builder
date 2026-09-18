---
identifier: "PAP-506"
title: "Onboarding funnel for staff: `/admin/onboarding` tenants by step reached, drop-off counts, resume nudges through the notification centre and the `onboarding.funnel` query"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-33", "PAP-38", "PAP-58", "PAP-367", "PAP-579"]
blocks: []
key: "r4/app-shell/onboarding-funnel-admin"
url: "https://linear.app/paperos/issue/PAP-506/onboarding-funnel-for-staff-adminonboarding-tenants-by-step-reached"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-506: Onboarding funnel for staff: `/admin/onboarding` tenants by step reached, drop-off counts, resume nudges through the notification centre and the `onboarding.funnel` query

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-367 builds the customer-facing wizard; the staff view that shows where tenants stall is separable and feeds growth analytics (PAP-194). Splitting it keeps the wizard session focused on the five steps and the resume logic.

**Scope**

In:

* Spec `specs/pages/staff/admin-onboarding.spec.yaml` (`access: [staff.owner, agent.atlas]`), route `/admin/onboarding` in the staff console (PAP-63).
* Procedure `onboarding.funnel` aggregating `tenant.settings.onboarding` into `{ step, count, medianMinutes, stalledOver24h }` per step, plus `onboarding.nudge(tenantId)` posting a `onboarding.stalled` notification (PAP-136 kind) to the tenant owner.
* UI: funnel bars per step (PAP-71 data display), stalled list with last activity from PAP-38 audit, nudge button with rate limit (one per tenant per day).
* Event `onboarding.step.completed` published from the wizard procedures so PAP-194 can attribute.

Out: the wizard itself (PAP-367), acquisition analytics (PAP-194), email copy beyond the notification kind.

**Spec**

* Funnel excludes demo tenants (`attributes.demo`, PAP-363).
* Nudge writes an audit event with actor and reason; customers never see this page (`DeniedState`).
* Query under 200 ms for 10k tenants (index on `(settings->>'onboardingStep')` or a materialised column).

**Interface contract**

Provides: route `/admin/onboarding`, `onboarding.funnel`, `onboarding.nudge`, topic `onboarding.step.completed`; consumed by PAP-194, PAP-136 (kind), Atlas digests.

Consumes: staff console shell (PAP-63), audit log (PAP-38), notification kinds (PAP-136, soft), the wizard state shape (PAP-367).

**Definition of done**

* Seeded tenants at mixed steps render the funnel; nudge sends one notification and refuses a second within a day.
* Screenshots at 375, 1024, 1920; a11y clean; CHANGELOG; Linear comment.

**Test plan**

* Unit: funnel aggregation over fixture tenants; nudge rate limit.
* E2E: staff opens the page, nudges a stalled tenant, customer principal is denied.

**Demo**

Reviewer opens `/admin/onboarding`, sees three tenants stalled at "connect billing", clicks Nudge and the owner of one receives an in-app notification. Under a minute.

**Edge cases**

* Tenant deleted mid-onboarding (PAP-432 lifecycle): excluded from the funnel.
* Step order changes in a later template: funnel keys on step id, not index.

**Dependencies**

Hard: PAP-16, PAP-38. Sibling: PAP-367 wizard procedures. Soft: PAP-63 (the route moves into the staff console shell when it lands; a plain `_app/admin` layout until then), PAP-136, PAP-194, PAP-432.

**Agent**

Builder: Forge with Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-367 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-367 blocks this issue (`blocks` relation).
