---
identifier: "PAP-807"
title: "Support SLA policies and business hours: first-response and resolution targets per priority, business-hour calendars, breach warnings and escalation to a manager or Linear"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-136", "PAP-412", "PAP-725"]
blocks: []
key: "r4/growth/support-sla-and-business-hours"
url: "https://linear.app/paperos/issue/PAP-807/support-sla-policies-and-business-hours-first-response-and-resolution"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:09.856Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-807: Support SLA policies and business hours: first-response and resolution targets per priority, business-hour calendars, breach warnings and escalation to a manager or Linear

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-197 stores `sla jsonb` and leaves policies out. Targets per priority with business hours, warnings before breach and an escalation path make the inbox measurable and are what a clinic or agency promises its clients.

**Scope**

In: `support_sla_policy (name, applies: FilterTree over conversation fields, targets { first_response_min, resolution_min } per priority, business_hours_id)`, `support_business_hours (timezone, weekly rules, holidays[])`; computation of `first_response_due_at` and `resolution_due_at` in business time, paused while `pending` on the customer; warnings at 75 percent via PAP-136 to the assignee, breach to the manager; optional escalation action creating a Linear issue through PAP-131's escalation path; SLA badges in the PAP-412 list and conversation header; metrics (attainment percent) added to `support.metrics`.

Out: contractual SLA reporting to customers, multi-level escalation trees.

**Spec**

* Due times are pure functions of policy, business hours and status history; fixtures cover weekends, holidays and DST.
* Policy matching picks the most specific policy (most clauses) then the newest; changes apply to open conversations prospectively.
* Badges use the PAP-71 status chip with `on_track|warning|breached`.

**Interface contract**

Provides: `support.sla.*`, `support.businessHours.*`, due-time computation, badges, notification kinds `support.sla.warning|breached`, metrics extension. Consumes: inbox and conversation view (PAP-412), notifications (PAP-136), Linear escalation (PAP-131), filter builder (PAP-166), status chip (PAP-71).

**Definition of done**

* Due-time fixtures green; warning and breach fire once each in a test clock run; Playwright badges; screenshots at 375, 1024, 1920 light and dark.
* `docs/growth/support.md` gains an SLA section; CHANGELOG.

**Test plan**

* Unit: business-hour arithmetic, pause on pending, policy specificity, once-only alerts.
* E2E: set a 1-hour first-response target, open a fixture conversation, advance the clock 45 minutes to see the warning, then past to see the breach and the manager alert.

**Demo**

Reviewer creates a policy, opens the inbox sorted by due time and advances the clock to watch a badge turn to breached. Under two minutes.

**Edge cases**

* Holiday added retroactively: open conversations recomputed; closed ones untouched.
* Conversation reopened after resolution: resolution timer restarts from the reopen.

**Dependencies**

Hard: PAP-412, PAP-136. Soft: PAP-131, PAP-166, PAP-71.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Edge Case Hunter for calendars).

**Size**

S: half a session.
