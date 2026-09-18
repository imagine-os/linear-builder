---
identifier: "PAP-669"
title: "Density modes: compact, default and comfortable as a runtime setting with density tokens for control heights, spacing and row heights, applied by every component"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66", "PAP-72", "PAP-238"]
blocks: ["PAP-76"]
key: "r4/design-system/density-modes"
url: "https://linear.app/paperos/issue/PAP-669/density-modes-compact-default-and-comfortable-as-a-runtime-setting"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:28.093Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-669: Density modes: compact, default and comfortable as a runtime setting with density tokens for control heights, spacing and row heights, applied by every component

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Linear, Gmail and Atlassian let users pick a density; PAP-71's cells and PAP-165's grid each take a `density` prop, but there is no global setting and no token layer, so a compact grid sits inside a comfortable form. Define density as tokens and a user setting every component honours.

**Scope**

In: `packages/ui/tokens/density.tokens.json` (`control.height.{sm,md,lg}`, `space.inline`, `space.stack`, `row.height`, `font.size.body` per mode); `data-density` attribute contract and `DensityProvider` with `pos.settings.density` persisted per user; component updates to read density tokens instead of fixed sizes; Storybook toolbar global; `SettingRow` for PAP-62 and PAP-63 settings.

Out: per-view row height (PAP-165 keeps it, defaulting from the density), per-tenant density defaults (v0.2), typography scale (a11y font scale is separate).

**Spec**

* Modes `compact|default|comfortable` map control heights to 28/32/36, 32/40/48 and 36/44/52 px, stack spacing 8/12/16, inline 6/8/12, body 13/14/15 px; coarse pointers force a 44 px minimum hit area regardless of mode (`@media (pointer: coarse)`), so compact on touch changes spacing, not targets.
* Tokens compile through PAP-66's build into `--pos-density-*` variables redefined under `[data-density="compact"]` and `[data-density="comfortable"]`; components reference `var(--pos-control-height-md)` instead of literal rem sizes (PAP-236, PAP-238, PAP-70, data display and surfaces updated in this issue).
* `DensityProvider` reads the user setting (PAP-33 `user_preferences.density`, synced via PAP-143), applies `data-density` on `<html>` (or a subtree via `scope`), exposes `useDensity()`; grid and cells default their `density` prop from it; the Storybook toolbar sets the same attribute.
* Motion durations shorten by 20 percent in compact (PAP-72 reads `useDensity`); illustrations shrink one size in compact `EmptyState`.
* Visual regression: Gate 3 (PAP-82) adds density to its matrix for the component gallery only, not every page.

**Interface contract**

Provides: density tokens and CSS variables, `DensityProvider`, `useDensity()`, `data-density` contract, `pos.settings.density` key, `DensitySettingRow`. Consumes: token build (PAP-66), components to update (PAP-236, PAP-238, PAP-70, PAP-71 children, surfaces), motion (PAP-72), preferences and sync (PAP-33, PAP-143, soft), Storybook toolbar (PAP-69). Consumed by PAP-341 default row height, PAP-76 density guideline page, PAP-62 and PAP-63 settings.

**Definition of done**

* Tokens merged and every core component renders correctly in three densities (gallery story screenshots at 375 and 1280 in three densities and two themes); touch minimum proven with the PAP-154 audit under `pointer: coarse` in compact.
* `docs/design/density.md`; changelog; Linear comment on PAP-341 and PAP-76.

**Test plan**

* Unit: token resolution per mode; provider persistence with a throwing `localStorage`; coarse-pointer override; scope attribute on a subtree.
* Visual: gallery at three densities; axe target-size rule under coarse pointer in compact.
* E2E: switch density in settings, reload, confirm the grid row height and form controls changed together.

**Demo**

Reviewer switches the Storybook density toolbar through the three modes on the All components story, then changes the setting in the template app and sees the grid and a settings form tighten together. Under one minute.

**Edge cases**

* Component with a hard-coded height left behind: lint rule `no-raw-control-height` (design lint issue) catches it.
* Density scope inside a scope: innermost wins.
* Compact on a phone: targets stay 44 px, spacing tightens.
* Print: default density forced.

**Dependencies**

PAP-66 (hard), PAP-238 (hard, components complete), PAP-72 (hard, motion hook). Soft: PAP-33, PAP-143, PAP-69, PAP-82. Blocks PAP-76 density page.

**Agent**

Builder: Iris (Token Keeper). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
