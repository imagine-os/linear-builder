---
identifier: "PAP-628"
title: "Record templates and field default values: FieldDef.defaultValue with dynamic tokens, per-dataset record templates and the New record menu"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "All view types"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-332", "PAP-613"]
blocks: ["PAP-427"]
key: "r4/tables/record-templates-and-field-defaults"
url: "https://linear.app/paperos/issue/PAP-628/record-templates-and-field-default-values-fielddefdefaultvalue-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:19.346Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-628: Record templates and field default values: FieldDef.defaultValue with dynamic tokens, per-dataset record templates and the New record menu

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Notion database templates, Airtable default values and ClickUp task templates let a team create consistent records in one click. Give every dataset field defaults (static or dynamic) and a set of named record templates that pre-fill fields, honoured by the grid, kanban inline add, forms and importers.

**Scope**

In: `FieldDef.defaultValue?: { kind: 'static', value } | { kind: 'dynamic', token: 'now' | 'today' | 'currentUser' | 'nextNumber' | 'fromParam' }`; table `record_template (tenant_id, dataset_id, name, icon, values jsonb, position, audience_id?)`; procedures `recordTemplates.*`; `NewRecordMenu`; `applyDefaults(dataset, partial, ctx)` used server-side by `records.create`.

Out: page templates and business packs (PAP-426, PAP-427 consume this), automation-created records (PAP-389 calls `applyDefaults` too), template marketplace.

**Spec**

* `applyDefaults` fills missing keys in this order: template values, field `defaultValue`, type default; dynamic tokens resolve server-side in the actor timezone; `fromParam` reads `?p.<key>=` on forms and deep links; defaults never override explicit values or `computed` fields.
* `FieldEditor` (PAP-332) gains a Default section per type: static input via the type's editor, dynamic token select where the type allows (`date` → `today|now`, `user` → `currentUser`, `autonumber` never).
* Record templates: values validated against `FieldDef[]` at save; `audience_id` limits who sees a template (PAP-62); `NewRecordMenu` replaces every "+ New" (grid footer, kanban column, gallery, list) with a split button: default create, or pick a template; `mod+shift+n` opens it.
* Templates may set relation fields to `{ ref: 'context' }` so a template used from a filtered kanban column or a related-records block inherits the column value or parent record.
* Import (PAP-199) and `records.create` share `applyDefaults`; the audit diff marks defaulted keys with `source: 'default' | 'template:<id>'`.
* Business packs (PAP-427) ship templates in the pack format (PAP-426 `recordTemplates` array).

**Interface contract**

Provides: `defaultValue` schema addition (PAP-161 minor bump), `applyDefaults`, `recordTemplates.list|create|update|delete|reorder`, `<NewRecordMenu datasetRef context />`, `RecordTemplate` type for PAP-426. Consumes: `records.create` (PAP-613), `FieldEditor` (PAP-332), editors per type (PAP-338, PAP-339), audiences (PAP-62), kanban and grid add affordances (PAP-167, PAP-343). Consumed by PAP-427 packs, PAP-199 importers, PAP-389 `record.create` action.

**Definition of done**

* Defaults and templates green in Vitest, integration and Playwright; stories at 375, 1024, 1920 in three themes; axe clean.
* `docs/views/record-templates.md`; CHANGELOG; Linear comment on PAP-426 with the template shape.

**Test plan**

* Unit: `applyDefaults` precedence; dynamic token resolution with a fixed clock and actor; `fromParam` parsing and type coercion; template validation rejects unknown fields.
* Integration: create through the API with no body gets defaults; kanban inline add in the Done column applies the template plus the column value; audit diff carries `source`.
* E2E: set Status default to Open and Owner to current user, add a "Bug" template, create from the kanban column split button, verify both fields; keyboard-only run.

**Demo**

Reviewer sets defaults on two fields, creates a "Client onboarding" template with five values, then adds a record from the grid footer using it. Under two minutes.

**Edge cases**

* Template references an archived field: value dropped with a warning badge on the template.
* Default `currentUser` on a public form: unresolved, left empty.
* Template audience mismatch: hidden from the menu, API returns `FORBIDDEN`.
* `nextNumber` on a non-autonumber field: validation error at save.

**Dependencies**

PAP-613 (hard), PAP-332 (hard, `FieldEditor`). Soft: PAP-62, PAP-167, PAP-343. Blocks PAP-427 packs (soft: packs can ship without templates).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/records-crud-procedures` = PAP-613.
