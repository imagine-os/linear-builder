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
blocks: ["PAP-28", "PAP-123", "PAP-126", "PAP-160", "PAP-264", "PAP-360", "PAP-361", "PAP-363"]
key: "spec-builder/app-level-spec"
url: "https://linear.app/paperos/issue/PAP-117/define-appspecyaml-audiences-navigation-entities-integrations-that"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:50:29.345Z"
---

# PAP-117: Define app.spec.yaml (audiences, navigation, entities, integrations) that page specs inherit from

**Goal**

Define `specs/app.spec.yaml`, the single app-wide file holding audiences, navigation, entities, integrations, defaults and theme that page specs inherit from, so page specs stay short and the router, permission engine, canvas and search read app structure from one place.

**Scope**

* In: Zod `AppSpec` in `packages/spec/src/schema/app.ts`, merge precedence, `pnpm spec gen:app`, validator rules, `docs/spec/app-spec.md`, a populated template file.
* Out: business profile section (PAP-126 extends this file), connector registry content (PAP-121), navigation rendering (PAP-16 consumes).

**Spec**

* Shape: `app { id, name, tenantModel: multi | single, defaultLocale }`, `audiences[] { id, kind: customer | staff | partner | admin | agent | anonymous, label, extends?, segment? }` (shape agreed with PAP-55), `navigation: Record<audienceKind, NavItem[]>` (static routes only), `entities[] { id, table, label, plural, searchable, owner, fields? }`, `integrations[] { connector, mode }`, `defaults { layout, access, states }`, `theme`.
* Precedence: page beats app defaults; `inherit: false` clears; audience `extends` expands transitively with cycle detection.
* `gen:app` writes `apps/web/src/generated/app/{navigation,audiences,entities}.ts`; navigation items render through `useCan('page.view')` at runtime, never trusting the static list.
* Rules: `APP_SINGLE_FILE`, `APP_NAV_PARAM_ROUTE`, `APP_ENTITY_TABLE_MISSING` (against Drizzle schema when available), `APP_NAV_ORPHAN_PAGES` (warn), `APP_AUDIENCE_CYCLE`, `APP_DUP_AUDIENCE_LABEL` (warn), `APP_TENANT_ROWS_REDUNDANT` (warn).
* Merge for 500 entities under 100 ms, memoised by file hash.

**Interface contract**

* Provides: `AppSpecSchema`, types `AppSpec`, `AudienceId`, `EntityId`, `NavItem`, functions `loadAppSpec(root)`, `resolvePage(page, app): ResolvedPageSpec`, `expandAudience(id)`, generated navigation and entity modules, `pnpm spec gen:app`.
* Consumers: PAP-116 audience expansion, PAP-119 entity check, PAP-121 enabled connectors, PAP-123 start nodes per audience, PAP-16 navigation, PAP-59 `AudienceId` type, PAP-138 entity registration, PAP-126 `business:` extension, PAP-22 writes the file for new apps.
* Requires: PAP-114 schema. Soft: PAP-32 Drizzle schema for table checks, PAP-55 kinds, PAP-16 nav consumer.

**Definition of done**

* Vitest: parse fixture, precedence, `inherit: false`, audience expansion and cycle, each rule.
* `gen:app` outputs committed and drift-checked; router nav renders from generated navigation (screenshots at 375 and 1280 px for staff and customer audiences).
* Template ships a populated `app.spec.yaml` that validates.
* Docs; changelog; `AudienceId` imported by PAP-59 compiles; Linear comment with screenshots.

**Test plan**

* Unit: merge matrix (app default only, page only, both, `inherit: false`), expansion, rule fixtures.
* Bench: 500-entity fixture merge under 100 ms.
* Integration: `gen:app` then typecheck of the generated modules in `apps/web`.
* Visual: navigation rendered for two audiences at 375 and 1280 px through gate 3.

**Demo**

Add a `Reports` item under `navigation.staff`, run `pnpm spec gen:app`, reload the staff console and see the new item; sign in as a customer and it is absent. One minute.

**Edge cases**

* Nav route with params: rejected.
* Same label, different ids: warning.
* Entity table renamed by migration: blocks the PR until the spec updates.
* Audience with pages but empty navigation: warning listing routes.
* `tenantModel: single` with tenant row conditions: redundancy warning.

**Dependencies**

Blocked by PAP-114. Soft: PAP-32, PAP-55, PAP-16. Blocks PAP-126, PAP-28, PAP-123.

**Agent**

Built by Quill (Page Spec Writer); reviewed by Atlas and Forge (Schema Wright).

**Size**

S
