---
identifier: "PAP-361"
title: "Build entity-derived page specs: `pnpm spec gen:entity-pages` derives list, detail, form and settings pages per entity and audience with view specs, comment anchors and access rules"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Developer", "Staff"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-116", "PAP-117", "PAP-161"]
blocks: ["PAP-363"]
key: "gp/spec-builder/entity-pages"
url: "https://linear.app/paperos/issue/PAP-361/build-entity-derived-page-specs-pnpm-spec-genentity-pages-derives-list"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:10.040Z"
---

# PAP-361: Build entity-derived page specs: `pnpm spec gen:entity-pages` derives list, detail, form and settings pages per entity and audience with view specs, comment anchors and access rules

**Goal**

Give every entity in `app.spec.yaml` a complete, spec-first CRUD surface without anyone writing YAML: a list page (grid view), a detail page (fields, comments, activity) and a form page (create and edit) per audience that may read or write it, plus the staff settings pages. These generated specs are ordinary `page.spec.yaml` files that PAP-120 and PAP-119 then turn into code, so the golden path produces real pages, not placeholders.

**Scope**

In:

* `pnpm spec gen:entity-pages [--entity <id>] [--check]` in `packages/spec/src/codegen/entity-pages.ts` writing `specs/pages/<surface>/<entity>-list.spec.yaml`, `<entity>-detail.spec.yaml`, `<entity>-form.spec.yaml` for each `(entity, audience kind)` pair where the access rules grant `read` (list, detail) or `create|update` (form).
* Derivation rules from `entities[]` and `audiences[]` in PAP-117: fields to columns, `status` select to kanban option, date range to calendar option, `owner` relation to ownership filter for customers, `searchable` to the search slot.
* Per generated page: `meta` with `generated: entity-pages` and the entity hash, `access` in the PAP-116 format (`customer.*` read own rows via `owner = actor.id`, `staff.*` read and write all, `agent.builder` read), `data` section referencing PAP-119 queries (`list`, `byId`, `create`, `update`, `archive`), `layout.template: app`, `components` using registered ids only (`ui.dataGrid`, `ui.recordHeader`, `ui.fieldList`, `ui.commentThread`, `ui.activityFeed`, `ui.form`), `states` copy from `defaults`, `edgeCases` seeded with empty, huge (10k rows), offline, denied and concurrent edit.
* A `ViewSpec` per list page in `packages/views/src/generated/views.ts` per PAP-161 (`kind: grid`, fields from entity, default sort `updated_at desc`, `visibility: shared`, permissions from the audience), plus kanban and calendar variants when the option fields exist.
* Comment anchors: every detail page declares `comments: { anchor: entity:<type>:<id> }` matching the PAP-131 anchor grammar; every list row carries `data-spec-key` for pins.
* Staff settings pages `settings-members`, `settings-roles`, `settings-branding`, `settings-modules`, `settings-audit`, `settings-api-keys` emitted once from templates in `packages/spec/templates/settings/` (only when the module is enabled, PAP-264).
* Ownership: generated specs are rewritten on every run unless a file has `meta.generated: false`, which detaches it (the two-file rule of PAP-120 applied to specs).

Out: the code generation itself (PAP-120, PAP-119), the landing page and demo seed (default surfaces starter kit), non-CRUD pages, dashboards (PAP-172).

**Spec**

* Deterministic output: same `app.spec.yaml` yields byte-identical specs; keys sorted per the PAP-114 canonical order; `--check` exits 1 on drift (wired into gate 1 alongside PAP-120's drift job).
* Page ids: `<audienceKind>-<entity>-<view>`; routes `/_app/<plural>`, `/_app/<plural>/$id`, `/_app/<plural>/new` and `/_app/<plural>/$id/edit` with the staff surface under `/_staff/...` per PAP-16 route conventions.
* Field to component map lives in `packages/spec/src/codegen/field-components.ts` and is shared with PAP-164 cell renderers; unknown field types render `ui.textField` and warn.
* Customer detail pages hide fields marked `internal: true` in the entity definition; forms omit `computed` and `owner` (set server-side).
* `edgeCases` include the `neverHappen` seeds from the app interview when present.
* Generation of 20 entities times 3 audiences completes in under 5 s.

**Interface contract**

Provides: `generateEntityPages(app: AppSpec, opts): { written: string[], views: ViewSpec[], warnings: Warning[] }` from `@paperos/spec/codegen`, the `field-components.ts` map, and the settings page templates. Consumes: `AppSpec` and `resolvePageSpec` (PAP-117), access section grammar (PAP-116), `ViewSpec` and `FieldDef` (PAP-161), anchor grammar (PAP-131, soft: string format only), component ids from the PAP-74 registry (soft: static list of the six ids until the registry exists). Consumed by: default surfaces starter kit, `paperos gen` pipeline, PAP-125 examples (may replace hand-written list pages), PAP-29.

**Test plan**

* Unit: derivation rules per field type; access output for customer (own rows), staff (all), agent (read); kanban/calendar options only when fields exist.
* Golden: the three canned apps produce snapshot spec trees; snapshots validated with PAP-115 at zero warnings.
* Drift: modify an entity field, run `--check`, expect exit 1 naming the stale file.
* Integration (after PAP-120): generated specs for `clinic-booking` render three routes in Storybook with mocked hooks; conformance tests from PAP-122 pass.

**Definition of done**

* Generator merged; the three canned apps generate and validate with zero warnings; snapshots committed.
* `ViewSpec`s parse with the PAP-161 Zod schema; one kanban and one calendar variant present in the clinic fixture.
* `docs/spec/entity-pages.md` documents the rules and the detach mechanism; CHANGELOG entry; Linear comment with the generated tree for the clinic app.
* Runtime under 5 s for the 60-page stress fixture (timed in CI).

**Edge cases**

* Entity without a `name` field: list uses the first text field, or the id, and warns.
* Two entities with the same plural (`person`/`people`, `staff`/`staff`): route collision fails generation with both ids named.
* Audience with no read grant on any entity: no pages generated, a warning suggests reviewing access.
* Entity relation to an entity the audience may not read: detail shows the relation as an opaque label, never a link; recorded in the access matrix for PAP-64.
* A detached spec (`generated: false`) whose entity was removed: left in place, flagged by the validator as orphaned.

**Dependencies**

Hard: PAP-117, PAP-116, PAP-161. Soft: PAP-131 anchor grammar, PAP-74 component registry, PAP-164 field types, PAP-16 routes. Blocks the default surfaces starter kit and the `paperos gen` pipeline.

**Agent**

Built by Forge (Spec Tooling sub-agent); reviewed by Sentinel (spec-conformance) and Iris for the default component choices.

**Size**

M: one generator with rule tables, settings templates, fixtures.

**Demo**

Screenshot of the generated `specs/pages` tree for the clinic app and one generated list spec side by side with its `app.spec.yaml` entity; Storybook link once PAP-120 lands.
