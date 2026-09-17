---
identifier: "PAP-204"
title: "Import ClickUp and Linear workspaces into the PM module"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-100", "PAP-199", "PAP-201"]
blocks: []
key: "migration/clickup-linear"
url: "https://linear.app/paperos/issue/PAP-204/import-clickup-and-linear-workspaces-into-the-pm-module"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-204: Import ClickUp and Linear workspaces into the PM module

**Goal**

Bring project history along: import ClickUp workspaces (spaces, folders, lists, tasks, subtasks, custom fields, statuses, comments, attachments) and Linear workspaces (teams, projects, cycles, issues, sub-issues, labels, comments, relations) into the PaperOS PM module so a team switching tools keeps identifiers, states, assignees and discussion, and so PaperOS's own Linear workspace can be mirrored into the PM tables for `pm-linear/board-views`.

**Scope**

In:
- Connector `packages/import/src/connectors/clickup/` on ClickUp REST v2 (OAuth or PAT): `discover` teams -> spaces -> folders -> lists with statuses and custom field definitions; `stream` tasks per list with `include_closed=true`, `subtasks=true`, page 100, rate limit 100 rpm per token; comments via `/task/{id}/comment`; attachments from task `attachments[]` streamed to `data-layer/file-storage`; time tracking entries optional.
- Connector `packages/import/src/connectors/linear/` on `@linear/sdk`: `discover` teams, workflow states, labels, projects, milestones, cycles; `stream` issues with `filter: { updatedAt: { gt: cursor } }`, `first: 100` pagination, plus comments, attachments, relations, history optional; respects complexity-based rate limit with backoff.
- Mapping to `pm-linear/pm-data-model` tables: ClickUp space -> `pm_team`, list -> `pm_project`, statuses -> `pm_workflow_state` (type inferred from ClickUp `type: open|custom|closed|done`), task -> `pm_issue` (`identifier` from custom task id or `<TEAMKEY>-<n>` generated sequentially, priority 1-4 mapped to 1-4, `due_date`, `start_date`, `time_estimate` -> `estimate` in points via setting), subtask -> `parent_id`, tags -> `pm_label`, dependencies -> `pm_issue_relation blocks`, comments -> `pm_comment` (ClickUp comment markup to Markdown), custom fields -> issue `custom jsonb` typed via `tables/field-types`; Linear maps one-to-one by design (`pm_external_ref system: linear`).
- People matching: assignees and authors by email to tenant users; unmatched become `placeholder` users (`user.kind: service`, name preserved) invited later, per a wizard toggle.
- Wizard steps: workspace picker, team and list selection with counts, state mapping table (source state -> target state or create), people matching table, identifier strategy.

Out: ClickUp docs and whiteboards (docs later via a Notion-style converter), Linear roadmaps and initiatives, time tracking reports, two-way sync (`pm-linear/linear-sync` covers live Linear sync for PaperOS's own workspace).

**Spec**

- Identifier preservation: Linear keeps `PAP-123`; ClickUp uses custom task ids if enabled else generates, and the original ClickUp id is stored in `pm_external_ref.external_id` with `external_url`.
- Ordering: `sort_order` from ClickUp `orderindex` and Linear `sortOrder`.
- Closed items imported with `completed_at` from history where available, else `date_closed`; canceled states map to `canceled` type.
- Markdown fidelity: ClickUp comment and description markup converted with a small parser (mentions `@user`, checklists, code); Linear markdown passes through with attachment URLs rewritten.
- Incremental re-import via `updatedAt` cursors using `migration/id-mapping`; issues deleted in source archived here when the "mirror deletions" toggle is on.
- Import runs as the acting staff user; created_by on imported items is the placeholder or matched user, not the importer (audit reason `import:<run_id>`).

**Definition of done**

- Vitest: state type inference, priority mapping, identifier strategies, people matching, ClickUp markup conversion on 20 fixtures, relation mapping, incremental rerun with no duplicates.
- Integration: import the PaperOS Linear workspace (team PAP with this plan's issues) and a ClickUp test workspace (3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments); recordings attached; `pm-linear/board-views` renders the result.
- Playwright: wizard with state mapping and people matching; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for state mapping and imported board.
- Cross-check counts: issues, comments and attachments equal source counts in the run report.
- `docs/migration/pm-tools.md`; CHANGELOG entry; Linear comment with recordings and count table.

**Edge cases**

- ClickUp task in multiple lists: imported once in its home list, linked via a relation note for the others.
- Linear issue with a parent in another team: parent link kept; team differs, allowed by the PM model.
- State name collision across ClickUp lists with different meanings: mapping table is per list; user can merge.
- Comment author deleted in source: attributed to a placeholder "Former member".
- Attachment behind ClickUp auth (private URL): fetched with the token; expired token pauses the run resumable.
- Importing into a team that already has issues: identifier collisions resolved by continuing the sequence and recording the source id.

**Dependencies**

`migration/import-framework` and `pm-linear/pm-data-model` (hard). `migration/id-mapping`, `tables/field-types` (custom fields), `data-layer/file-storage`, `pm-linear/board-views` (to view the result). Coordinate with `pm-linear/linear-sync` so both write `pm_external_ref` compatibly.

**Agent**

Built by Scout (Import Mapper) with Atlas consulted on Linear fidelity. Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Forge (Schema Wright) for PM constraints.

**Size**

M: two connectors but the target model already mirrors Linear; ClickUp mapping is the bulk.
