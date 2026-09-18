---
identifier: "PAP-816"
title: "Linear connector: teams, states, labels, projects, cycles, issues, comments, relations and attachments into the PM module with identifiers preserved and the reusable StateMapping and PeopleMatching steps"
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
blockedBy: ["PAP-100", "PAP-199", "PAP-201", "PAP-347", "PAP-349"]
blocks: ["PAP-817", "PAP-825"]
key: "r4/migration/linear-connector-and-pm-mapping"
url: "https://linear.app/paperos/issue/PAP-816/linear-connector-teams-states-labels-projects-cycles-issues-comments"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:49.644Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-816: Linear connector: teams, states, labels, projects, cycles, issues, comments, relations and attachments into the PM module with identifiers preserved and the reusable StateMapping and PeopleMatching steps

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-204 is one M for two connectors; the Linear half is the strategic one because it mirrors PaperOS's own workspace into PM tables for PAP-102 and PAP-101. This child ships the Linear connector and the wizard steps the ClickUp sibling and every future PM importer reuse.

**Scope**

In: `connectors/linear/` on `@linear/sdk`: discover teams, workflow states, labels, projects, milestones, cycles; stream issues with `updatedAt` cursor and `first: 100`, comments, attachments (streamed to PAP-37), relations; complexity-aware backoff on `X-Complexity` and 429; mapping to PAP-100 tables one to one (`pm_team`, `pm_project`, `pm_workflow_state`, `pm_issue` with `PAP-123` identifiers preserved, `parent_id`, `pm_label`, `pm_issue_relation blocks`, `pm_comment`, cycles); people matching by email with placeholder users; wizard steps `StateMapping`, `PeopleMatching`, `IdentifierStrategy` exported for reuse; incremental via PAP-201 cursors with a 'mirror deletions' toggle.

Out: ClickUp (sibling), Linear roadmaps and initiatives, two-way sync (PAP-101), documents.

**Spec**

* Import runs as the acting staff user; `created_by` is the matched or placeholder user; audit reason `import:<run_id>`.
* Writes `pm_external_ref` through the PAP-201 helper compatibly with PAP-101 so a later sync recognises imported rows.
* Ordering from `sortOrder`; `completed_at` from `completedAt`; trashed issues only with 'include archived'.
* Recorded API responses (team PAP, anonymised) are the CI fixture; the live run against team PAP uses a read-only key.

**Interface contract**

Provides: `registerConnector('linear')`, wizard steps `StateMapping`, `PeopleMatching`, `IdentifierStrategy`, `inferStateType(status)`, recorded fixture set. Consumes: framework (PAP-347, PAP-348, PAP-349), PM tables (PAP-100), external refs (PAP-201), files (PAP-37), board views (PAP-102), connections (PAP-815, soft), conformance harness (soft).

**Definition of done**

* Recorded import of team PAP: issue, comment, relation and attachment counts equal the fixture; PAP-102 renders the board; rerun yields zero duplicates.
* Wizard Playwright with state and people mapping; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; axe clean; `docs/migration/pm-tools.md` Linear section; CHANGELOG.

**Test plan**

* Unit: state type inference, priority mapping, identifier strategies, people matching, relation mapping, complexity backoff.
* E2E: run the wizard against the recorded workspace, map states one to one, commit, open the PM board grouped by state with comments intact.

**Demo**

Reviewer runs the Linear connector against the recorded team PAP fixture, keeps identifiers, commits and opens the PM board showing this plan's issues. Under two minutes.

**Edge cases**

* Parent in another team: kept; allowed by the PM model.
* Deleted comment author: placeholder 'Former member'.
* Target team already has issues: sequence continues; source id recorded.

**Dependencies**

Hard: PAP-347, PAP-100, PAP-201. Soft: PAP-348, PAP-349, PAP-37, PAP-102, PAP-101 coordination, connections issue, conformance harness. Blocks the ClickUp sibling (shared steps).

**Agent**

Builder: Scout (Import Mapper) with Atlas on Linear fidelity. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/source-oauth-connections-and-token-refresh` = PAP-815.
