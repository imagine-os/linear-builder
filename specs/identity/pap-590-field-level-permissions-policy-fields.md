---
identifier: "PAP-590"
title: "Field-level permissions: policy `fields:` allow and deny lists, response masking in the repository and oRPC output, write rejection per field, `useCan` for fields and spec `data.fields[].access`"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Roles and audiences enforced end to end"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-227", "PAP-229", "PAP-268"]
blocks: []
key: "r4/identity/field-permissions"
url: "https://linear.app/paperos/issue/PAP-590/field-level-permissions-policy-fields-allow-and-deny-lists-response"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.124Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-590: Field-level permissions: policy `fields:` allow and deny lists, response masking in the repository and oRPC output, write rejection per field, `useCan` for fields and spec `data.fields[].access`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

RLS decides which rows; nothing decides which columns. A customer must not see `internal_notes` or `cost_price`, support must not edit `credit_limit`, and an agent should read but never write `email`. Hasura and Supabase expose column privileges; PAP-228 already has a `permissionColumns` map for SQL. This adds field rules to the same policies and enforces them in one place on the way out and on the way in.

**Scope**

In: `Policy.fields?: { allow?: string[], deny?: string[] }` in `packages/permissions` model with validation against `permissionColumns`; `maskFields(actor, action, resourceType, rows)` applied by the repository (PAP-568, soft) and by an oRPC output middleware for hand-written routers; write path: `update`/`create` inputs containing a denied field return `FORBIDDEN` with `details[].path`; `useCan(action, resource, { field })` and a `canField()` helper for forms; spec `data.fields[].access` (PAP-116, PAP-119) compiling to field policies; list shape columns (PAP-270) intersected with allowed fields per principal at subscribe time; docs section 'Field permissions'.

Out: Encryption (PAP-353), PII classification (PAP-559), search snippets (PAP-39 respects masked bodies by re-checking), export redaction (PAP-420 reuses `maskFields`).

**Spec**

* Resolution: field visibility for `read` is the union of allowed fields across matching allow policies minus any deny; deny wins; unspecified means all fields (backward compatible); masked fields are omitted from the object, never set to null, and the DTO type is a `Partial` marked with `__masked: string[]` in dev.
* Write: `update` with a denied field fails atomically; `create` with a denied field fails unless the field has a server default and the client omitted it.
* Shapes: the proxy (PAP-270) intersects requested `columns` with the principal's allowed columns for the table and rejects a request naming a denied column with `SHAPE_FORBIDDEN`; PGlite therefore never stores masked data.
* `explain()` reports field decisions with sources; PAP-64's matrix gains a fields dimension when a spec declares `data.fields[].access`.
* Performance: mask computation memoised per request per resource type; under 50 µs per row at 50 fields (bench).

**Interface contract**

Provides: `Policy.fields`, `maskFields`, `canField`, `useCan` field option, output middleware `maskOutput()`, shape column intersection hook, spec key `data.fields[].access`, docs. PAP-638 (custom datasets, deferred) compiles `FieldDef.permissions` into `Policy.fields` and calls `maskFields`, so entity and custom datasets share one enforcement path.

Consumes: Policy model and explain (PAP-227), adapter and `useCan` (PAP-229), routers (PAP-268), `permissionColumns` (PAP-228), shape proxy (PAP-270, soft), entity factory (PAP-568, soft), spec data section (PAP-116, PAP-119, soft). Consumed by PAP-164 editors, PAP-165 grid (hide masked columns), PAP-333 record page, PAP-420 export, PAP-64.

**Definition of done**

* Customer reading an invoice gets no `internal_notes`; support updating `credit_limit` gets `FORBIDDEN` with the path; agent read includes `email`, agent write of `email` refused (compose tests through `callAs`).
* Shape request naming a denied column returns `SHAPE_FORBIDDEN`; allowed subscribe streams only permitted columns (integration with Electric).
* `useCan(..., { field })` story: form field hidden for customer, read-only for support; bench committed; docs; changelog under Identity.

**Test plan**

* Unit: resolution of allow, deny and unspecified across policies, masking of nested and array fields, write rejection paths, memoisation.
* E2E: grid demo as three audiences shows different column sets; explain CLI prints the field decision with the spec line.

**Demo**

Run `pnpm permissions explain --actor fixtures/customer.json --action invoice.read --resource invoice:123 --fields` and read which fields are hidden and why, then open the invoice as the customer and as support. Under two minutes.

**Edge cases**

* Field used in a filter or sort the principal may not read: list refuses with `VALIDATION` naming the field (no side-channel).
* Computed or formula fields (PAP-168): masked when any input field is denied.
* Field renamed in the schema: `permissionColumns` typecheck fails, never a silent leak.

**Dependencies**

Blocked by PAP-227, PAP-229, PAP-268 (hard). Soft: PAP-228, PAP-270, PAP-116, PAP-119, PAP-568. Consumed by PAP-164, PAP-165, PAP-333, PAP-420, PAP-64.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Security Auditor; Edge Case Hunter for side channels).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/entity-factory` = PAP-568, `r4/data-layer/pii-registry` = PAP-559, `r4/tables/field-level-permissions` = PAP-638.
