---
identifier: "PAP-884"
title: "Build HR core: employee directory and profiles on fin_employee, time-off policies and requests with approvals, shift scheduling on the availability shape, clock-in, timesheets and export to payroll runs"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Orders, POS, purchasing, projects and HR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-59", "PAP-229", "PAP-344", "PAP-399", "PAP-400", "PAP-877", "PAP-883"]
blocks: ["PAP-892"]
key: "r4/commerce/hr-core"
url: "https://linear.app/paperos/issue/PAP-884/build-hr-core-employee-directory-and-profiles-on-fin-employee-time-off"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-884: Build HR core: employee directory and profiles on fin_employee, time-off policies and requests with approvals, shift scheduling on the availability shape, clock-in, timesheets and export to payroll runs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Give every business the staff-facing basics payroll assumes: an employee directory and profile on `fin_employee` (PAP-399) with documents and emergency contacts, time-off policies (accrual, carryover, blackout) with requests approved through the approvals framework, shift scheduling that reuses the engagement availability shape and renders on the calendar (PAP-344), clock-in and out (kiosk or mobile with geofence), timesheets that aggregate entries and shifts, and an export that becomes the PAP-400 payroll run inputs.

**Scope**

In: `HrPort`: `directory` (profiles, roles, managers, documents via PAP-37 with restricted audience `hr`), `timeOff` (policies, balances, requests, approvals via policy key `timeoff.approve`), `shifts` (templates, publish, swap requests, open shifts claim), `timesheets` (weekly, from clock events, time entries and shifts; approve), `toPayroll(period)` producing the hours and earnings inputs PAP-400 consumes. Pages: `/hr/people` (directory grid and profile), `/hr/time-off` (calendar overlay and requests), `/hr/schedule` (week view on PAP-344 with drag, coverage counts, labour cost estimate), `/hr/timesheets`; staff self-service under `/me` (balances, request, my shifts, clock). Clock: kiosk mode (PAP-23) with PIN and photo, mobile with geofence (PAP-260 geolocation) and offline queue (PAP-148); events feed timesheets. Permissions: HR data uses attribute policies (PAP-227): managers see reports, HR sees all, employees see self; salary fields restricted to payroll roles; every access to compensation audited (PAP-38).

Out: Benefits administration, recruiting and onboarding checklists beyond a workflow template (packs may add). Labour-law compliance engines (overtime rules are configurable, not pre-certified).

**Spec**

* Time-off accrual runs monthly as a job with per-policy rules; balances derive from ledger-like entries (accrual, usage, adjustment) and are rebuildable
* Published shifts write `AvailabilityRule(kind blocked|available, source shift)` on the linked scheduling resource so bookings and shifts agree
* Timesheet locks after approval; changes create adjustments visible to payroll; overtime rules (daily and weekly thresholds, multipliers) configurable per tenant and jurisdiction profile (PAP-126)
* `toPayroll` output validates against the PAP-398 adapter contract and is reviewed with the typed-total approval (PAP-400)

**Interface contract**

Provides: `HrPort` default adapter, tables, HR pages and self-service, clock flows, shift → availability bridge, payroll export, `timeoff.*`, `shift.*`, `timesheet.approved` events. Consumes: employee model and payroll run (PAP-399, PAP-400, PAP-398), calendar view (PAP-344), scheduling availability shape (engagement), approvals framework, attribute policies (PAP-227), kiosk and geolocation (PAP-23, PAP-260), offline outbox (PAP-148), audit (PAP-38). Consumed by: PAP-400 (inputs), engagement scheduling (staff availability), projects (utilisation), packs (restaurant, retail, gym, construction).

**Definition of done**

* Restaurant demo: 12 employees, a two-week published schedule, two time-off requests approved, clock events from the kiosk, timesheets approved with overtime, export validated against the payroll adapter fixture; salary access audited
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: accrual rules; overtime computation across week boundaries and DST; shift-to-availability bridge; geofence check.
* Integration: approval flow; timesheet lock and adjustments; export validation against PAP-398 schema.
* E2E: schedule drag on the calendar; self-service request on a phone; kiosk clock with PIN.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Publish next week's schedule for the restaurant, approve a vacation that opens a shift, let another employee claim it, clock in at the kiosk, approve timesheets and export to payroll.

**Edge cases**

* Employee in two roles with different rates: shifts carry the role; timesheet lines split by role for payroll
* Clock-in without connectivity at a remote site: queued with device time and geolocation; flagged for review if the drift exceeds 5 minutes
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-883 (soft: shares timesheet UI), PAP-399, PAP-400, PAP-398 (hard), PAP-344 (hard), PAP-59, PAP-227 (hard), engagement scheduling model (soft), PAP-23, PAP-260, PAP-148 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/commerce/projects-time-billing` = PAP-883.
