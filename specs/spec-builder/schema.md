---
identifier: "PAP-114"
title: "Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Spec schema and validator"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-115", "PAP-116", "PAP-117", "PAP-119", "PAP-120", "PAP-121", "PAP-123", "PAP-124", "PAP-132", "PAP-207", "PAP-249", "PAP-74", "PAP-85"]
key: "spec-builder/schema"
url: "https://linear.app/paperos/issue/PAP-114/define-the-pagespecyaml-schema-purpose-logic-access-data-integrations"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-114: Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases

**Goal**

Define the canonical `page.spec.yaml` format that every PaperOS page must have, as a Zod 4 schema in `packages/spec` with a generated JSON Schema for editors and TypeScript types for codegen. The validator, codegen, conformance tests, canvas and permission engine all read this contract, so it lands first and changes only through ADRs.

**Scope**

In:
- `packages/spec/src/schema/page.ts`: Zod 4 `PageSpec` with sections `meta` (`id`, `title`, `route`, `surface: customer|staff|developer|agent|public`, `owner` character, `status: draft|ready|built|deprecated`, `specVersion: 1`), `purpose` (paragraph plus `successMetric`), `logic` (named `actions` each with `steps[]`, `guard`, `effects[]`, `onError`), `access`, `data`, `integrations` (interim shapes; finalised by `spec-builder/access-section`, `spec-builder/data-section`, `spec-builder/integrations-section`), `layout` (`template: app|public|focus|kiosk`, `slots` map), `components` (tree of `{ id: ComponentRef, key, props, slot, events, children }`), `states` (`loading`, `empty`, `error`, `offline`, `denied` plus custom, each `{ copy, component? }`), `events` (transitions `{ on, to: RouteRef, guard?, kind: navigate|mutation|integration }`), `edgeCases[]` (`{ id, scenario, expected, test: unit|e2e|manual }`).
- `packages/spec/src/schema/common.ts`: `SpecId` `^[a-z][a-z0-9-]*$`, `RouteRef`, `AudienceRef`, `EntityRef`, `ComponentRef` `^(ui|app)\.[a-z][A-Za-z0-9]*$` (matches `design-system/component-spec-mapping`).
- `pnpm --filter spec schema:build` emitting `packages/spec/schema/page.spec.schema.json` via `zod-to-json-schema` and `src/generated/types.d.ts`; committed and drift-checked in gate 1.
- `parsePageSpec(yamlText, { file })` using `yaml` 2.x CST so every `SpecIssue { code, path, message, line, col, hint }` carries a location. Codes are `SPEC_*`.
- `x-*` extension keys preserved; all other unknown keys rejected (`.strict()`).
- Fixtures in `packages/spec/fixtures/`: `minimal.spec.yaml`, `maximal.spec.yaml`, ten invalid files each targeting one rule.
- `docs/spec/page-spec.md` field reference generated from Zod `.describe()` strings.

Out: cross-file checks (`spec-builder/validator`), `app.spec.yaml` (`spec-builder/app-level-spec`), codegen, editor UI.

**Spec**

- File location `specs/pages/<id>.spec.yaml`; `meta.id` must equal the filename stem; first line `# yaml-language-server: $schema=../../packages/spec/schema/page.spec.schema.json`.
- Minimal valid example:
  ```yaml
  specVersion: 1
  meta: { id: customer-invoices, title: Invoices, route: /_app/invoices, surface: customer, owner: Nova, status: draft }
  purpose: { summary: Customers review and pay invoices., successMetric: 90% of invoices paid in-app }
  access: { view: [customer.any] }
  layout: { template: app, slots: { main: ui.dataTable } }
  components: [{ id: ui.dataTable, key: invoiceTable, slot: main, props: { density: comfortable } }]
  states: { empty: { copy: No invoices yet. } }
  edgeCases: [{ id: no-tenant, scenario: user has no tenant, expected: redirect to onboarding, test: e2e }]
  ```
- `status: ready` requires `access`, `data` or `x-static: true`, at least three `edgeCases`, and every `events[].to` to be a `RouteRef`.
- Component `events` values must be `actions.<name>` referencing `logic.actions`.
- `migrations/v1-to-v2.ts` skeleton and `migrateSpec()` so future versions have a path.

**Definition of done**

- Vitest: fixtures parse; each invalid fixture fails with the expected `code`, `line` and `col`; snapshot of the JSON Schema.
- `schema:build` idempotent; drift check wired into the `generated-drift` job of `quality/ci-gate1`.
- JSON Schema gives autocompletion in VS Code on the fixture files (screenshot in PR).
- `docs/spec/page-spec.md` generated with every field described; ADR `docs/adr/00NN-PAP-<n>-page-spec-format.md` registered in `collab/decision-log`.
- Types exported from `@paperos/spec` and consumed by `app-shell/router-layouts` `useSpec` (replace its interim type).
- CHANGELOG entry; Linear comment linking docs, schema file and the ADR.

**Edge cases**

- YAML anchors and merge keys (`<<: *base`) are allowed and resolved before validation; issues point at the merged line.
- Duplicate `components[].key` in one spec: error `SPEC_DUP_KEY` listing both lines.
- Route contains params (`/_app/invoices/$id`): `RouteRef` accepts TanStack `$param` syntax only, not `:param`.
- Spec 200 KB or larger: warn `SPEC_TOO_LARGE`, suggest splitting into sub-pages.
- Windows line endings and BOM: normalised before parsing, positions still correct.
- `specVersion` missing: treated as 1 with a warning until 2 exists.

**Dependencies**

None hard. Soft: `design-system/component-spec-mapping` (interim `ComponentRef` regex agreed). Unblocks `spec-builder/validator`, `spec-builder/access-section`, `spec-builder/app-level-spec`, `spec-builder/data-section`, `spec-builder/layout-codegen`, `spec-builder/spec-to-canvas`, `collab/canvas-view`, `quality/edge-case-hunter`.

**Agent**

Built by Quill (Page Spec Writer). Reviewed by Atlas for the contract, Sentinel (Code Reviewer), and Iris for the components section.

**Size**

M: little code, but every key name is permanent and a dozen projects consume it.
