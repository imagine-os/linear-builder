---
identifier: "PAP-811"
title: "Sales dashboard and forecast: pipeline funnel, win rate, velocity, weighted forecast by stage probability, activity leaderboard and stale-deal alerts as dashboard blocks"
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
blockedBy: ["PAP-173", "PAP-189", "PAP-387"]
blocks: []
key: "r4/growth/sales-dashboard-and-forecast"
url: "https://linear.app/paperos/issue/PAP-811/sales-dashboard-and-forecast-pipeline-funnel-win-rate-velocity"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:24.416Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-811: Sales dashboard and forecast: pipeline funnel, win rate, velocity, weighted forecast by stage probability, activity leaderboard and stale-deal alerts as dashboard blocks

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-189 stops at 'pipeline value'. The questions a founder asks next (how much will close this month, where do deals stall, who is following up) are five datasets over tables that already exist, rendered by the dashboard engine that PAP-186 already proves.

**Scope**

In: datasets `crm.funnel` (deals entering each stage per period with conversion), `crm.winRate` (by owner, source, period), `crm.velocity` (median days per stage), `crm.forecast` (open deals times stage probability by expected close month, plus commit and best-case from an owner-set `forecast_category`), `crm.activityLeaderboard`, `crm.staleDeals` (no activity for N days); seeded dashboard `crm.sales` installed with the CRM module; number blocks `crm.pipelineValue|weightedForecast|winRate`; stale-deal alert kind via PAP-136 weekly; drill-down from every block to the filtered pipeline view.

Out: quota management, AI forecasting, revenue recognition (finance).

**Spec**

* Forecast uses `crm_pipeline_stage.probability` and `crm_deal.expected_close_date`; deals without a date fall into 'unscheduled'.
* Stage history for funnel and velocity comes from the `system` activities the PAP-187 trigger writes, so no new table is needed.
* Datasets compile through PAP-163 with `FilterTree` params and respect `crm.*.read` scoping (a rep sees own deals by default).

**Interface contract**

Provides: six datasets, three number blocks, dashboard `crm.sales`, alert kind `crm.deal.stale`, drill filters. Consumes: CRM views and seed (PAP-189), dashboard engine and print (PAP-173), compiler (PAP-163), charts (PAP-170), notifications (PAP-136), stage history trigger (PAP-790).

**Definition of done**

* Datasets equal brute-force calculations on the demo seed; dashboard settles under 2 s; cross-filter replay; screenshots at 375, 768, 1024, 1440, 1920 in three themes; every block has a text summary.
* `docs/growth/sales-dashboard.md`; CHANGELOG.

**Test plan**

* Unit: funnel conversion maths, median velocity, weighted forecast by month, stale detection, permission scoping.
* E2E: open `/crm/dashboard`, click a funnel stage to filter the pipeline, change the period, export PDF.

**Demo**

Reviewer opens the sales dashboard on the seeded tenant, reads this month's weighted forecast, clicks the stalled-deals block and lands on the filtered pipeline. Under two minutes.

**Edge cases**

* Pipeline with custom stages: probabilities default from stage kind (open 20, won 100, lost 0) until edited.
* Deal moved backwards: velocity counts the re-entry; funnel counts the first entry only.
* Owner with zero deals: leaderboard shows them with zeros, never hidden.

**Dependencies**

Hard: PAP-189, PAP-173. Soft: PAP-163, PAP-170, PAP-136, PAP-790.

**Agent**

Builder: Beacon (CRM Builder) with Nova on blocks. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/crm-schema-routers-page-specs` = PAP-790.
