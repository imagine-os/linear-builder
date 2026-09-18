---
identifier: "PAP-549"
title: "Kernel devtools: `/dev/modules` page with the dependency graph, bindings and scopes, a slot overlay highlighting fills by module, topic flow and flag state, plus `paperos module explain <port>`"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-434", "PAP-435", "PAP-438", "PAP-537", "PAP-538"]
blocks: []
key: "r4/module-system/kernel-devtools"
url: "https://linear.app/paperos/issue/PAP-549/kernel-devtools-devmodules-page-with-the-dependency-graph-bindings-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:05.447Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-549: Kernel devtools: `/dev/modules` page with the dependency graph, bindings and scopes, a slot overlay highlighting fills by module, topic flow and flag state, plus `paperos module explain <port>`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

React DevTools shows the component tree; nothing shows the module tree. A session debugging "why does this nav item come from CRM" or "which impl answered this request" today reads manifests by hand. PAP-435 gives staff `/settings/modules`; developers and agents need the inspector view: graph, bindings, slot fills in place, events flowing, flags evaluated, all from `kernel.describe()`.

**Scope**

In:

* Route `/dev/modules` (`access: [developer, agent]`, dev and preview only, hidden in production): dependency graph (from `dependency-map.json`, PAP-439) with live binding state, module cards (kind, risk, impl, health, boot time), a request inspector reading `X-PaperOS-Impl` and the last 50 port calls (PAP-547 ring buffer), topic flow (last events per topic from the outbox, PAP-436).
* Slot overlay: `Ctrl+Shift+M` toggles outlines around every rendered slot fill with `module:slot:order` labels and a click-through to the manifest line (mirrors PAP-438 registration data).
* Flag panel: `module.*.impl` evaluation trace for the current scope (kill, tenant, audience, default) from PAP-366 `explain`.
* CLI `paperos module explain <contract>.<port>`: prints providers, current default, consumers with the ports they use, conformance status and the last shadow diff count.

Out: staff operations page (PAP-538), generated docs (PAP-445), production telemetry.

**Spec**

* The page reads only `kernel.describe()`, the dependency map and telemetry buffers; it never resolves ports itself.
* Overlay adds no DOM to production bundles (tree-shaken behind `import.meta.env.DEV || PUBLIC_ENV=preview`).
* Graph renders 18 modules and 60 edges in under 200 ms using the PAP-132 canvas primitives when available, SVG fallback otherwise.
* Agent access through the API: `GET /api/dev/modules` returns the same JSON for sessions without a browser.

**Interface contract**

Provides: route `/dev/modules`, `GET /api/dev/modules`, slot overlay, `paperos module explain`; consumed by builder sessions (PAP-92 playbook debugging section), PAP-446 (drill evidence screenshots), PAP-24 guide, Sentinel reviewers.

Consumes: `kernel.describe()` (PAP-434), slot registry (PAP-438), flag evaluation and headers (PAP-435, PAP-366), dependency map (PAP-439), outbox (PAP-436, soft), canvas primitives (PAP-132, soft).

**Definition of done**

* Page renders the template graph with bindings; overlay labels every fill on the dashboard; `explain` output for `ViewQueryPort` matches the matrix (screenshots at 1280 and 1920).
* Production build contains no devtools code (bundle grep); `docs/platform/devtools.md`; Linear comment.

**Test plan**

* Unit: graph data builder from describe and map; overlay label composition; explain formatter.
* E2E: Playwright in preview: open `/dev/modules`, toggle overlay, assert labels; production build 404s the route.

**Demo**

Reviewer opens `/dev/modules` on the preview, clicks `tables`, sees `compiler-v2` bound for the demo tenant, presses `Ctrl+Shift+M` on the dashboard and every block shows its `module:slot` label. Under a minute.

**Edge cases**

* Kernel failed to boot partially (dev banner, PAP-434): the page still renders with the failed module in red and the error.
* Hundreds of port calls per second: ring buffer bounded at 50, sampled.
* Multi-window (PAP-262): each window shows its own kernel; the page notes the window label.

**Dependencies**

Hard: PAP-434, PAP-438, PAP-435. Soft: PAP-439, PAP-436, PAP-366, PAP-132, PAP-547.

**Agent**

Builder: Forge (Platform Engineer) with Iris on the overlay. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/module-system/kernel-otel` = PAP-547, `r4/module-system/modules-settings-page` = PAP-538.
