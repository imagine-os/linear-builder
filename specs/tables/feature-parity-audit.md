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
blocks: ["PAP-171"]
key: "tables/feature-parity-audit"
url: "https://linear.app/paperos/issue/PAP-162/audit-airtable-notion-clickup-baserow-and-nocodb-view-features-into-a"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-162: Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist

**Goal**

Turn "every feature Airtable, Notion and ClickUp have for views" into a concrete, checkable parity list. The audit enumerates view types, field types, filter operators, grouping, aggregation, sharing and interaction features across Airtable, Notion, ClickUp, Baserow and NocoDB, marks which PaperOS issue covers each, and becomes the coverage tracker the project reports against.

**Scope**

In:
- `docs/views/parity.md` (human-readable) and `docs/views/parity.csv` (machine-readable) in `imagine-os/paperos-template`.
- Coverage script `pnpm --filter views parity:report` that prints percentage covered per product and per category.
- Gap issues: any feature not covered by an existing `tables/*` issue is proposed as a new Linear issue draft in the comment.

Out: implementing any feature; UI screenshots of competitors (link to public docs instead).

**Spec**

- Sources: public documentation and changelogs of Airtable, Notion, ClickUp, Baserow and NocoDB; the OSS repos of Baserow and NocoDB for their view/field enums. Use `WebFetch`; cite URLs in a `source` column.
- CSV columns: `id, category, feature, airtable, notion, clickup, baserow, nocodb, paperos_issue, paperos_status (planned|in_progress|done|wontdo), notes, source`. Product columns hold `yes|partial|no|paid`.
- Categories (minimum): view types; field types; filter operators per field type; sort options; grouping (levels, collapsed, aggregates per group); aggregations; row height/density; column ops (freeze, hide, resize, reorder, wrap); record expansion; inline editing; bulk edit; keyboard navigation; kanban (swimlanes, WIP, card cover, collapse); calendar/timeline/Gantt (dependencies, milestones, zoom); gallery/list; forms (conditional logic, prefill, branding); map; charts; formulas (function count); lookups/rollups; sharing (personal/shared/public, embed, password, expiry); permissions (field-level, view lock); dashboards (blocks, cross-filter); import/export; API access; automations (mark out of scope with pointer to `growth/*` or a future project).
- Expect 250-400 rows. Each row maps to a `tables/*` issue key or is marked `gap`.
- `parity:report` (`packages/views/scripts/parity-report.ts`, `csv-parse` 5.x) validates the CSV against a Zod row schema and fails on unknown issue keys by reading `plan.json` issue keys or a static list.
- Formula function inventory saved separately as `docs/views/formula-functions.csv` (name, airtable_name, notion_name, category, paperos_status) as direct input to `tables/formula-engine`.

**Definition of done**

- `parity.md` and `parity.csv` committed; CSV validates; report prints per-product coverage.
- At least 250 rows with source URLs; formula inventory has 80+ functions.
- Every `tables/*` issue is referenced by at least one row; gaps listed in a "Proposed issues" section with one-line acceptance criteria.
- `docs/views/parity.md` linked from `docs/views/view-model.md`.
- CHANGELOG entry (docs section); Linear comment summarising coverage percentages and the top 10 gaps for Atlas to decide on.
- Report script runs in CI gate 1 (`quality/ci-gate1`) as a docs check.

**Edge cases**

- Features gated behind paid tiers (Airtable Interfaces, Notion charts) recorded as `paid`, not `yes`.
- Features that are the same idea under different names (Notion "sub-items" vs ClickUp "subtasks") get one row with aliases in notes.
- Product docs that change during the audit: record the access date in `source`.
- Features PaperOS deliberately declines (spreadsheet cell formulas) marked `wontdo` with the ADR link.
- Baserow/NocoDB features absent from the big three are still listed; they often reveal cheap wins.

**Dependencies**

- `tables/view-model-spec` consumes the equivalence table; `libraries/data-landscape` and `libraries/oss-products` overlap on NocoDB/Baserow and should be cross-linked, not duplicated.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Nova (Views Engineer) for technical accuracy, Quill for doc quality.

**Size**

M: research-heavy but bounded; time-box to one session plus one revision.
