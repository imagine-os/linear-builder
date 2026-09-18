---
identifier: "PAP-553"
title: "Auto-generated module settings forms from `settingsSchema` at `/settings/modules/<id>`: Zod to form fields, tenant scope, validation, secret-name display and audit"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-236", "PAP-444"]
blocks: []
key: "r4/module-system/module-settings-ui"
url: "https://linear.app/paperos/issue/PAP-553/auto-generated-module-settings-forms-from-settingsschema-at"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:06.521Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-10-01"
cycle: null
---

# PAP-553: Auto-generated module settings forms from `settingsSchema` at `/settings/modules/<id>`: Zod to form fields, tenant scope, validation, secret-name display and audit

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Every module declares `settingsSchema` (PAP-264) and PAP-444 validates it at boot, but staff have no way to set a module's tenant-level settings without a bespoke page. Backstage and Terraform render forms from schema; with eighteen modules and more coming, a generated form is the only way settings stay complete and consistent.

**Scope**

In:

* Route `/settings/modules/<id>` (child of PAP-538) rendering a form from the module's `settingsSchema` through a Zod-to-fields mapper: strings, numbers, booleans, enums, arrays of primitives, nested objects as sections; `.describe()` as help text; PAP-233 pickers for dates.
* Storage: tenant-scoped values in `tenant_module_settings` (`tenant_id`, `module_id`, `values jsonb`, `updated_by`) with RLS; `ConfigPort.get(module)` (PAP-444) merges tenant values over app defaults per request scope.
* Secrets: fields declared in `secrets` show the secret name and `set|not set` status only (PAP-444 masking), with a link to the broker runbook; never an input.
* Validation server-side with the same schema; audit event per change (PAP-38); `can(actor, "module:settings")`.

Out: app-level defaults (`app.spec.yaml`), secrets entry (PAP-300 broker), per-user preferences.

**Spec**

* Form covers every Zod kind the sample and template modules use; unsupported kinds render a JSON editor fallback with validation.
* Saving a value that would fail another module's boot validation is refused with the module and field named.
* Changes propagate to request scopes immediately (no restart), through the PAP-444 port cache invalidation on `module.settings.changed`.

**Interface contract**

Provides: route, `SchemaForm` component (reusable by PAP-124 spec editor forms), `tenant_module_settings` table, topic `module.settings.changed`; consumed by PAP-444 (tenant layer), PAP-266 (module page), business-core and growth modules for provider settings, PAP-124.

Consumes: config port and validation (PAP-444), form primitives (PAP-236, PAP-233), audit (PAP-38), `can` (PAP-59), kernel request scope.

**Definition of done**

* Sample module settings edited for one tenant and reflected in a request within a second; another tenant unchanged (test); invalid value refused with field error.
* Screenshots at 375 and 1280 for three module schemas; a11y clean; `docs/platform/config.md` tenant section; Linear comment.

**Test plan**

* Unit: Zod-to-fields mapper per kind; merge order defaults then tenant; refusal on cross-module boot validation.
* E2E: Playwright edits a setting, asserts the API response reflects it, customer denied.

**Demo**

Reviewer opens `/settings/modules/business-core`, sees the Stripe secret as `set`, changes the invoice numbering prefix, saves, and the next invoice preview uses it. Under a minute.

**Edge cases**

* Schema changes in a module upgrade: stored values re-validated on load; invalid ones shown with a migration hint, not dropped.
* Very large arrays: paginated editor with import from CSV.
* Module disabled for the tenant: page read-only with the PAP-266 toggle link.

**Dependencies**

Hard: PAP-444, PAP-236. Soft: PAP-233, PAP-38, PAP-59, PAP-266, PAP-538.

**Agent**

Builder: Iris (Component Crafter) with Forge on storage. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/module-system/modules-settings-page` = PAP-538.
