---
identifier: "PAP-830"
title: "Migration verification dashboard and cutover checklist: source versus target counts and hashes per collection over time, parallel-run status, freeze notice and go-live sign-off"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-173", "PAP-201", "PAP-349", "PAP-387"]
blocks: []
key: "r4/migration/migration-verification-dashboard-and-cutover"
url: "https://linear.app/paperos/issue/PAP-830/migration-verification-dashboard-and-cutover-checklist-source-versus"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:24.416Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-830: Migration verification dashboard and cutover checklist: source versus target counts and hashes per collection over time, parallel-run status, freeze notice and go-live sign-off

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Imports report per run; a migration is many runs over weeks with the old tool still in use. A dashboard that compares source and target continuously, a checklist for the cutover day and a freeze notice for the team are what turn 'we imported it' into 'we moved'.

**Scope**

In: `migration_project (name, sources[], target_scope, status: planning|parallel_run|frozen|cut_over|closed, cutover_at, owner)`; datasets `migration.parity` (per collection: source count from `discover`, target count, last sync, hash agreement where the connector supports content hashes via PAP-201) and `migration.runs`; seeded dashboard `migration.status` with blocks (parity table, drift trend, open errors, checklist progress); cutover checklist (final incremental sync, export baseline via PAP-205, freeze source edits notice, DNS or link updates, notify team, go-live sign-off by an owner with typed confirmation); freeze banner shown to staff during `frozen`; PAP-208 reads and updates the project and checklist; report card export as PDF.

Out: automated source locking (tools rarely allow it), post-cutover two-way sync.

**Spec**

* Parity counts are refreshed by the scheduled resync issue's runs or on demand; discrepancies link to the PAP-349 run history filtered to that collection.
* Checklist items are computed where possible (last sync age, export baseline exists) and manual otherwise; sign-off is audited.
* The migration agent (PAP-208) may tick computed items, never the sign-off.

**Interface contract**

Provides: tables, datasets, dashboard `migration.status`, checklist component, freeze banner slot fill, PDF report card, `migration.projects.*`. Consumes: run history (PAP-349), mappings and hashes (PAP-201), dashboards (PAP-173), export (PAP-205), scheduled resync issue (soft), migration agent (PAP-208, soft), banner slot (PAP-264).

**Definition of done**

* Parity dataset equals brute force on a fixture migration with two sources; checklist flow Playwright with sign-off; screenshots at 375, 1024, 1920 light and dark; `docs/migration/cutover.md`; CHANGELOG.

**Test plan**

* Unit: parity computation, checklist auto-evaluation, state machine, sign-off guard.
* E2E: create a migration project over the fixture Airtable and CSV sources, run syncs, watch parity reach 100 percent, walk the checklist and sign off.

**Demo**

Reviewer opens the migration dashboard, sees one collection at 98 percent, drills to the missing rows, reruns and signs off the cutover. Under two minutes.

**Edge cases**

* Source count unavailable (CSV): parity shows target count only with 'no source count'.
* Cutover reverted: state back to `parallel_run` with an audit note; banner removed.

**Dependencies**

Hard: PAP-349, PAP-201, PAP-173. Soft: PAP-205, PAP-208, PAP-264, PAP-820.

**Agent**

Builder: Scout (Import Mapper) with Iris on the dashboard. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/scheduled-resync-and-sync-status` = PAP-820.
