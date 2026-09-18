---
identifier: "PAP-825"
title: "Asana, Trello and Jira import into the PM module: API connectors for Asana and Jira Cloud, Trello JSON export reader, reusing StateMapping, PeopleMatching and IdentifierStrategy"
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
blockedBy: ["PAP-100", "PAP-816"]
blocks: []
key: "r4/migration/asana-trello-jira-connectors"
url: "https://linear.app/paperos/issue/PAP-825/asana-trello-and-jira-import-into-the-pm-module-api-connectors-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:50.696Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-825: Asana, Trello and Jira import into the PM module: API connectors for Asana and Jira Cloud, Trello JSON export reader, reusing StateMapping, PeopleMatching and IdentifierStrategy

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

After ClickUp and Linear, the next three tools a switching team names are Asana, Trello and Jira. With the PM mapping and wizard steps already built, each is a connector over the same target model; shipping them together keeps the mapping table in one place.

**Scope**

In: `connectors/asana/` (REST with PATs or OAuth via the connections issue: workspaces, projects, sections to states, tasks, subtasks, custom fields, comments, attachments); `connectors/trello/` (board JSON export file and REST: lists to states, cards, checklists to subtasks or Markdown, labels, comments, attachments); `connectors/jira/` (Jira Cloud REST v3 with API token: projects, issue types, statuses and categories to state types, issues, subtasks, epics as parents, comments in ADF converted to Markdown, attachments, issue links to relations); people matching by email; identifier strategies (Jira keys preserved like Linear); recorded fixtures from public sample data.

Out: Jira Server and Data Center, Asana portfolios and goals, Trello Power-Ups, two-way sync.

**Spec**

* ADF to Markdown covers paragraphs, headings, lists, code, mentions, links and tables; unsupported nodes become a note with a count in the report.
* Trello checklists map to subtasks by default with a toggle to inline them as Markdown checkboxes.
* All three pass `connectorConformance()` and register wizard steps from the Linear child unchanged.

**Interface contract**

Provides: three connectors, `adfToMarkdown`, Trello export reader, mapping tables in `docs/migration/pm-tools.md`. Consumes: Linear child steps and PM mapping, PM tables (PAP-100), connections issue, PAP-201, PAP-37, conformance harness.

**Definition of done**

* Recorded fixtures for all three import with counts equal to the fixture manifests; reruns zero duplicates; 20 ADF fixtures convert; screenshots at 375, 1024, 1920 light and dark for state mapping on Jira; CHANGELOG.

**Test plan**

* Unit: ADF conversion, checklist mapping toggle, status category inference, epic parenting, link mapping.
* E2E: import the Jira sample project, keep keys, open the PM board grouped by state with epics as parents.

**Demo**

Reviewer uploads a Trello board export, maps lists to states and opens the board with checklists as subtasks. Under two minutes.

**Edge cases**

* Jira issue type with no category: mapped to `unstarted` with a report line.
* Trello card in an archived list: imported archived only with the toggle.
* Asana task in multiple projects: imported once with relations.

**Dependencies**

Hard: PAP-816, PAP-100. Soft: connections issue, PAP-201, PAP-37, conformance harness.

**Agent**

Builder: Scout (Import Mapper). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/linear-connector-and-pm-mapping` = PAP-816.
