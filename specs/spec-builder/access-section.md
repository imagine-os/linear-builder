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
blockedBy: ["PAP-114", "PAP-229", "PAP-279", "PAP-59"]
blocks: ["PAP-64"]
key: "spec-builder/access-section"
url: "https://linear.app/paperos/issue/PAP-116/specify-the-access-section-format-that-compiles-to-permission-engine"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-116: Specify the access section format that compiles to permission-engine policies

**Goal**

Finalise the `access` section of a page spec so that "who can see this page and do what on it" is written once in YAML and compiled losslessly into `identity/rbac-abac` policies, SQL predicates and permission tests. Replace the draft adapter in the permission engine with this contract.

**Scope**

In:
- Zod 4 schema `AccessSection` in `packages/spec/src/schema/access.ts`:
  ```yaml
  access:
    public: false
    view: [customer.any, staff.support, staff.admin]
    actions:
      markPaid: { audiences: [staff.billing], condition: { path: resource.status, op: eq, value: open } }
      export:   { audiences: [staff.admin] }
    rows:
      invoice: { path: resource.customerId, op: eq, ref: actor.customerId }
    deny: [agent.*]
    fields:
      invoice.internalNotes: { view: [staff.*] }
  ```
- `Condition` type imported from `@paperos/permissions` (same `all|any|not` tree, ops `eq|neq|in|contains|gte|lte|isNull`) so nothing is duplicated.
- Compiler `packages/spec/src/access/compile.ts`: `toPolicies(page: PageSpec, app: AppSpec): Policy[]` producing `page.view`, `page.action:<name>`, `<entity>.<verb>` row policies and `field.view:<entity>.<field>` with `source: { specPath, line }`; wildcards `staff.*` expand against `app.spec.yaml` audiences.
- Validator rules (plugin to `spec-builder/validator`): `ACCESS_UNKNOWN_AUDIENCE`, `ACCESS_ACTION_WITHOUT_LOGIC` (action in access but not in `logic.actions`), `ACCESS_LOGIC_WITHOUT_ACCESS` (error when `status: ready`), `ACCESS_EMPTY_VIEW` unless `public: true`, `ACCESS_ROW_ENTITY_NOT_IN_DATA`.
- `paperos-spec access-matrix [--format md|json]` printing audiences by actions per page; JSON consumed by `identity/permission-tests` and `spec-builder/conformance-tests`.
- Docs `docs/spec/access.md` with three worked examples (customer sees own invoices, support impersonates, agents cannot delete).

Out: evaluation and SQL compilation (`identity/rbac-abac`), audience definitions (`identity/audience-model`, `spec-builder/app-level-spec`).

**Spec**

- Semantics: `deny` beats everything; `view` grants `page.view`; an action grants only its named action, never implied view (validator warns if an action audience lacks view).
- `rows` compile to predicates applied by generated data hooks (`spec-builder/data-section`) and by oRPC `authorize` middleware; one entry per entity in `data.entities`.
- `public: true` means `page.view` for the built-in `anonymous` audience; conflicts with `rows` referencing `actor.*` (error).
- Inheritance: `app.spec.yaml` may declare `defaults.access` (for example `deny: [agent.*]`) merged before compile; page can override with `inherit: false`.
- Output is deterministic and sorted so `policies.generated.json` diffs are readable; `pnpm spec gen:policies` writes `packages/permissions/src/generated/spec-policies.json`.

**Definition of done**

- Vitest: compile fixtures to expected `Policy[]` (snapshot), wildcard expansion, inheritance, each validator rule pass and fail.
- Property test (`fast-check`): any valid `AccessSection` compiles and `can()` from `identity/rbac-abac` agrees with a naive reference evaluator on 500 random actor/action pairs.
- Draft adapter in `packages/permissions/src/from-spec.ts` replaced; its tests pass unchanged or with documented updates.
- `access-matrix` output committed for the three example pages of `spec-builder/spec-docs`.
- `docs/spec/access.md`; CHANGELOG entry; Linear comment with matrix and PR links.

**Edge cases**

- Audience renamed in `app.spec.yaml`: every page referencing it fails with file and line; `--fix` offers a rename when `x-renamedFrom` is set.
- Condition referencing `actor.customerId` for a staff audience with no such attribute: warn `ACCESS_ATTR_UNAVAILABLE`.
- Action name containing a dot or uppercase: rejected, actions are `^[a-z][a-zA-Z0-9]*$`.
- Circular `all/any` nesting deeper than 8: error, keeps SQL compilation bounded.
- Page with `public: true` and `actions`: allowed for anonymous flows such as pay-by-link; matrix marks them.
- Field rule for an entity not in `data.entities`: error.

**Dependencies**

`spec-builder/schema` (hard), `identity/rbac-abac` (Policy and Condition types; if not merged, import from its branch and pin). `identity/audience-model` and `spec-builder/app-level-spec` for audience ids. Unblocks `identity/permission-tests`, `spec-builder/conformance-tests`.

**Agent**

Built by Quill (Page Spec Writer) with Forge (Schema Wright) on the compiler. Reviewed by Sentinel (Security Auditor) and Atlas.

**Size**

M: small surface, but security semantics must be exact and tested against the engine.
