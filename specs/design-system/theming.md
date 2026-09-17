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
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-75: Implement light, dark and high-contrast themes plus per-tenant brand theming with runtime token override

**Goal**

Let any PaperOS app switch between light, dark and high-contrast themes at runtime and let each tenant upload a logo and a few brand colours that re-theme the whole product without a rebuild, while every generated palette still passes contrast checks.

**Scope**

In:
- `ThemeProvider` in `packages/ui/src/theme/` managing `mode: 'light'|'dark'|'hc'|'system'`, persisted per user (`pos.settings.theme`), applied as `data-theme` on `<html>` with no flash (inline boot script in `apps/web/index.html`).
- Brand theme generator `generateBrandTheme({ accent, neutral?, radius?, font? })` producing OKLCH ramps with `culori`, validating contrast against the semantic pairs from `design-system/tokens`, and emitting a CSS string of overridden variables scoped to `[data-tenant="<id>"]` or `:root`.
- Tenant branding stored in `tenant.branding jsonb` (`data-layer/core-entities`): `{ logoFileId, logoDarkFileId?, accent, neutral?, radius?, fontFamily?, mode default }`; API procedure `branding.get/update` (`data-layer/api-layer`) gated by `can('tenant.branding.update')`.
- Branding settings page spec and UI `/org/settings/branding` in the staff console: colour pickers, logo upload (`data-layer/file-storage`), live preview of components, "reset to default".
- Storybook toolbar hooks into the same provider; `hc` theme tokens finalised (higher contrast, thicker borders, no shadows).

Out: full custom CSS injection, per-page themes, marketing site theming (Webflow), font uploading (system and Google fonts allowlist only).

**Spec**

- Boot script reads `localStorage` theme and `matchMedia` and sets `data-theme` before first paint; `ThemeProvider` hydrates from it.
- Generated ramps: derive 11 steps by fixing hue and chroma curve from the accent, lightness steps `97, 93, 85, 75, 65, 55, 47, 39, 31, 23, 15`; dark theme maps inverted; hc theme clamps `fg` to L 10 or 98 and doubles border widths.
- Contrast validation returns `{ ok, failures: [{ token, ratio, required }] }`; the settings UI shows failures and auto-nudges lightness until pairs pass, showing the adjusted colour.
- Runtime injection: a single `<style id="pos-tenant-theme">` element replaced atomically; CSS size under 6 KB.
- Tauri: theme mode also sets the native window theme via `window.setTheme` for title bars.
- Logo: `Logo` component picks light or dark variant, falls back to tenant name in `font-semibold`; max 512 KB SVG or PNG, SVG sanitised with `dompurify` on upload.
- Fonts: allowlist of 12 Google fonts plus system stacks loaded with `font-display: swap`.
- Email templates and PDFs read the same branding JSON via a `brandingToInlineCss()` helper for later business-core use.

**Definition of done**

- Mode switching with no flash proven by Playwright (screenshot at first paint) for light, dark, hc, and system.
- Brand theme generation tested in Vitest for 20 random accents: all contrast pairs pass after nudge.
- Settings page screenshots at 375, 768, 1280 and 1920; live preview updates within one frame of picker change (video).
- Tenant switch (`identity/org-tenancy`) re-themes without reload; e2e test with two tenants.
- Security review of SVG sanitisation; `docs/design/theming.md`; CHANGELOG entry; Linear comment with preview link and a before/after screenshot pair.

**Edge cases**

- Accent colour nearly white or black: generator falls back to neutral-tinted accent and warns.
- Two tenants open in two windows of the same user: `[data-tenant]` scoping prevents cross-bleed; theme element keyed per window.
- Logo SVG containing scripts or external references: stripped; raster fallback offered.
- System theme changes while app is open: `system` mode follows live via `matchMedia` listener.
- Printing: force light theme in `@media print`.
- Offline (local-first) first load: last branding cached in PGlite so the brand shows without network.

**Dependencies**

`design-system/tokens` (hard). Soft: `data-layer/core-entities` (branding column), `data-layer/api-layer`, `data-layer/file-storage` (logo), `identity/rbac-abac` (permission), `identity/staff-console-shell` (settings route). Consumed by `identity/customer-portal-shell`, `business-core/invoicing` (branded PDFs), `growth/landing-forms`.

**Agent**

Built by Iris (Token Keeper). Reviewed by Sentinel (Security Auditor for SVG upload, Visual Inspector for all themes) and Ledger consulted on PDF branding needs.

**Size**

M: the generator and contrast nudging are subtle; the settings page is straightforward once components exist.
