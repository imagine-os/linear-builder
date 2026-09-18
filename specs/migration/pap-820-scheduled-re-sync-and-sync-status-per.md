---
identifier: "PAP-820"
title: "Scheduled re-sync and sync status: per-source Routines calling runIncremental, sync status page with last run, drift and errors, pause and resume, and connector health alerts"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-201", "PAP-349", "PAP-565"]
blocks: []
key: "r4/migration/scheduled-resync-and-sync-status"
url: "https://linear.app/paperos/issue/PAP-820/scheduled-re-sync-and-sync-status-per-source-routines-calling"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:50.296Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-820: Scheduled re-sync and sync status: per-source Routines calling runIncremental, sync status page with last run, drift and errors, pause and resume, and connector health alerts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-201 makes incremental imports possible and explicitly leaves scheduling to 'a Routine'. Nobody owns that Routine, the page that shows whether last night's sync worked, or the alert when a token expires. Without them incremental import is a CLI feature.

**Scope**

In: `import_schedule (source_id, cron, timezone, enabled, last_run_id, next_run_at, on_source_delete policy, failure_count)`; PAP-43 cron jobs calling `runIncremental(sourceId)` with concurrency one per source and a 5-minute overlap window; status page `_app/settings/import/sync` (last run, records changed, drift versus source counts from `discover`, errors) with pause, resume and 'run now'; alerts via PAP-136 on two consecutive failures or `reauth_required` from the connections issue; Google Sheets live-link mode as the first consumer (`gsheets` incremental via revision check) since PAP-200 leaves live sync out; `import.sync.completed|failed` events.

Out: two-way sync, webhook-driven near-real-time sync (v0.3, noted), per-record sync conflicts beyond PAP-201 rules.

**Spec**

* Schedules run in the tenant timezone; a run that overlaps the previous is skipped and counted, never queued twice.
* Failure backoff doubles the interval up to a day and resets on success; the page shows the effective next run.
* Drift is computed only for connectors whose `discover` returns counts; otherwise 'unknown' with no alert.

**Interface contract**

Provides: `import.schedules.*`, jobs, status page, alert kinds `import.sync.failed|reauth`, events, gsheets revision-based incremental. Consumes: cursors and `runIncremental` (PAP-201), run history UI (PAP-349), jobs (PAP-43), notifications (PAP-136), connections (PAP-815, soft), CSV and Sheets connector (PAP-200).

**Definition of done**

* Fixture-connector schedule runs three times in a test clock with one injected failure and one overlap, producing the expected runs and one alert; status page Playwright; screenshots at 375, 1024, 1920 light and dark.
* `docs/migration/sync.md`; CHANGELOG.

**Test plan**

* Unit: cron and timezone next-run, overlap skip, backoff, drift arithmetic, alert once-per-transition.
* E2E: schedule the fixture source hourly, advance the clock, see runs in history and the status page, pause and confirm no run.

**Demo**

Reviewer schedules the demo Airtable fixture nightly, clicks Run now, watches the status update and reads the drift column. Under one minute.

**Edge cases**

* Source deleted at the provider: run fails with `NOT_FOUND`, schedule auto-paused with a banner.
* Tenant timezone changes: next run recomputed; no double run.

**Dependencies**

Hard: PAP-201, PAP-349, PAP-43. Soft: PAP-136, PAP-200, connections issue.

**Agent**

Builder: Scout (Import Mapper). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/source-oauth-connections-and-token-refresh` = PAP-815.
