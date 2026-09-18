---
identifier: "PAP-266"
title: "`paperos create --without`, tenant module toggles and the CI removal matrix"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: "PAP-28"
children: []
blockedBy: ["PAP-22", "PAP-265", "PAP-503", "PAP-912"]
blocks: ["PAP-29", "PAP-126", "PAP-894"]
key: "child/PAP-28/11"
url: "https://linear.app/paperos/issue/PAP-266/paperos-create-without-tenant-module-toggles-and-the-ci-removal-matrix"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:28.009Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-266: `paperos create --without`, tenant module toggles and the CI removal matrix

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let apps omit modules at generation time and tenants toggle optional modules at runtime, with retained data, a Needs Justin gate on purge, and a CI matrix that removes each optional module in turn to prove the template stays green.

**Scope**

In: `--without` in PAP-22 removing module packages and manifest entries; `tenant_module` table and `modules.list|toggle` procedures; settings page `/settings/modules`; runtime 404 and API rejection for disabled modules; `pnpm modules:purge <id>` with production gate; CI matrix workflow; module list written to the Linear project.

Out: entitlement pricing (PAP-178).

**Spec**

* Toggle checks `dependsOn`; blocked with the dependency list in UI and API.
* Disabled at runtime: route returns not-found, nav item hidden, procedures return `MODULE_DISABLED`; data untouched.
* Purge requires `--tenant` and, in production, a Needs Justin issue link.

**Interface contract**

Provides: `tenant_module` table, `modules.*` procedures, `useModuleEnabled(id)`, settings page, CLI flag. Consumes: children 1 and 2, PAP-22, PAP-59 for the settings page permission.

**Definition of done**

* `paperos create demo --without payroll,crm,growth` builds and shows no CRM or payroll navigation (screenshots).
* CI matrix green for every optional module.
* Playwright: admin disables `canvas`, route 404s, API rejects, re-enable restores data; customer cannot open the settings page.

**Test plan**

* Unit: toggle dependency check; purge guard.
* Integration: `modules.toggle` as admin and as customer via `callAs`.
* E2E: Playwright toggle flow at 375 and 1280.
* CI: matrix job per optional module running `pnpm check`.

**Demo**

Reviewer opens Settings, Modules, switches Canvas off, sees the nav item vanish and `/canvas` show not-found, switches it back on and the data is intact. Under 90 seconds.

**Edge cases**

* Tenant disables a module a business template requires: importer refuses or prompts.
* Two admins toggle concurrently: last write wins with an audit event.

**Dependencies**

Children 1 and 2 (hard), PAP-22. Feeds PAP-29, PAP-207.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-846 (wire) (new, phase 2) would block this issue but sits in a later milestone (2026-10-16 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-861 (wire) (new, phase 2) would block this issue but sits in a later milestone (2026-10-16 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-876 (wire) (new, phase 2) would block this issue but sits in a later milestone (2026-10-16 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-892 (wire) (new, phase 2) would block this issue but sits in a later milestone (2026-10-16 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-907 (wire) (new, phase 2) would block this issue but sits in a later milestone (2026-10-16 > 2026-09-29); no `blocks` relation was created. Build against its interface and reconcile when it lands.

*Round 4 (2026-09-18): PAP-471 soft: the pm-linear wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-471 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-471 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-480 soft: the collab wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-480 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-480 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-481 soft: the realtime wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-481 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-481 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-482 soft: the input wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-482 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-482 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-489 soft: the tables wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-489 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-489 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-490 soft: the business-core wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-490 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-490 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-491 soft: the growth wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-491 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-491 -> PAP-266 was removed.*

*Round 4 (2026-09-18): PAP-496 soft: the migration wire issue lands (09-30/10-01) after the* `--without` *milestone (09-29); until it lands, PAP-266's removal matrix covers modules whose wire issue has merged; PAP-496 adds its module to the matrix and to* `paperos create --without` *when it lands. The* `blocks` *relation PAP-496 -> PAP-266 was removed.*

**Agent**

Built by Forge with Iris on the settings page. Reviewed by Sentinel.

**Size**

M
