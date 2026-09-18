---
identifier: "PAP-817"
title: "ClickUp connector: spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments and attachments into the PM module with ClickUp markup to Markdown"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: "PAP-204"
children: []
blockedBy: ["PAP-816"]
blocks: []
key: "r4/migration/clickup-connector-and-markup-mapping"
url: "https://linear.app/paperos/issue/PAP-817/clickup-connector-spaces-folders-lists-tasks-subtasks-custom-fields"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:49.813Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-817: ClickUp connector: spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments and attachments into the PM module with ClickUp markup to Markdown

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

The ClickUp half of PAP-204: a REST v2 connector whose target model is the same PM tables, reusing the wizard steps the Linear sibling ships, plus the markup converter ClickUp needs and Linear does not.

**Scope**

In: `connectors/clickup/` on REST v2 (OAuth via the connections issue or PAT): discover teams, spaces, folders, lists with statuses and custom fields; stream tasks per list with `include_closed`, `subtasks`, page 100 at 100 rpm; comments; attachments streamed to PAP-37; mapping space to `pm_team`, list to `pm_project`, statuses to `pm_workflow_state` with `inferStateType`, task to `pm_issue` (custom task ids when enabled else generated, original stored in `pm_external_ref` with `external_url`), subtasks to `parent_id`, tags to `pm_label`, dependencies to `blocks`, custom fields to typed `custom jsonb` via PAP-164 types, comments with `mapClickUpMarkup(text)`; ordering from `orderindex`; `completed_at` from `date_closed`.

Out: ClickUp docs and whiteboards (PAP-418 converter reuse later), time-tracking reports, goals.

**Spec**

* Tasks in multiple lists import once with a relation note; state mapping is per list and the user may merge states.
* Recorded fixtures from the PaperOS Test ClickUp workspace (3 lists, 150 tasks, 5 custom fields, 40 comments, 10 attachments) are the CI gate; live run when `CLICKUP_TEST_TOKEN` exists.
* Rate limiter is a token bucket shared per team id; 429 honours `Retry-After`.

**Interface contract**

Provides: `registerConnector('clickup')`, `mapClickUpMarkup(text): string`, custom-field type mapping table in `docs/migration/pm-tools.md`. Consumes: Linear sibling steps, framework (PAP-347 to PAP-349), PM tables (PAP-100), PAP-201, PAP-164, PAP-37, test accounts (soft), conformance harness (soft).

**Definition of done**

* Recorded workspace imports with counts equal to the fixture; rerun zero duplicates; 20 markup fixtures convert; screenshots at seven widths light and dark for state mapping and the imported board; CHANGELOG.

**Test plan**

* Unit: markup conversion (mentions, checklists, code, links), custom field types, multi-list dedupe, rate limiter.
* E2E: wizard from a mocked PAT to the imported board with a merged state mapping.

**Demo**

Reviewer imports the recorded ClickUp workspace, merges two same-meaning statuses and opens the board with comments rendered as Markdown. Under two minutes.

**Edge cases**

* Private attachment URL with an expired token: run pauses resumable.
* Custom field type unknown: stored as text with a report line.
* Subtask whose parent is excluded: imported top-level with a note.

**Dependencies**

Hard: PAP-816. Soft: connections issue, test accounts, conformance harness.

**Agent**

Builder: Scout (Import Mapper). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/linear-connector-and-pm-mapping` = PAP-816.
