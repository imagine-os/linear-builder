---
identifier: "PAP-812"
title: "Social analytics report: per-post and per-account metrics history, engagement rate by platform and time slot, best-time suggestions in the composer and a campaign roll-up block"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-173", "PAP-387", "PAP-402"]
blocks: []
key: "r4/growth/social-analytics-report"
url: "https://linear.app/paperos/issue/PAP-812/social-analytics-report-per-post-and-per-account-metrics-history"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:24.416Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-812: Social analytics report: per-post and per-account metrics history, engagement rate by platform and time slot, best-time suggestions in the composer and a campaign roll-up block

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-402 fetches metrics into `social_post_target.metrics` and stops. Buffer and Postiz sell the report: what worked, when, on which platform. A history table, two datasets and a best-time hint in the composer finish the loop cheaply.

**Scope**

In: `social_metric_snapshot (target_id, captured_at, impressions, likes, comments, shares, clicks, video_views)` captured by the PAP-402 metrics job at 1 h, 24 h, 72 h and 7 d after publish; datasets `social.postPerformance` (engagement rate, by platform, campaign, author) and `social.bestTimes` (engagement by weekday and hour in tenant timezone over 90 days); composer hint 'best time for LinkedIn: Tue 09:00' when data exists; dashboard block `social.engagement` and report route `_app/marketing/social/analytics`; CSV export.

Out: competitor benchmarking, paid ad metrics, comment moderation.

**Spec**

* Snapshots are append-only; the latest is denormalised to `metrics` for cards; rates divide by the account follower count captured daily when the adapter exposes it, else by impressions.
* Best-time suggestions require at least 20 posts in the window; below that the composer shows nothing.
* All adapters in `dryRun` return fixture metrics so the report renders in CI.

**Interface contract**

Provides: snapshot table, datasets, block, composer hint component, report route, CSV export. Consumes: metrics fetch and adapters (PAP-402, PAP-403), dashboards and charts (PAP-173, PAP-170), composer (PAP-401), campaigns (PAP-799 for the cross-channel roll-up, soft).

**Definition of done**

* Datasets equal brute force on a fixture of 200 posts; hint threshold test; screenshots at 375, 1024, 1920 light and dark; CSV opens.
* `docs/growth/social.md` gains an analytics section; CHANGELOG.

**Test plan**

* Unit: engagement rate maths, weekday and hour bucketing across DST, threshold, snapshot schedule.
* E2E: publish three posts through the mock adapter, run the metrics job with fixture values, open the report and see the best-time hint in the composer.

**Demo**

Reviewer opens Social analytics on the seeded tenant, switches to LinkedIn and reads the best-time heatmap, then opens the composer and sees the hint. Under one minute.

**Edge cases**

* Platform rate limits on metrics: snapshots skipped and marked; report shows gaps, never zeros.
* Account disconnected: history kept, new snapshots stop.

**Dependencies**

Hard: PAP-402, PAP-173. Soft: PAP-403, PAP-170, PAP-401.

**Agent**

Builder: Beacon (Campaign Composer) with Iris on the heatmap. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/email-broadcast-campaigns` = PAP-799.
