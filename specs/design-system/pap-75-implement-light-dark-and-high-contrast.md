---
identifier: "PAP-75"
title: "Implement light, dark and high-contrast themes plus per-tenant brand theming with runtime token override"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66"]
blocks: ["PAP-235"]
key: "design-system/theming"
url: "https://linear.app/paperos/issue/PAP-75/implement-light-dark-and-high-contrast-themes-plus-per-tenant-brand"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:12.905Z"
---

# PAP-75: Implement light, dark and high-contrast themes plus per-tenant brand theming with runtime token override

**Goal**

Let any app switch between light, dark and high-contrast at runtime and let each tenant upload a logo and a few brand colours that re-theme the whole product without a rebuild, while every generated palette still passes contrast checks.

**Scope**

* In: `ThemeProvider` with `mode: 'light' | 'dark' | 'hc' | 'system'` persisted per user and applied as `data-theme` with a no-flash boot script; `generateBrandTheme()` producing OKLCH ramps with contrast validation and nudging; `tenant.branding jsonb` and `branding.get/update` procedures gated by `can('tenant.branding.update')`; `/org/settings/branding` page and spec with live preview; `Logo` component with SVG sanitising; hc token finalisation; Storybook toolbar hook.
* Out: custom CSS injection, per-page themes, marketing site theming, font uploads (allowlist only), email and PDF rendering (PAP-235 consumes `brandingToInlineCss`, which this issue provides).

**Spec**

* Boot script in `apps/web/index.html` reads `localStorage` `pos.settings.theme` and `matchMedia` and sets `data-theme` before first paint; `ThemeProvider` hydrates from it; Tauri also calls `window.setTheme`.
* `generateBrandTheme({ accent, neutral?, radius?, font? })` fixes hue and a chroma curve from the accent and derives 11 steps at lightness `97, 93, 85, 75, 65, 55, 47, 39, 31, 23, 15`; dark maps inverted; hc clamps `fg` to L 10 or 98 and doubles border widths; returns `{ css, failures: [{ token, ratio, required }] }` after nudging lightness until every PAP-66 semantic pair passes.
* Injection: one `<style id="pos-tenant-theme">` replaced atomically, scoped to `[data-tenant="<id>"]` or `:root`, under 6 KB.
* `tenant.branding = { logoFileId, logoDarkFileId?, accent, neutral?, radius?, fontFamily?, defaultMode }`; fonts from an allowlist of 12 Google fonts plus system stacks with `font-display: swap`.
* `Logo` picks light or dark variant, falls back to the tenant name; SVG max 512 KB sanitised with `dompurify` on upload; PNG accepted.
* Settings page: colour pickers, logo upload (PAP-37), live component preview, contrast failure list with the adjusted colour shown, reset.
* `brandingToInlineCss(branding)` returns inline-safe hex values for PAP-235.

**Interface contract**

* Provides: `ThemeProvider`, `useTheme()` (`{ mode, setMode, resolved }`), `generateBrandTheme()`, `brandingToInlineCss()`, `Logo`, `TenantBranding` Zod schema, procedures `branding.get`, `branding.update`, the `data-theme` and `data-tenant` attribute contracts, `pos.settings.theme` storage key; the same CSS variable names as PAP-66 (overrides only, no new names).
* Requires: PAP-66 tokens (hard); PAP-33 `tenant.branding` column, PAP-35 procedures, PAP-37 file storage, PAP-59 permission, PAP-63 settings route, PAP-36 cache (all soft).
* Consumers: PAP-62 portal, PAP-63 console, PAP-235, PAP-180 PDFs, PAP-193 landing pages, PAP-69 toolbar, PAP-82 theme fixture.

**Definition of done**

* No flash on first paint for light, dark, hc and system (Playwright screenshot at first paint).
* `generateBrandTheme` for 20 random accents: all contrast pairs pass after nudging (Vitest).
* Settings page screenshots at 375, 768, 1280 and 1920; live preview updates within one frame of a picker change (video).
* Tenant switch re-themes without reload (e2e with two tenants).
* Security review of SVG sanitising; `docs/design/theming.md`; changelog entry; Linear comment with before/after screenshots.

**Test plan**

* Unit: ramp generation, nudge convergence, near-white and near-black accents fall back with a warning, CSS size cap, `brandingToInlineCss` hex output.
* Integration: `branding.update` denied for `member`; sanitiser strips `<script>` and external references from a fixture SVG.
* E2E: mode switch persists across reload; system mode follows a `matchMedia` change; two windows with different tenants do not bleed.
* Visual: settings page at four widths; print media forces light.

**Demo**

Open `/org/settings/branding` as the seeded owner, pick a purple accent and upload the sample logo, watch the preview and the console re-theme live, then switch to the second tenant and back. Under two minutes.

**Edge cases**

* Accent nearly white or black: neutral-tinted fallback with a warning.
* Malicious SVG: stripped; raster fallback offered.
* Offline first load: branding cached in PGlite (PAP-36).
* Printing: light theme forced.

**Dependencies**

PAP-66 (hard). Soft: PAP-33, PAP-35, PAP-37, PAP-59, PAP-63, PAP-36.

**Agent**

Iris (Token Keeper). Reviewed by Sentinel (Security Auditor for uploads, Visual Inspector for themes); Ledger consulted on branding needs for PAP-235.

**Size**

M.
