---
identifier: "PAP-117"
title: "Define app.spec.yaml (audiences, navigation, entities, integrations) that page specs inherit from"
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
blockedBy: ["PAP-114"]
blocks: ["PAP-123", "PAP-126", "PAP-160", "PAP-264", "PAP-28"]
key: "spec-builder/app-level-spec"
url: "https://linear.app/paperos/issue/PAP-117/define-appspecyaml-audiences-navigation-entities-integrations-that"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-117: Define app.spec.yaml (audiences, navigation, entities, integrations) that page specs inherit from

**Goal**

Define `specs/app.spec.yaml`, the single app-wide file holding audiences, navigation, entities, integrations, defaults and theme that page specs inherit from, so page specs stay short and consistent and the router, permission engine, canvas and search have one place to read app structure.

**Scope**

In:
- Zod 4 `AppSpec` in `packages/spec/src/schema/app.ts`:
  ```yaml
  specVersion: 1
  app: { id: paperos-template, name: PaperOS, tenantModel: multi, defaultLocale: en-US }
  audiences:
    - { id: customer.any, kind: customer, label: Customer }
    - { id: customer.pro, kind: customer, extends: customer.any, segment: { plan: pro } }
    - { id: staff.support, kind: staff, label: Support }
    - { id: agent.builder, kind: agent }
  navigation:
    staff: [{ label: Dashboard, route: /_app/dashboard, icon: layout-dashboard, children: [] }]
    customer: [{ label: Invoices, route: /_app/invoices, icon: receipt }]
  entities:
    - { id: invoice, table: invoices, label: Invoice, plural: Invoices, searchable: true, owner: Ledger }
  integrations: [{ connector: stripe, mode: test }]
  defaults: { layout: { template: app }, access: { deny: [agent.*] }, states: { error: { copy: Something went wrong. } } }
  theme: default
  ```
- `resolvePageSpec(page, app): ResolvedPageSpec` deep-merging `defaults`, expanding audience wildcards, attaching entity metadata; used by validator, codegen and canvas.
- Validator rules: `APP_NAV_ROUTE_MISSING`, `APP_ENTITY_TABLE_MISSING` (table not exported by `packages/db/src/schema` from `data-layer/drizzle-schema`), `APP_AUDIENCE_CYCLE` (`extends` loops), `APP_DUP_ID`.
- Generated outputs via `pnpm spec gen:app`: `apps/web/src/generated/navigation.ts` (typed nav trees per audience consumed by `app-shell/router-layouts` nav slot and `identity/staff-console-shell`), `audiences.ts` (union type used by `identity/rbac-abac`), `entities.ts`.
- JSON Schema `app.spec.schema.json` and `docs/spec/app-spec.md`.

Out: audience semantics and segment evaluation (`identity/audience-model`), page-level sections, per-tenant navigation overrides (later).

**Spec**

- Exactly one `specs/app.spec.yaml` per app; `paperos create` (`app-shell/create-cli`) writes it from the template with the app id filled in.
- Audience `kind` enum `customer|staff|partner|admin|agent|anonymous`; `segment` is a flat key/value map matched against actor attributes by the permission engine.
- Navigation items may carry `audiences` to hide items; codegen filters at render using `useCan('page.view')` rather than trusting the static list.
- `entities[].fields` optional summary `{ name, type, label }` used for docs and the canvas; the Drizzle schema remains the source of truth and a drift warning fires when names diverge.
- `integrations` entries reference `spec-builder/integrations-section` connector ids; page specs can only use connectors listed here.
- `theme` resolves to a token preset from `design-system/theming`.

**Definition of done**

- Vitest: parse fixture, merge precedence (page beats app defaults, `inherit: false` clears), audience expansion, each validator rule.
- `gen:app` outputs committed and drift-checked; router nav renders from generated navigation (screenshot at 375 and 1280 for staff and customer audiences).
- Template repo ships a populated `app.spec.yaml`; `paperos-spec validate` passes.
- `docs/spec/app-spec.md`; CHANGELOG entry; Linear comment with screenshots and generated files.
- Type `AudienceId` imported by `identity/rbac-abac` compiles.

**Edge cases**

- Navigation item route with params (`/_app/invoices/$id`): rejected in nav, only static routes allowed.
- Two audiences with the same label but different ids: allowed with a warning.
- Entity table renamed in a migration: `APP_ENTITY_TABLE_MISSING` blocks the PR until the spec is updated.
- Empty `navigation` for an audience with pages granting view: warn `APP_NAV_ORPHAN_PAGES` listing routes.
- App declares `tenantModel: single`: pages with `rows` conditions on `tenantId` warn as redundant.
- Very large app (500 entities): merge runs under 100 ms; memoised by file hash.

**Dependencies**

`spec-builder/schema` (hard). Soft: `data-layer/drizzle-schema` (table existence check), `identity/audience-model` (kinds), `app-shell/router-layouts` (nav consumer). Unblocks `spec-builder/access-section` wildcard expansion, `spec-builder/spec-to-canvas`, `collab/knowledge-search` entity registration.

**Agent**

Built by Quill (Page Spec Writer). Reviewed by Atlas and Forge (Schema Wright) for the entity mapping; Sentinel (Code Reviewer).

**Size**

S: one schema and a merge function, but it must be agreed with identity and router owners.
