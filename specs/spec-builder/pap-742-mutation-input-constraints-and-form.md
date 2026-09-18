---
identifier: "PAP-742"
title: "Mutation input constraints and form derivation: typed `input` fields with validation rules, generated Zod for client and server, `ui.form` field lists"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-311", "PAP-739"]
blocks: []
key: "r4/spec-builder/mutation-input-constraints"
url: "https://linear.app/paperos/issue/PAP-742/mutation-input-constraints-and-form-derivation-typed-input-fields-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:34.920Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-26"
cycle: null
---

# PAP-742: Mutation input constraints and form derivation: typed `input` fields with validation rules, generated Zod for client and server, `ui.form` field lists

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

PAP-311 types mutation `input` as `Record<string, ScalarType>`: no required, min, pattern or relation constraints, so generated forms (PAP-361) cannot validate and the server re-derives rules by hand. Add a constraint grammar that defaults from the entity field grammar, emit one Zod schema used by the form, the hook and the router, and derive the `ui.form` field list.

**Scope**

In: `packages/spec/src/schema/input.ts` (`InputField`, `Constraint`), `data.mutations[].input` upgraded in PAP-311's schema (backwards compatible: a bare `ScalarType` still parses), generator `gen:forms` in `packages/spec/src/codegen/forms.ts` writing `apps/web/src/generated/<id>.forms.ts` (Zod schema, `defaultValues`, `fields[]` for `ui.form`) and the server-side `input` schema import for PAP-741 routers; validator rules; `docs/spec/forms.md`. Out: form components (PAP-233 adapters, PAP-236), layout of forms, file upload widgets (PAP-37).

**Spec**

* `InputField = { type: ScalarType | FieldType, from?: 'entity.<field>' (inherit constraints), required?, min?, max?, minLength?, maxLength?, pattern?, enum?, relation?, default?, label?: MessageRef, help?: MessageRef, widget?: ComponentRef }`; `from` copies the entity field's constraints and options so forms do not restate them.
* Generated Zod: one schema per mutation, `.strict()`, ICU-ready messages with ids per PAP-375 (`<specId>.mutations.<name>.<field>.error.<rule>`); the same module is imported by the generated hook (PAP-312) for client validation and by the generated router for server validation, so both fail identically.
* `fields[]` for `ui.form`: order from the spec, widget by type map shared with PAP-361's `field-components.ts` (`date` to `ui.datePicker`, `relation` to `ui.relationPicker`, `select` to `ui.select`), `internal` and `computed` entity fields excluded, `owner` excluded unless staff.
* Rules: `DATA_INPUT_UNKNOWN_FROM`, `DATA_INPUT_CONSTRAINT_TYPE` (min on a string), `DATA_INPUT_ENUM_EMPTY`, `DATA_INPUT_REQUIRED_DEFAULT` (required with default warns), `DATA_INPUT_PATTERN_INVALID`.
* Cross-field rules: `x-refine` escape hatch naming a function in `pages/<id>.logic.ts` (`refine.<name>`), typed stub generated once.

**Interface contract**

Provides: `InputFieldSchema`, `Constraint`, `generateForms()`, `pnpm spec gen:forms`, generated `<id>.forms.ts`, widget map, rule ids. Consumers: PAP-312 hooks (client validation), PAP-741 routers (server validation), PAP-361 form pages, PAP-377 form editor (constraint controls), PAP-233 form adapters, PAP-85 edge-case hunter (reads constraints for boundary inputs). Requires: PAP-311 (hard), field grammar (hard), PAP-375 `MessageRef` (soft), PAP-74 widget ids (soft; static map).

**Definition of done**

* `customer-invoices` `markPaid` and the clinic `appointment-form` generate schemas; the same invalid payload is rejected by the hook and by the router with the same rule id; `fields[]` renders through `ui.form` in Storybook.
* Two runs byte-identical; drift job covers `*.forms.ts`; `docs/spec/forms.md`; CHANGELOG entry; Linear comment with a generated file excerpt.

**Test plan**

* Unit: constraint to Zod mapping per type, `from` inheritance, rule fixtures, message id derivation, widget map.
* Integration: generated schema imported by a mocked router and a rendered form (Testing Library) reject the same inputs.
* E2E (Playwright): submit an invalid appointment form at 375 and 1280, read inline errors, fix, submit.

**Demo**

Add `{ id: amount, from: 'invoice.amount', min: 1 }` to `markPaid.input`, run `pnpm spec gen:forms customer-invoices`, open the generated Zod and the story, submit 0 and read the error. One minute.

**Edge cases**

* Entity field type changes: `from` picks it up on regeneration; stale hand-written override in `logic.ts` flagged by typecheck.
* Relation to an entity the audience may not read: widget becomes a read-only label (matches PAP-361).
* Pattern with catastrophic backtracking: validator warns using a regex complexity check.
* Currency input: `Money` wire encoding (PAP-302) as a decimal string; Zod transforms to `amountMinor`.

**Dependencies**

Hard: PAP-311, PAP-739. Soft: PAP-312, PAP-375, PAP-74, PAP-233, PAP-302, PAP-361.

**Agent**

Builder: Forge (Schema Wright) with Iris on the widget map. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/entity-backend-codegen` = PAP-741, `r4/spec-builder/entity-field-grammar` = PAP-739.
