---
identifier: "PAP-739"
title: "Define the entity field grammar in app.spec.yaml: field types, constraints, relations, `internal` and `computed` flags shared by entity pages, forms and backend codegen"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-117"]
blocks: ["PAP-360", "PAP-361", "PAP-741", "PAP-742"]
key: "r4/spec-builder/entity-field-grammar"
url: "https://linear.app/paperos/issue/PAP-739/define-the-entity-field-grammar-in-appspecyaml-field-types-constraints"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.851Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-739: Define the entity field grammar in app.spec.yaml: field types, constraints, relations, `internal` and `computed` flags shared by entity pages, forms and backend codegen

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec S

**Goal**

PAP-117 leaves `entities[].fields?` untyped; PAP-360 writes fields from the interview, PAP-361 derives columns and forms from them, and the golden path promises Drizzle tables from the same list. Three consumers, no grammar. Fix the `Field` shape once, aligned with the tables field-type union (PAP-164), so the interview, the page generators and the backend generator agree byte for byte.

**Scope**

In: `packages/spec/src/schema/field.ts` (`FieldSchema`, `FieldType`), the `entities[].fields` slot in `AppSpecSchema` (PAP-117), validator rules through PAP-115 `defineRule`, `docs/spec/entities.md`, fixtures for the three canned apps (clinic, agency, retail). Out: page-level `data` (PAP-311), the tables `FieldDef` runtime (PAP-338), Drizzle emission (PAP-741).

**Spec**

* `Field = { id, type, label?, required?, unique?, default?, internal?: boolean (hidden from customers), computed?: boolean (server-set), index?: boolean, pii?: 'none'|'low'|'high' (feeds PAP-355 and PAP-41), options?: string[] (select, multiSelect), relation?: { entity, kind: one|many, onDelete: restrict|cascade|setNull }, format?: { currency?, precision?, min?, max?, pattern?, maxLength? } }`.
* `FieldType` is the PAP-164 union re-exported from `@paperos/contract-tables` when present, else the frozen list `text|longText|number|currency|percent|date|dateTime|checkbox|select|multiSelect|relation|user|attachment|url|email|phone|json|rating`; `formula`, `lookup`, `rollup` are `computed` and need `x-expression` (PAP-171 territory, allowed but not generated).
* Every entity implicitly has `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`, `created_by`; declaring them is rule `APP_FIELD_RESERVED`. Naming: `^[a-z][a-zA-Z0-9]*$`, table column snake_case derived deterministically.
* Rules: `APP_FIELD_UNKNOWN_TYPE`, `APP_FIELD_RELATION_TARGET` (entity missing), `APP_FIELD_OPTIONS_REQUIRED` (select without options), `APP_FIELD_DUP`, `APP_FIELD_CURRENCY_FORMAT` (currency without `format.currency` falls back to the business profile default with a warning), `APP_FIELD_PII_UNSET` (warn on `email|phone|longText` without `pii`).
* `owner` convention: a `relation(user)` field named `owner` or flagged `x-owner: true` is the ownership field PAP-361 uses for customer row conditions; at most one per entity.

**Interface contract**

Provides: `FieldSchema`, `FieldType`, `Field`, `entityColumns(entity)` (explicit plus implicit fields), `RESERVED_FIELDS`, JSON Schema fragment merged into `app.spec.schema.json`, rule ids above. Consumers: PAP-360 (writes fields), PAP-361 (columns, kanban and calendar options, forms), PAP-741, PAP-742, PAP-123 (relation edges), PAP-41 (`pii`), PAP-208 migration agent. Requires: PAP-117 `AppSpecSchema` (hard), PAP-164 or PAP-338 union (soft, frozen copy with a drift test), PAP-126 currency default (soft).

**Definition of done**

* Schema, rules and fixtures merged; three canned apps validate with zero warnings; JSON Schema snapshot committed and drift-checked in gate 1.
* Drift test against `@paperos/contract-tables` `FieldType` when present; `docs/spec/entities.md` lists every type with an example; ADR entry via PAP-130 naming the frozen union.
* Comments on PAP-360 and PAP-361 pointing at the schema; CHANGELOG entry.

**Test plan**

* Unit (Vitest): every type parses; every rule pass and fail fixture; reserved names; relation cycle allowed (self-relation) but `cascade` on self warns.
* Property (`fast-check`): random valid entities round-trip through `parse(stringify())`.
* Integration: PAP-117 `gen:app` emits typed `entities.ts` including fields; no UI.

**Demo**

Add `fields: [{ id: dueAt, type: date }, { id: patient, type: relation, relation: { entity: patient, kind: one } }]` to `appointment` in the clinic fixture, run `pnpm spec:validate`, then break the relation target and read `APP_FIELD_RELATION_TARGET` with the line. Under one minute.

**Edge cases**

* Entity with 200 fields: allowed; warning suggests splitting.
* Relation to an entity in a disabled module: `MODULE_DISABLED` via PAP-265's rule, not a field error.
* `select` options renamed later: `x-renamedFrom` on the option so PAP-430 can write a data codemod.
* Field id collides with a route param name: warning `APP_FIELD_PARAM_SHADOW`.

**Dependencies**

Hard: PAP-117. Soft: PAP-164, PAP-338, PAP-126, PAP-115. Blocks PAP-360, PAP-361, PAP-741.

**Agent**

Builder: Quill (Page Spec Writer) with Forge (Schema Wright). Reviewer: Sentinel (Code Reviewer) and Nova for field-type fit.

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/entity-backend-codegen` = PAP-741, `r4/spec-builder/mutation-input-constraints` = PAP-742.
