---
identifier: "PAP-705"
title: "Chunk progress in the burn report: which $2,500 chunk is active, issues landed versus planned per chunk from `plan/chunks.json`, forecast of chunk completion and a Needs Justin top-up card"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-98"]
blocks: []
key: "r4/pm-linear/chunk-progress-report"
url: "https://linear.app/paperos/issue/PAP-705/chunk-progress-in-the-burn-report-which-dollar2500-chunk-is-active"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:29.130Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-705: Chunk progress in the burn report: which $2,500 chunk is active, issues landed versus planned per chunk from `plan/chunks.json`, forecast of chunk completion and a Needs Justin top-up card

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Justin pays $50 per $2,500 of list-price spend and asked what each chunk buys. `plan/chunks.json` and `docs/build-chunks.md` plan the chunks; PAP-98 meters spend; nothing joins them. This issue adds a chunk section to the daily burn report and a one-click top-up card when the current chunk is about to run out, so the money question has a standing answer.

**Scope**

* In: `src/metering/chunks.ts` reading `plan/chunks.json` (chunk index, planned issues, planned list dollars, planned start and end), `chunk_progress(chunk, spent_usd, landed_issues, planned_issues, forecast_end)` computed from `usage_events` and PAP-97 `pr.merged` events, burn-report section `templates/burn-report.md` ("Chunk n of 4: $x of $2,500 (y%), issues landed a of b, forecast end <date>"), `pnpm burn --chunks`, Needs Justin top-up card at 85 percent of the last approved chunk, docs section in `docs/pm/credit-metering.md`.
* Out: re-planning the chunks (Atlas by hand, `plan/chunks.json` is the input), enforcement (PAP-111), Anthropic Console reconciliation (PAP-98 owns it).

**Spec**

* Chunk boundaries are cumulative list-price spend from `usage_events.cost_usd` since the plan start `2026-09-17T14:23Z`; the active chunk is the first whose upper bound exceeds cumulative spend; Justin's cost is `ceil(chunks) * 50` and shown beside the list total.
* Landed issues: Done or In Review with a merged PR since the chunk start, matched against the chunk's planned issue list; unplanned landings and planned-but-missing issues are listed separately (top five each).
* Forecast: linear regression over the last three days of spend gives the expected chunk end; compared with the planned end in `chunks.json`; a slip beyond one day is flagged in the report and in Atlas's Monday project update.
* Top-up card (PAP-94) at 85 percent of the final approved chunk: `Decision needed: approve chunk n+1 ($50 for $2,500 list)`, recommendation from the forecast, options continue, pause P2 claims, stop; default `pause P2 claims` after 48 h; `hard-block` when the reserve would be touched.
* Model mix per chunk (served model counts from the routing issue) shown as one line so Justin sees the Opus versus Sonnet split he asked about.

**Interface contract**

* Provides: `chunkProgress()`, table `chunk_progress`, burn-report section, `pnpm burn --chunks`, the top-up card key `chunk-topup-<n>`.
* Consumes: PAP-98 `usage_events` and report job, `plan/chunks.json`, PAP-97 merge events, PAP-94 `requestDecision()`, the model-routing served-model field.

**Definition of done**

* Three daily reports with the chunk section on staging (screenshots at 375 and 1280 px); numbers match `pnpm burn --chunks`.
* Seeded spend crossing 85 percent of chunk 1 files exactly one top-up card (test with mocked meter).
* Docs; changelog; Linear comment with the screenshots.

**Test plan**

* Unit: boundary arithmetic, landed-issue matching, forecast regression on fixture series, card dedupe.
* E2E: staging report job for three days.

**Demo**

Run `pnpm burn --chunks` and read `Chunk 1 of 4: $1,930 of $2,500 (77%), issues 41 of 58, forecast end 09-21 15:00Z`; open the burn report issue on a phone and see the same line. Under one minute.

**Edge cases**

* Chunk plan re-cut by Atlas mid-build: history keeps the old boundaries with a `replanned` marker; the report shows both for a day.
* Spend recorded late (Console lag): forecast uses metered data only; reconciliation adjustments appear as a delta line.
* Cumulative spend already past the last planned chunk: report says `beyond plan` and the top-up card is `hard-block`.
* No PRs merged in a chunk yet (day one): landed 0 of n, no slip flag before 24 h.

**Dependencies**

Hard: PAP-98. Soft: PAP-97, PAP-94, PAP-704, plan/chunks.json.

**Agent**

Builder: Ledger (Bookkeeper) with Atlas. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/session-model-and-effort-routing` = PAP-704.
