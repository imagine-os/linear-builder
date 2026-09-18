---
identifier: "PAP-744"
title: "Compile `flags` and `modules` sections: route guards through the flag service, `MODULE_DISABLED` handling in codegen, flag-gated nodes on the flow graph"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-315", "PAP-740"]
blocks: []
key: "r4/spec-builder/flags-modules-compile"
url: "https://linear.app/paperos/issue/PAP-744/compile-flags-and-modules-sections-route-guards-through-the-flag"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:35.044Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-26"
cycle: null
---

# PAP-744: Compile `flags` and `modules` sections: route guards through the flag service, `MODULE_DISABLED` handling in codegen, flag-gated nodes on the flow graph

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-366 promises a `flags:` guard in page specs and PAP-88 wants risky pages behind flags; PAP-265 rejects specs referencing disabled modules at validate time but nothing handles a module disabled at runtime for one tenant. Compile the two v1.1 sections into route guards, generated states and graph annotations so a flag flip or a module toggle changes what renders without code.

**Scope**

In: extension of PAP-315's state switch with `flagged` (renders `fallback` route redirect or `DeniedState` variant `ui.featureUnavailable`) and `moduleDisabled` (renders PAP-234 `IntegrationUnavailable` styled for modules); `useFlags(page.flags)` from PAP-366 in the generated view; route `beforeLoad` guard emitted into the route file at creation; `flags[]` on `FlowGraph` nodes (PAP-123 already reserves the field) and a `flag` filter in PAP-322's toolbar; `docs/spec/flags.md`. Out: the flag service (PAP-366), tenant module toggles (PAP-266), navigation hiding (PAP-117 `gen:app` already filters through `useCan`; extend with `useFlags` here).

**Spec**

* Guard order in the generated view: `denied` (access), then `moduleDisabled` (PAP-266 `tenant_module`), then `flagged`, then the PAP-315 states; navigation items for flagged pages hide unless the flag holds (`gen:app` navigation gains a `flags` field).
* `flags.require` all must hold, `flags.any` at least one; evaluation is server-side through PAP-366's streamed values with a 5 s propagation budget; missing flag service means `fallback`.
* Conformance tests (PAP-122) gain a `flagged` state assertion when the section exists; PAP-64's permission matrix records flag-gated actions as `conditional`.
* Flow graph nodes with `flags` render a flag badge (PAP-320) and can be hidden by the toolbar filter; `paperos gen --check` fails when a spec references an undeclared flag (`FLAG_UNKNOWN` from the schema issue).
* Kill switch (`module.<id>.impl` family is reserved by PAP-435; page flags live under `page.<id>.*`) never collides: validator rule `FLAG_RESERVED_FAMILY`.

**Interface contract**

Provides: generated guard code, `ui.featureUnavailable` state wiring (component owned by PAP-234, requested by comment), navigation `flags` field, graph badge, rule `FLAG_RESERVED_FAMILY`. Consumes: v1.1 schema, PAP-315 state switch, PAP-366 `useFlags` and server evaluation, PAP-266 `tenant_module`, PAP-234 state components, PAP-123 and PAP-320 graph types, PAP-122 generated tests. Consumed by: PAP-88 release train (flagged pages), PAP-195 in-app targeting, PAP-363 starter kit (optional surfaces).

**Definition of done**

* Clinic fixture page `payments-report` behind `page.payments.report`: hidden from navigation and redirected while off, renders when on, for one tenant only; `appointments` page with `modules.require: [scheduling]` shows the module-disabled state when the tenant toggles it off.
* Storybook stories for both states at 375 and 1280 in light and dark; conformance test asserts the flagged state; `docs/spec/flags.md`; CHANGELOG entry.

**Test plan**

* Unit: guard order, `require` vs `any`, fallback when the service is down, navigation filtering, reserved family rule.
* Integration: flip a flag through PAP-366's API and observe the generated route within 5 s (compose stack).
* E2E (Playwright): two tenants, flag on for one, navigate as each.

**Demo**

Set `flags: { require: ['page.payments.report'] }` on a page, regenerate, load it (redirected), flip the flag in `/_app/settings/flags`, reload and see it. Under two minutes.

**Edge cases**

* Flag on but module disabled: module state wins (order rule).
* Public page with flags: evaluated for anonymous with tenant-level rules only.
* Flag deleted while pages reference it: `--check` red and a banner in the spec editor.

**Dependencies**

Hard: PAP-740, PAP-315. Soft: PAP-366, PAP-266, PAP-234, PAP-123, PAP-320, PAP-322, PAP-122.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/spec-builder/schema-v1-1-extensions` = PAP-740.
