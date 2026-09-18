---
identifier: "PAP-623"
title: "Saved views: views.* CRUD, personal vs shared visibility, ViewSwitcher, per-audience defaults and view locking"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-172"
children: []
blockedBy: ["PAP-59", "PAP-62", "PAP-165", "PAP-229", "PAP-343", "PAP-558", "PAP-585", "PAP-614", "PAP-618", "PAP-630"]
blocks: ["PAP-385", "PAP-624"]
key: "r4/tables/saved-views-switcher-and-audience-defaults"
url: "https://linear.app/paperos/issue/PAP-623/saved-views-views-crud-personal-vs-shared-visibility-viewswitcher-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:18.744Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-623: Saved views: views.* CRUD, personal vs shared visibility, ViewSwitcher, per-audience defaults and view locking

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-172 and the part PAP-173 waits on: views as permissioned, persisted objects. CRUD procedures, personal versus shared visibility, the switcher that lists what the actor may see, per-audience defaults per dataset and view locking. Public links move to the sibling so this can land without the security review gating it.

**Scope**

In: table `view_default`; procedures `views.list|create|update|duplicate|delete|reorder|setDefault|resolveDefault|lock`; `ViewSwitcher`, `ViewSettingsSheet`; permission actions `view.read|update|delete|lock`; commands `view.switch|new|duplicate`; `page.spec.yaml` `views.default` pin.

Out: public tokens, `/v/:token`, embeds and passwords (sibling), per-field permissions (PAP-59 and PAP-638).

**Spec**

* `visibility`: `personal` (owner only), `shared` (workspace policies via `can()`), `public` reserved for the sibling. New views are personal; making shared requires `view.share`; `view` rows use PAP-161's table with `position` fractional index.
* `view_default (tenant_id, dataset_ref jsonb, audience_id, view_id, position)`; `resolveDefault(datasetRef, actor)` picks the most specific matching audience (PAP-62 segments), else the first shared view by position, else a fresh personal grid; `page.spec.yaml` `views.default: <viewId|slug>` pins one for a page.
* `locked: true` blocks `spec` changes except for `view.lock` holders; temporary URL filters (`useTempViewState`) still work; the toolbar shows a lock chip with the reason.
* `ViewSwitcher` groups "Your views / Shared / Public", search, drag reorder (PAP-329), rename inline, icon per kind from the registry; `mod+shift+v` opens it; `views.duplicate` copies the spec into a personal view.
* Owner leaves the tenant (membership removed event, PAP-58): personal views deleted, shared views transferred to the workspace owner by a PAP-43 job; audit events `view.default.changed`, `view.locked`.
* Permission matrix for the four actions generated through PAP-63's matrix generator.

**Interface contract**

Provides: procedures above, `<ViewSwitcher datasetRef />`, `<ViewSettingsSheet viewId />`, `resolveDefault`, `useCurrentView()`, commands, audit topics, `ViewDefault` type. Consumes: grid host and toolbar (PAP-343, PAP-618), `can()` and `useCan` (PAP-229), audiences (PAP-62), audit (PAP-38), drag (PAP-329), jobs (PAP-43), `ViewHost` registry for icons. Consumed by PAP-385 dashboards, PAP-183 saved reports, PAP-189 per-audience CRM defaults, the public sibling.

**Definition of done**

* Vitest, integration and Playwright green; permission matrix committed; stories at 375, 768, 1024, 1440, 1920 in three themes; axe clean.
* `docs/views/saved-views.md`; CHANGELOG; Linear comment with demo.

**Test plan**

* Unit: default resolution precedence (specific audience beats general beats first shared beats fresh); lock semantics; reorder positions; duplicate naming ("Copy of").
* Integration: `callAs(member)` cannot update a shared view without `view.update`; membership removal transfers shared views and deletes personal ones; RLS harness on `view_default`.
* E2E: create a personal view, share it, set it as the default for the customer audience, sign in as a customer and land on it, lock it and try to change a filter as staff (temporary only); keyboard-only run; 375 px sheet.

**Demo**

Reviewer creates "Open tasks" from the demo grid, shares it, sets it as default for the Customer audience, then opens the portal as the demo customer and lands on it. Under two minutes.

**Edge cases**

* Two audiences match: most specific wins, ties by `position`.
* Default points at a deleted view: falls back to the next rule and self-heals the row.
* Page-spec pin references a personal view: validator error in PAP-115.
* Rename to an existing name: allowed, slug uniquified.

**Dependencies**

PAP-343 (hard), PAP-229 (hard), PAP-62 (hard, audiences), PAP-618 (hard, Share and Views slots). Soft: PAP-38, PAP-43, PAP-329. Blocks PAP-385 and the public sibling; PAP-183 and PAP-189 consume it softly (their milestones are earlier).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/field-level-permissions` = PAP-638, `r4/tables/view-toolbar-sort-group-aggregates` = PAP-618.
