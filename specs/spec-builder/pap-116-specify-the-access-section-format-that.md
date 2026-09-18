---
identifier: "PAP-116"
title: "Specify the access section format that compiles to permission-engine policies"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-59", "PAP-114", "PAP-229", "PAP-279"]
blocks: ["PAP-64", "PAP-361", "PAP-743"]
key: "spec-builder/access-section"
url: "https://linear.app/paperos/issue/PAP-116/specify-the-access-section-format-that-compiles-to-permission-engine"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:28.943Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-116: Specify the access section format that compiles to permission-engine policies

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec P0

**Goal**

Finalise the `access` section so "who can see this page and do what" is written once in YAML and compiled losslessly into PAP-59 policies, SQL predicates and permission tests. Replace the draft adapter in the permission engine with this contract.

**Scope**

* In: Zod `AccessSection` in `packages/spec/src/schema/access.ts`, compiler `toPolicies()`, validator rules, `pnpm spec gen:policies`, `access-matrix` output, `docs/spec/access.md`.
* Out: the evaluator (PAP-59), audience definitions (PAP-55, PAP-117), the conformance tests (PAP-122 consumes the matrix).

**Spec**

* Shape: `public: boolean`, `view: AudienceId[]`, `actions: Record<name, { audiences[], condition? }>`, `rows: Record<entity, Condition>`, `deny: AudienceId[]`, `fields: Record<"entity.field", { view[] }>`, `inherit: boolean`.
* `Condition` imported from the shared filter grammar `@paperos/core/filter` (PAP-279) so identity, tables and specs share one tree (`all | any | not`, ops `eq | neq | in | contains | gte | lte | isNull`); depth limit 8.
* Semantics: `deny` beats everything; `view` grants `page.view`; an action grants only itself (warn if its audience lacks view); `rows` compile to predicates merged by PAP-119 and enforced by oRPC `authorize`; `public: true` grants `anonymous` and conflicts with `actor.*` references; `app.spec.yaml` `defaults.access` merges unless `inherit: false`.
* Output sorted and deterministic; `packages/permissions/src/generated/spec-policies.json` with `source: { specPath, line }` per policy.
* Rules: `ACCESS_UNKNOWN_AUDIENCE`, `ACCESS_ACTION_NAME` (`^[a-z][a-zA-Z0-9]*$`), `ACCESS_ATTR_UNAVAILABLE` (warn), `ACCESS_FIELD_ENTITY_MISSING`, `ACCESS_PUBLIC_ACTOR_REF`, `ACCESS_DEPTH`.

**Interface contract**

* Provides: `AccessSectionSchema`, type `AccessSection`, `toPolicies(page, app): Policy[]`, `accessMatrix(page, app): Matrix` (`audience x action -> boolean`), `pnpm spec gen:policies`, generated `spec-policies.json`.
* Consumers: PAP-59 loads `spec-policies.json` (its `from-spec.ts` draft is replaced); PAP-64 permission tests and PAP-122 conformance read `accessMatrix`; PAP-119 merges `rows`; PAP-120 emits `DeniedState` when `page.view` fails; PAP-124 access editor edits this shape.
* Requires: PAP-114 schema; PAP-59 `Policy` type (pinned branch import if not merged); PAP-279 `Condition`; PAP-55 and PAP-117 audience ids.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (permissions `Condition` is an alias of `FilterTree` (PAP-279), so `rows:` conditions in the access section are FilterTree literals with `{ $var: 'principal.id' }` variables; the subject is the §1 `Principal`, audience ids come from PAP-55); §6 rows "`FilterTree`", "`Principal` and audiences" and "Page and app spec schema" (this issue compiles the spec side of the `can()` contract owned by PAP-59).

**Definition of done**

* Compile fixtures to expected `Policy[]` snapshots; wildcard expansion; inheritance; each rule pass and fail.
* Property test: `can()` from PAP-59 agrees with a naive reference evaluator on 500 random actor and action pairs for any valid section.
* Draft adapter replaced; its tests pass or are updated with reasons.
* Matrix committed for the three PAP-125 examples; docs; changelog; Linear comment with matrix and PR links.

**Test plan**

* Unit: compiler per feature, determinism (two runs byte-equal), condition depth, action name regex.
* Property (`fast-check`): compile then evaluate vs reference for random principals.
* Integration: `pnpm spec gen:policies` in the template repo, then PAP-59 loads the file and `can()` answers for the examples.
* No UI breakpoints; matrix rendered in the docs page at 1280 px.

**Demo**

Edit `customer-invoices.spec.yaml` to add `markPaid` for `staff.billing`, run `pnpm spec gen:policies && pnpm spec access-matrix customer-invoices` and read the matrix row flip from false to true; then `pnpm permissions explain --as staff.support --action page.action:markPaid` shows the denying line. One minute.

**Edge cases**

* Audience renamed in app spec: every page fails with file and line; `--fix` renames when `x-renamedFrom` is set.
* Staff audience referencing `actor.customerId`: warning.
* `public: true` with actions: allowed (pay-by-link); matrix marks them.
* Field rule for an entity missing from `data.entities`: error.
* Deeper than eight levels: error.

**Dependencies**

Blocked by PAP-114, PAP-59 (types), PAP-279 (`Condition`). Uses PAP-55, PAP-117. Blocks PAP-64, PAP-122.

**Agent**

Built by Quill (Page Spec Writer) with Forge (Schema Wright) on the compiler; reviewed by Sentinel (Security Auditor).

**Size**

M
