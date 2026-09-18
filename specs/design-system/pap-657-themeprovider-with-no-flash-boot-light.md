---
identifier: "PAP-657"
title: "ThemeProvider with no-flash boot, light, dark, hc and system modes, and generateBrandTheme producing contrast-validated OKLCH ramps"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: "PAP-75"
children: []
blockedBy: ["PAP-66"]
blocks: ["PAP-235", "PAP-461", "PAP-658"]
key: "r4/design-system/theme-provider-and-brand-theme-generator"
url: "https://linear.app/paperos/issue/PAP-657/themeprovider-with-no-flash-boot-light-dark-hc-and-system-modes-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:32.290Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-657: ThemeProvider with no-flash boot, light, dark, hc and system modes, and generateBrandTheme producing contrast-validated OKLCH ramps

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-75, pure code with no procedures or uploads: the runtime theme switch that never flashes, and the palette generator that turns one accent into a full tenant theme that still passes every PAP-66 contrast pair. Storybook's theme toolbar (PAP-69) and the wire issue (PAP-461) consume it.

**Scope**

In: `packages/ui/src/theme/{ThemeProvider,useTheme,boot,generateBrandTheme,inject,inlineCss}.ts`; boot script for `apps/web/index.html`; `pos.settings.theme` storage key; `data-theme` and `data-tenant` attribute contracts; hc token finalisation; `brandingToInlineCss`; Storybook toolbar hook.

Out: branding table, procedures, settings page, Logo and SVG sanitising (sibling), email and PDF kit (PAP-235), per-page themes.

**Spec**

* Boot script (inline, under 600 bytes) reads `localStorage['pos.settings.theme']` in try/catch and `matchMedia('(prefers-color-scheme: dark)')`, sets `data-theme` on `<html>` before first paint; `ThemeProvider` hydrates from the attribute, exposes `{ mode, setMode, resolved }`, listens to `matchMedia` changes in `system` mode, and calls Tauri `window.setTheme` when present.
* `generateBrandTheme({ accent, neutral?, radius?, font? })` derives an 11-step OKLCH ramp at lightness `97, 93, 85, 75, 65, 55, 47, 39, 31, 23, 15` with a chroma curve from the accent; dark maps inverted; hc clamps `fg` to L 10 or 98 and doubles border widths; it nudges lightness until every PAP-66 semantic pair passes 4.5:1 or 3:1 and returns `{ css, failures: [{ token, ratio, required }] }`.
* `injectTenantTheme(css, tenantId?)` replaces one `<style id="pos-tenant-theme">` atomically, scoped to `[data-tenant="<id>"]` or `:root`, under 6 KB; uses the same `--pos-` variable names as PAP-66, never new ones.
* `brandingToInlineCss(branding)` returns inline-safe hex values (OKLCH to sRGB via `culori` `clampChroma`) for PAP-235 and PAP-89 digest HTML.
* Print media forces light; `forced-colors: active` leaves system colours untouched; the Storybook `globalTypes.theme` toolbar sets the attribute through this provider.

**Interface contract**

Provides: `ThemeProvider`, `useTheme()`, `generateBrandTheme()`, `injectTenantTheme()`, `brandingToInlineCss()`, `TenantBranding` Zod schema (colour subset), `data-theme|data-tenant` contracts, `pos.settings.theme` key, `ThemePort` implementation for `contract-design-system`. Consumes: tokens, semantic pairs and `tokens:check` maths (PAP-66), `culori`. Consumed by the sibling settings page, PAP-69 toolbar, PAP-461 wire, PAP-235, PAP-82 theme fixture, PAP-18 `theme_color`.

**Definition of done**

* No flash on first paint for light, dark, hc and system (Playwright screenshot at first paint, all four); `generateBrandTheme` for 20 random accents passes all contrast pairs after nudging (Vitest); CSS size cap tested.
* `docs/design/theming.md` sections on modes and generation; changelog; Linear comment on PAP-69 and PAP-461.

**Test plan**

* Unit: ramp generation; nudge convergence within 20 iterations; near-white and near-black accents fall back to a neutral-tinted ramp with a warning; hex conversion and gamut clamp; boot script parsing with a blocked `localStorage`.
* Integration: `injectTenantTheme` for two tenants in two windows does not bleed (jsdom documents).
* E2E: mode switch persists across reload; system mode follows a `matchMedia` emulation change; print emulation forces light.

**Demo**

Reviewer flips the mode through light, dark, hc and system in the template app with no flash on reload, then runs `pnpm tsx scripts/brand-theme.ts '#7c3aed'` and reads the generated CSS and zero failures. Under one minute.

**Edge cases**

* `localStorage` throws (private mode): boot script falls back to system with no error.
* Accent with chroma outside sRGB: clamped, noted in `failures` as a warning.
* Theme changed in another tab: `storage` event re-syncs.
* hc mode with a tenant accent: accent kept only where it passes 7:1, else system accent.

**Dependencies**

PAP-66 (hard). Blocks the sibling, PAP-461, PAP-235; PAP-69's toolbar sets the attribute directly until this lands (soft).

**Agent**

Builder: Iris (Token Keeper). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
