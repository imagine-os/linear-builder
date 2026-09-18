---
identifier: "PAP-764"
title: "Library and service cost model: paid tiers, seats, renewal dates and monthly cost per registry entry with a line in the daily burn report"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98", "PAP-216"]
blocks: []
key: "r4/libraries/library-cost-model"
url: "https://linear.app/paperos/issue/PAP-764/library-and-service-cost-model-paid-tiers-seats-renewal-dates-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.991Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-764: Library and service cost model: paid tiers, seats, renewal dates and monthly cost per registry entry with a line in the daily burn report

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (Execution Schedule stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

The registry records why we adopted AG Grid Community, tldraw or Resend; it does not record that the next tier costs money, when the trial ends or what the VPS services cost per month. PAP-98 reports Claude credit burn daily. Add the software line so Justin sees one number.

**Scope**

In: registry entry field `cost { model: free|open-core|per-seat|usage|flat, tier, monthlyUsd, seats?, renewsAt?, cancelBy?, owner, notes }` (PAP-216 schema, additive); `pnpm lib costs` printing the monthly total by category and the next 30 days of renewals; `docs/.generated/costs.json`; one line in PAP-98's daily report (`Software: $x/mo, renewals: n`) and a `costs` section on PAP-760; notification kind `library.renewal_due` 14 days before `cancelBy` to the owner. Out: invoices and payments (business-core), Claude credits (PAP-98).

**Spec**

* Costs are estimates entered by the owner from the vendor's public page with a URL; `verifiedAt` date; stale after 90 days (warning).
* Self-hosted services (MinIO, Hocuspocus) carry `monthlyUsd: 0` and an `infraShare` note pointing at the PAP-296 resource budget instead.
* Currency in `Money` wire form (PAP-302) converted to USD at entry time; `renewsAt` drives the notification.
* Totals appear in the PAP-89 release digest once a week and in the PAP-98 daily report.
* No secrets or account ids in the registry; billing portals are linked by URL only.

**Interface contract**

Provides: `cost` field, `pnpm lib costs`, `costs.json`, digest and burn-report lines, kind `library.renewal_due`. Consumes: registry schema and build (PAP-216), burn report (PAP-98), notification core (PAP-725), `Money` (PAP-302), resource budget (PAP-296). Consumed by: PAP-98, PAP-89, Justin.

**Definition of done**

* Ten entries carry costs; `pnpm lib costs` totals them; a fixture renewal 10 days out triggers the kind; burn report shows the line on staging.
* `docs/libraries/costs.md`; CHANGELOG entry.

**Test plan**

* Unit: schema, totals, staleness, renewal window.
* Integration: notification kind fires through the core with the `/__test` clock.
* E2E: none.

**Demo**

Run `pnpm lib costs`, read the total and the next renewal, open the health page costs section. Under one minute.

**Edge cases**

* Vendor changes pricing: owner edits with a new `verifiedAt`; history in git.
* Free tier with hard limits (Resend 3k emails): `model: usage` with the limit in notes and a PAP-40 alert suggestion.
* Owner leaves the roster: reassigned to Scout by the check.

**Dependencies**

Hard: PAP-216, PAP-98. Soft: PAP-725, PAP-302, PAP-296, PAP-89. Deferred: v0.2.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Sentinel (Code Reviewer) with Ledger checking the numbers.

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725, `r4/libraries/dependency-health-page` = PAP-760.
