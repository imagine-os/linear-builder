---
identifier: "PAP-614"
title: "View renderer registry and ViewHost: registerViewKind, one <ViewHost spec /> that renders any kind, kind switcher and per-kind options panel"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-341"]
blocks: ["PAP-102", "PAP-167", "PAP-169", "PAP-170", "PAP-172", "PAP-189", "PAP-386", "PAP-619", "PAP-621", "PAP-623", "PAP-631"]
key: "r4/tables/view-renderer-registry-and-host"
url: "https://linear.app/paperos/issue/PAP-614/view-renderer-registry-and-viewhost-registerviewkind-one-viewhost-spec"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:40.955Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-614: View renderer registry and ViewHost: registerViewKind, one <ViewHost spec /> that renders any kind, kind switcher and per-kind options panel

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Build the runtime half of the `ViewRendererRegistry` that `@paperos/contract-tables` (PAP-483) declares: `registerViewKind()` so each view issue plugs in without touching a switch statement, a single `<ViewHost spec onSpecChange />` that dashboards, page specs, PM boards and CRM render through, a kind switcher ("Show as grid | kanban | calendar ...") and a generic options panel driven by each kind's Zod options schema.

**Scope**

In: `packages/views/src/host/{registry,ViewHost,KindSwitcher,OptionsPanel,fallback}.tsx`; `registerViewKind({ kind, label, icon, component, optionsSchema, requiredFieldTypes, supports: { groups, aggregates, onFilter, embedded, print } })`; `getViewKind(kind)`; `ViewHost` embedded and full modes; `UnknownKindFallback`; `docs/views/adding-a-view-kind.md`.

Out: the view components themselves (PAP-165 to PAP-170), saved-view CRUD and switcher of saved views (PAP-172), dashboard block chrome (PAP-386).

**Spec**

* Registry is a module-level map filled at boot by each view package's `register.ts`; duplicate kind ids throw; `kernel` binding in PAP-489 exposes the same map through the contract port so other modules never import `packages/views`.
* `<ViewHost spec datasetRef mode='full'|'embedded' onSpecChange onFilter? toolbarSlot? />` resolves the kind, validates `spec.options` against `optionsSchema` (invalid options fall back to defaults with a dev warning), lazy-loads the component chunk, and renders `EmptyState`, `LoadingPage` and `ErrorState` (PAP-71, PAP-234) around it.
* `KindSwitcher` lists registered kinds whose `requiredFieldTypes` the dataset satisfies (calendar needs a `date`, kanban a `select|user|relation limitOne`, map a `geo`); switching converts the spec with `convertViewKind(spec, toKind)` keeping filter, sorts and field visibility, dropping incompatible options with a toast listing them.
* `OptionsPanel` renders form controls from the kind's Zod schema (`z.enum` to Select, `fieldId` refinements to a field picker filtered by type) through PAP-233 form adapters; kinds may override with a custom panel.
* Commands `view.kind.<kind>` and `view.options.open` registered in PAP-151; the host emits `view.rendered { kind, datasetRef, rows, ms }` telemetry (PAP-40).

**Interface contract**

Provides: `registerViewKind`, `getViewKind`, `listViewKinds(dataset)`, `<ViewHost />`, `<KindSwitcher />`, `<OptionsPanel />`, `convertViewKind`, `ViewKindDefinition` type (mirrors the contract), telemetry topic `view.rendered`. Consumes: `ViewSpec`, `viewSpecSchema` and fixtures (PAP-161), `GridView` as the first registered kind (PAP-341), field type registry for `requiredFieldTypes` (PAP-338), state components (PAP-71, PAP-234), form adapters (PAP-233), commands (PAP-151). Consumed by PAP-167, PAP-168, PAP-169, PAP-170 (each registers), PAP-386 blocks, PAP-172 switcher, PAP-119 inline views, PAP-102 PM boards, PAP-189 CRM views.

**Definition of done**

* Grid registered through the registry and `/demo/grid` renders via `ViewHost` with no direct `GridView` import outside `packages/views`.
* Storybook `views/host` shows the ten kinds (registered ones live, unregistered ones as the fallback tile); screenshots at 375, 1024, 1920 in three themes; axe clean.
* `docs/views/adding-a-view-kind.md` walks through registering a kind in under 40 lines; CHANGELOG; Linear comment on PAP-167, PAP-169, PAP-170 asking them to register instead of exporting.

**Test plan**

* Unit: registry duplicate and unknown kind; `listViewKinds` filtering by dataset field types; `convertViewKind` for every kind pair on the ten fixtures (filter and sorts preserved, incompatible options reported); options fallback on invalid options.
* Integration: PM `issue` entity dataset renders grid and kanban through `ViewHost` with `spec.kind` switched at runtime; embedded mode inside a 300 px container hides the toolbar.
* E2E: switch `/demo/grid` to kanban from the switcher, change an option in the panel, reload and see both persisted through `onSpecChange`; keyboard-only run of the same.

**Demo**

Reviewer opens `/demo/grid`, presses `mod+k`, runs "Show as kanban", opens the options panel to pick the group field, then switches back to grid and sees filters intact. Under two minutes.

**Edge cases**

* Kind registered after first render (lazy module): host re-renders on the registry's change event, no page reload.
* Dataset loses the field a kind requires (field archived): switcher greys the kind with the reason; open views of that kind render the fallback with "pick another field".

**Dependencies**

PAP-161 (hard, fixtures and schema), PAP-341 (hard, first kind). Soft: PAP-338, PAP-233, PAP-234, PAP-151. Blocks PAP-167, PAP-169, PAP-170, PAP-386, PAP-172, PAP-102, PAP-189 (they register kinds or render through the host).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

M: one session.
