---
identifier: "PAP-162"
title: "Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist"
project: "tables"
projectName: "Table & Views Engine"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Staff"]
milestone: "Grid with sort, filter, group"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-171", "PAP-382", "PAP-483"]
key: "tables/feature-parity-audit"
url: "https://linear.app/paperos/issue/PAP-162/audit-airtable-notion-clickup-baserow-and-nocodb-view-features-into-a"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:41.619Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-162: Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Research M

**Goal**

Turn "every view feature Airtable, Notion and ClickUp have" into a checkable parity list across Airtable, Notion, ClickUp, Baserow and NocoDB, mapped row by row to `tables/*` issues, plus the formula function inventory PAP-171 implements against. The CSV becomes the coverage tracker the project reports from.

**Scope**

In: `docs/views/parity.md`, `docs/views/parity.csv`, `docs/views/formula-functions.csv`, coverage script `pnpm --filter views parity:report`, a "Proposed issues" section for uncovered features.

Out: implementing anything; competitor screenshots (link public docs).

**Spec**

* Sources: public docs and changelogs, plus Baserow and NocoDB repos for view and field enums; every row cites a URL and access date.
* CSV columns: `id, category, feature, airtable, notion, clickup, baserow, nocodb, paperos_issue, paperos_status (planned|in_progress|done|wontdo), notes, source`; product cells `yes|partial|no|paid`.
* Categories (minimum 25): view types; field types; filter operators per type; sorting; grouping; aggregations; density; column ops; record expansion; inline and bulk edit; keyboard; kanban; calendar/timeline/Gantt; gallery/list; forms; map; charts; formulas; lookups/rollups; sharing; permissions; dashboards; import/export; API; automations (PAP-174); record history and trash (PAP-334, PAP-333); schema editing (PAP-332).
* 250 to 400 rows; `paperos_issue` must be a PAP identifier or `gap`.
* `parity-report.ts` (`csv-parse` 5.x) validates rows with Zod, fails on unknown identifiers (reads `linear-ids.json` or a static list), prints coverage per product and per category.
* `formula-functions.csv`: `name, airtable_name, notion_name, category, signature, paperos_status`; 80 or more functions.

**Interface contract**

Provides: `parity.csv` schema and `parity:report` exit code consumed by Gate 1 docs checks (PAP-78); `formula-functions.csv` consumed by PAP-171 `defineFunction` coverage tests; the "Proposed issues" list consumed by Atlas. Consumes: issue identifiers from Linear. No code exports.

**Definition of done**

* Both CSVs and `parity.md` committed; report prints coverage per product; at least 250 rows with sources.
* Every `tables/*` issue referenced by at least one row; gaps listed with one-line acceptance criteria.
* `parity.md` linked from `docs/views/view-model.md`; report wired into Gate 1 as a docs check.
* CHANGELOG (docs) entry; Linear comment with coverage percentages and top ten gaps.

**Test plan**

* Unit: Zod row schema rejects a bad status, an unknown identifier and a missing source; coverage maths on a 10-row fixture.
* Integration: `pnpm parity:report` runs in CI and fails when a referenced issue key is unknown.
* E2E and visual: none (research deliverable).

**Demo**

Reviewer runs `pnpm --filter views parity:report`, reads the coverage table (per product, per category), opens `parity.md` and spot-checks three rows' source links. Under two minutes.

**Edge cases**

* Paid-tier features recorded as `paid`, not `yes`.
* Same idea under different names: one row with aliases in notes.
* Docs change mid-audit: access date in `source`.
* Deliberately declined features (`wontdo`) link the ADR.
* Baserow/NocoDB-only features still listed; they are often cheap wins.

**Dependencies**

None; starts now. Feeds PAP-161 (equivalence column), PAP-171 (function inventory) and PAP-174 (trigger and action lists). Cross-link, do not duplicate, PAP-213 and PAP-214.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Nova (Views Engineer) for accuracy, Quill for the docs.

**Size**

M: bounded research; time-box one session plus one revision.

**Pending issues**

Bracketed references above are fully specified work packages that Linear refused to create on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free-plan issue cap). Their specs live in the project document(s) [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded.
