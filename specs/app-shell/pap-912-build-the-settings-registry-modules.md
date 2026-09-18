---
identifier: "PAP-912"
title: "Build the settings registry: modules declare settings sections and schemas in their manifests, the shell generates tenant, workspace and user settings pages with permissions, audit and search"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-59", "PAP-229", "PAP-264", "PAP-447"]
blocks: ["PAP-266"]
key: "r4/app-shell/settings-registry"
url: "https://linear.app/paperos/issue/PAP-912/build-the-settings-registry-modules-declare-settings-sections-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:43.804Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-912: Build the settings registry: modules declare settings sections and schemas in their manifests, the shell generates tenant, workspace and user settings pages with permissions, audit and search

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Stop every module from hand-building its settings page: manifests declare `settings.sections[]` with a Zod schema, scope (tenant, workspace, user), permission and UI hints; the shell fills `shell.settings.sections` (PAP-447) with generated forms (PAP-124 form-from-schema patterns), stores values in `settings` tables per scope with RLS, audits changes (PAP-38), exposes `useSetting(key)` with live updates, and makes settings searchable from the command palette.

**Scope**

In: Manifest extension `settings: [{ id, scope, schema, permission, group, order, secret?: string[] }]` validated by PAP-433; tables `tenant_setting`, `workspace_setting`, `user_setting` (`module`, `key`, `value jsonb`, versioned); `settings.get|set` procedures with schema validation and permission checks; `useSetting`, `useSettings(module)` hooks with Electric live updates (PAP-326). Generated pages `/settings`, `/console/settings/:section`, `/portal/settings/:section` with the PAP-233 adapters, secret fields via the secrets port (PAP-444) never echoed, search registration (PAP-39) of section titles and field labels, deep links from the help panel. Migration of existing hand-built settings (PAP-63's settings page, PAP-58 org settings, PAP-27 locale, PAP-75 branding) to registry declarations with an ADR.

Out: Platform admin settings (platform-ops console). Per-record settings.

**Spec**

* Precedence user > workspace > tenant > manifest default, resolved server-side; a section may forbid lower-scope overrides
* Every `set` writes an audit row with before and after (secrets redacted); a `settings.changed` event carries module and key
* Schema changes are versioned with upcasters (PAP-436 pattern) so stored values migrate on read

**Interface contract**

Provides: settings manifest extension, tables and procedures, hooks, generated settings pages, search registration, `settings.changed` event. Consumes: module manifests (PAP-264, PAP-433), settings slot (PAP-447), console and portal shells (PAP-63, PAP-62), permission engine (PAP-59), audit (PAP-38), form patterns (PAP-124, PAP-233), secrets port (PAP-444), live reads (PAP-326), search (PAP-39). Consumed by: every module (assistant, engagement, commerce, workflows and platform-ops all declare settings), PAP-266 module toggles (as a section), PAP-367 onboarding (writes settings).

**Definition of done**

* Three existing settings pages migrated to declarations with identical behaviour; a new module adds a section by manifest only; precedence and audit tested; search finds a setting from the palette
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: precedence; schema validation; upcaster.
* E2E: edit at tenant then override at user; secret never echoed; deep link from help panel.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Add a `bookingReminderHours` setting to the engagement manifest, reload, find it from the command palette, change it at tenant scope and see the audit row.

**Edge cases**

* Module disabled: its sections hide but stored values persist for re-enable
* Invalid stored value after a schema change without an upcaster: page shows the default with a repair notice
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-264, PAP-447, PAP-433 (hard), PAP-63, PAP-59, PAP-38 (hard), PAP-124, PAP-233, PAP-444, PAP-326, PAP-39 (soft).

* Soft dependency (round 4): PAP-63 is a soft dependency, not a `blocks` relation, because its milestone (2026-09-30) is later than this issue's (2026-09-29); build against its interface and reconcile when it lands.
* Soft dependency (round 4): PAP-124 is a soft dependency, not a `blocks` relation, because its milestone (2026-09-30) is later than this issue's (2026-09-29); build against its interface and reconcile when it lands.
  **Agent**

Builder: Forge. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
