---
identifier: "PAP-538"
title: "`/settings/modules` staff page: bound implementations per module, tenant overrides, shadow toggle and diff counts, kill switch with reason and the audit trail"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-59", "PAP-229", "PAP-236", "PAP-434", "PAP-435", "PAP-537", "PAP-541"]
blocks: ["PAP-442", "PAP-453", "PAP-454", "PAP-455", "PAP-458", "PAP-461", "PAP-464", "PAP-471", "PAP-472", "PAP-473", "PAP-480", "PAP-481", "PAP-482", "PAP-489", "PAP-490", "PAP-491", "PAP-496", "PAP-497", "PAP-539", "PAP-549"]
key: "r4/module-system/modules-settings-page"
url: "https://linear.app/paperos/issue/PAP-538/settingsmodules-staff-page-bound-implementations-per-module-tenant"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-538: `/settings/modules` staff page: bound implementations per module, tenant overrides, shadow toggle and diff counts, kill switch with reason and the audit trail

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-435 builds the selection hook, shadow diffs and headers; the staff page that operates a swap is UI work that Iris can build in parallel and that shares components with the flags page (PAP-501). PAP-266 also puts module enable and disable on this route, so one page owns "modules" for staff.

**Scope**

In:

* Spec `specs/pages/staff/settings-modules.spec.yaml` (`access: [staff.owner, agent.atlas]`), route `/settings/modules` in the `shell.settings.sections` slot; tabs `Enabled` (PAP-266 toggles) and `Implementations` (this issue).
* Components: `ModuleTable` (module, kind, swap risk, bound impls, default, tenant override, shadow state, diff count last 24 h), `ImplPicker` (per tenant, writes the `module.<id>.impl` rule through `flags.update`), `ShadowToggle`, `KillSwitch` (reused), `DiffDrawer` listing `swap_shadow_diff` rows by case id with a JSON diff view.
* Procedures used: `modules.list` (PAP-266), `modules.shadowDiffs` and `paperos module status` data (PAP-435), `flags.update|kill` (PAP-366); audit events (PAP-38) shown per module.

Out: the selection mechanism and diff table (PAP-435), enable and disable semantics (PAP-266), the swap CLI (PAP-442).

**Spec**

* Every change requires `can(actor, "module:impl:force")` and a reason; customers get `DeniedState`.
* Choosing an impl that is bound but not declared in `flags.yaml` is refused with the generator command to run.
* Diff drawer normalises with the conformance normaliser so case ids match the CLI output.
* Page works with 18 modules and 100k diff rows (server-side paging).

**Interface contract**

Provides: route `/settings/modules`, `ModuleTable`, `ImplPicker`, `DiffDrawer`; consumed by PAP-266 (its toggles live in the `Enabled` tab), PAP-442 (links to the page in evidence), PAP-446 (canary flip through the UI), PAP-453 demo.

Consumes: `can` (PAP-59), primitives (PAP-236, PAP-238), flags procedures (PAP-366), shadow diff data (PAP-435 sibling), module list (PAP-266), audit (PAP-38).

**Definition of done**

* Playwright: staff sets `tables` to `compiler-v2` for one tenant with shadow on, sees `X-PaperOS-Impl` change on a view request and the diff count update; kill switch returns default (recording).
* Screenshots at 375, 768, 1280, 1920 light and dark; axe clean; Storybook stories; CHANGELOG; Linear comment.

**Test plan**

* Unit: table state reducers; refusal of undeclared impl; diff drawer paging.
* E2E: flip, shadow, kill; `callAs(customer)` denied.

**Demo**

Reviewer opens `/settings/modules`, switches the demo tenant's `app-shell` to `minimal` with shadow on, watches the diff count stay at zero, then hits Kill and the full shell returns within five seconds. Ninety seconds.

**Edge cases**

* Module disabled for the tenant (PAP-266): implementation row greyed with the reason.
* Impl unbound after an override was set: warning badge and one-click reset (PAP-435 rule).
* Two staff edit concurrently: last write wins, both audit rows visible.

**Dependencies**

Hard: PAP-59, PAP-236. Sibling: PAP-435 mechanism. Soft: PAP-266, PAP-366, PAP-38, PAP-238.

**Agent**

Builder: Iris (Component Crafter) with Forge on procedures. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/flags-settings-page` = PAP-501.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-435 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-435 blocks this issue (`blocks` relation).
