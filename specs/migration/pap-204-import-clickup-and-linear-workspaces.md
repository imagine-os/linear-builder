---
identifier: "PAP-204"
title: "Import ClickUp and Linear workspaces into the PM module"
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
blockedBy: ["PAP-100", "PAP-199", "PAP-201", "PAP-349"]
blocks: []
key: "migration/clickup-linear"
url: "https://linear.app/paperos/issue/PAP-204/import-clickup-and-linear-workspaces-into-the-pm-module"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:56.327Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-204: Import ClickUp and Linear workspaces into the PM module

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Bring project history along: import ClickUp workspaces (spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments, attachments) and Linear workspaces (teams, projects, cycles, issues, sub-issues, labels, comments, relations) into the PM module so a switching team keeps identifiers, states, assignees and discussion, and so PaperOS's own Linear workspace can be mirrored into PM tables for PAP-102.

**Scope**

In:

* `connectors/clickup/` on REST v2 (OAuth or PAT): discover teams, spaces, folders, lists with statuses and custom fields; stream tasks per list with `include_closed`, `subtasks`, page 100, 100 rpm; comments; attachments streamed to PAP-37.
* `connectors/linear/` on `@linear/sdk`: discover teams, states, labels, projects, milestones, cycles; stream issues with `updatedAt` cursor, `first: 100`, comments, attachments, relations; complexity-aware backoff.
* Mapping to PAP-100 tables: space -> `pm_team`, list -> `pm_project`, statuses -> `pm_workflow_state` with type inferred, task -> `pm_issue` (identifier preserved or generated, priority 1-4, dates, estimate), subtask -> `parent_id`, tags -> `pm_label`, dependencies -> `pm_issue_relation blocks`, comments -> `pm_comment` (ClickUp markup to Markdown), custom fields -> typed `custom jsonb`; Linear one-to-one.
* People matching by email; unmatched become `placeholder` users per a wizard toggle.
* Wizard steps: workspace picker, team and list selection with counts, state mapping table, people matching table, identifier strategy.

Out: ClickUp docs and whiteboards, Linear roadmaps and initiatives, time-tracking reports, two-way sync (PAP-101).

**Spec**

* Linear keeps `PAP-123`; ClickUp uses custom task ids if enabled, else generates, storing the original in `pm_external_ref` with `external_url`.
* Ordering from `orderindex` and `sortOrder`; closed items get `completed_at` from history or `date_closed`.
* Import runs as the acting staff user; `created_by` is the matched or placeholder user; audit reason `import:<run_id>`.
* Incremental via `updatedAt` cursors with PAP-201; "mirror deletions" toggle archives here.

**Interface contract**

Provides: `registerConnector('clickup'|'linear')`, `mapClickUpMarkup(text): string`, `inferStateType(status)`, wizard steps `StateMapping`, `PeopleMatching`, `IdentifierStrategy` (reusable by future PM importers), writes `pm_external_ref` through PAP-201's helper compatibly with PAP-101. Consumes: PAP-199, PAP-100 tables, PAP-201, PAP-164 for custom fields, PAP-37, PAP-102 to view results, PAP-198 work package 2 (test accounts) ClickUp workspace, PAP-198 fixtures.

**Definition of done**

* Integration: import team PAP from Linear (this plan) and the ClickUp test workspace (3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments); PAP-102 renders both; counts of issues, comments and attachments equal the sources; recordings attached.
* Rerun produces zero duplicates.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for state mapping and imported board; axe clean.
* `docs/migration/pm-tools.md`; CHANGELOG; Linear comment with recordings and count table.

**Test plan**

* Vitest: state type inference, priority mapping, identifier strategies, people matching, 20 ClickUp markup fixtures, relation mapping, incremental rerun, complexity backoff with recorded Linear responses.
* Conformance suite for both connectors.
* Playwright: wizard with state mapping and people matching; visual baselines at the seven widths, both themes.

**Demo**

Reviewer runs the Linear connector against team PAP with a read-only key, maps states one-to-one, commits, and opens the PM board showing this plan's issues grouped by state with comments intact. Under two minutes.

**Edge cases**

* Task in multiple lists: imported once with a relation note.
* Parent in another team: kept; allowed by the PM model.
* Same state name with different meanings across lists: mapping is per list; user may merge.
* Deleted comment author: placeholder "Former member".
* Private attachment URL and expired token: run pauses resumable.
* Target team already has issues: sequence continues; source id recorded.

**Dependencies**

PAP-199 and PAP-100 (hard). PAP-201, PAP-164, PAP-37, PAP-102; PAP-198 work package 2 (importer test accounts; integration tests read only its env names and skip with `skipped: no-credentials` when unset) for the live ClickUp run. Coordinate with PAP-101 on `pm_external_ref`.

**Agent**

Built by Scout (Import Mapper) with Atlas on Linear fidelity. Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Forge (Schema Wright).

**Size**

M: two connectors; the target model mirrors Linear, ClickUp mapping is the bulk.
