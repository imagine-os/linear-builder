---
identifier: "PAP-638"
title: "Field-level permissions on custom datasets: per-field read and write by audience compiled into projections, editors and validators"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-229", "PAP-332", "PAP-613"]
blocks: []
key: "r4/tables/field-level-permissions"
url: "https://linear.app/paperos/issue/PAP-638/field-level-permissions-on-custom-datasets-per-field-read-and-write-by"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.708Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-638: Field-level permissions on custom datasets: per-field read and write by audience compiled into projections, editors and validators

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Deferred to v0.2 (NJ-19; reinstate via NJ-14). Airtable field permissions and ClickUp custom-field permissions hide salary from staff and cost from customers on the same table. Add per-field `read|write` audience rules on custom datasets, enforced in the query projection, the record procedures, editors and forms, not only hidden in the UI.

**Scope**

In: `FieldDef.permissions?: { read?: AudienceId[], write?: AudienceId[] }` (PAP-161 minor bump); `fieldMask(actor, dataset)` used by PAP-335 projections, `records.*` validation, `views.publicQuery`, export and forms; `FieldEditor` permissions section; `can('field.read', { datasetId, fieldId })` explain.

Out: entity datasets (their page specs and PAP-59 policies own field access), row-level rules (RLS and `toPredicate`), column-level encryption (PAP-353).

**Spec**

* Absent `permissions` means inherit dataset access; `read` lists audiences that may see the field; `write` must be a subset of `read`; owners and admins always pass.
* Compiler: unreadable fields are removed from `SELECT` and from filter and sort compilation (a filter on an unreadable field yields `FORBIDDEN`, never a silent empty result); aggregates on unreadable fields hidden.
* Procedures: `records.create|update` strip unreadable keys from responses and reject writes to unwritable keys with `FIELD_FORBIDDEN`; bulk (PAP-334) and import (PAP-199) call the same mask.
* UI: hidden columns are absent from the field menu (not merely unchecked); editors for read-only fields render the read-only cell with a lock tooltip and `explain()` in dev; forms omit the fields.
* Audit: permission changes write `field.permissions.changed`; the permission matrix generator (PAP-63) gains a per-dataset field matrix.

**Interface contract**

Provides: `FieldDef.permissions`, `fieldMask`, error `FIELD_FORBIDDEN`, `FieldPermissionsEditor`, matrix export. Consumes: `can()` and audiences (PAP-229, PAP-62), records procedures (PAP-613), `FieldEditor` (PAP-332), compiler core (PAP-335), export and public query (export issue, public links issue).

**Definition of done**

* Mask enforced in compiler, procedures, export and forms with the cross-tenant harness extended; matrix generated; stories at 375, 1024, 1920; `docs/views/field-permissions.md`; CHANGELOG; Security Auditor sign-off.

**Test plan**

* Unit: mask computation; subset rule; filter on unreadable field forbidden; response stripping.
* Integration: `callAs(customer)` never receives the salary key through query, get, export or form; write rejected; owner sees all.
* E2E: restrict Budget to Staff, sign in as the demo customer, confirm the column, filter option and export omit it.

**Demo**

Reviewer restricts Budget to Staff and shows the customer portal view without it, then tries a filter via the API and reads `FIELD_FORBIDDEN`. Under two minutes.

**Edge cases**

* Formula depends on an unreadable field: formula readable only if all inputs readable, else hidden.
* Lookup across datasets: target field's mask applies too.

**Dependencies**

PAP-229 (hard), PAP-613 (hard), PAP-332 (hard). Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/tables/records-crud-procedures` = PAP-613.
