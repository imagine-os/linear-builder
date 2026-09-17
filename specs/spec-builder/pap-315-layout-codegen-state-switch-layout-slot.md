---
identifier: "PAP-315"
title: "Layout codegen: state switch, layout slot mapping, action binding and search-param schema"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: "PAP-120"
children: []
blockedBy: ["PAP-234", "PAP-314"]
blocks: ["PAP-316"]
key: "spec-builder/layout-codegen/wiring"
url: "https://linear.app/paperos/issue/PAP-315/layout-codegen-state-switch-layout-slot-mapping-action-binding-and"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:25.369Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-315: Layout codegen: state switch, layout slot mapping, action binding and search-param schema

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make generated views behave: a `states` switch driven by data hook status and permission (`loading`, `empty`, `error`, `offline`, `denied`, custom) using the PAP-234 and PAP-71 components, slots mapped to the PAP-16 layout templates through `useLayout()`, component `events` bound to `actions.<name>` from the logic file with `data-action` attributes, and a Zod `validateSearch` schema generated from `search.*` params.

**Scope**

* In: extensions to the view and stories templates, `states` resolver using PAP-119 `dataStates`, slot mapping table, event binding, `validateSearch` emission, `DeniedState` via PAP-59 `useCan('page.view')`, `OfflineBanner` from PAP-18 online status.
* Out: template infrastructure (sibling), example verification (sibling).

**Spec**

* State precedence: `denied` beats all; then `offline` banner overlays; `error`, `loading`, `empty`, then success; custom states are reachable through `logic` flags exposed by the logic file (`useViewState()` hook stub).
* Copy from `states.*.copy` rendered as-is until PAP-375 wraps it; `component?` overrides the default component per state.
* Slots: `layout.template` `app | public | focus | kiosk` maps to PAP-16 shells; `slots` keys validated against the shell's slot names; `kiosk` falls back to `focus` with a warning before PAP-23.
* Events: `events: { onClick: actions.markPaid }` emits `onClick={() => actions.markPaid(ctx)}` and `data-action="markPaid"`; unbound actions fail generation (`SPEC_ACTION_UNBOUND` already caught by PAP-115).
* Search params: every `param: search.<name>` yields a Zod field typed from the contract; `validateSearch` exported to the route file at creation time.
* Stories: one per state with `vi.fn` mocked hooks returning the matching status.

**Interface contract**

* Provides: `data-action` attribute convention (used by PAP-64 permission tests and PAP-122), `useViewState()` stub signature, slot mapping table `layoutSlots.ts`, `validateSearch` emission.
* Consumers: PAP-122 asserts states and `data-spec-key`; PAP-64 clicks `data-action` targets per audience; PAP-131 anchors comments on `data-spec-key`; PAP-83 video flows use `data-action`.
* Requires: templates child, PAP-234 state components, PAP-71 `EmptyState` and `Skeleton`, PAP-16 `useLayout`, PAP-59 `useCan`, PAP-119 `dataStates` (stubs otherwise), PAP-18 online hook.

**Definition of done**

* Snapshot tests for each state and each layout template; event binding and search schema tests.
* Stories for the maximal fixture render every state in Storybook (screenshots at 375 and 1280 px).
* Denied state renders no data hook call (asserted).
* Changelog; Linear comment with story links.

**Test plan**

* Unit: precedence table, slot validation, `data-action` emission, Zod search schema snapshot.
* Integration: Testing Library render of the generated maximal view under each mocked status.
* Visual: Storybook states at 375 and 1280 px, light and dark.

**Demo**

Open the generated stories for `customer-invoices` in Storybook and step through loading, empty, error, offline and denied; toggle the mocked `can` to false and watch `DeniedState` appear with no network calls in the panel. One minute.

**Edge cases**

* Spec omits `states.error`: app defaults (PAP-117 `defaults.states`) fill it.
* Two components bound to one action: allowed; both get `data-action`.
* Search param also a route param: error, ambiguous binding.
* Custom state never set by logic: story exists; runtime unreachable; validator warns `SPEC_STATE_UNREACHABLE`.
* Public page (`public: true`): `useCan` skipped; denied state unreachable and omitted.

**Dependencies**

Blocked by PAP-314, PAP-234. Soft: PAP-119, PAP-16, PAP-59, PAP-18.

**Agent**

Built by Nova with Iris (Component Crafter); reviewed by Sentinel.

**Size**

M
