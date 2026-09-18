---
identifier: "PAP-658"
title: "Tenant branding: tenant.branding schema and procedures, /org/settings/branding page with live preview and contrast report, Logo component and SVG sanitising"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: "PAP-75"
children: []
blockedBy: ["PAP-37", "PAP-63", "PAP-229", "PAP-583", "PAP-657", "PAP-663"]
blocks: ["PAP-62", "PAP-193", "PAP-235", "PAP-461", "PAP-584", "PAP-793"]
key: "r4/design-system/tenant-branding-settings-and-logo"
url: "https://linear.app/paperos/issue/PAP-658/tenant-branding-tenantbranding-schema-and-procedures"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:23.731Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-658: Tenant branding: tenant.branding schema and procedures, /org/settings/branding page with live preview and contrast report, Logo component and SVG sanitising

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-75: persist a tenant's brand and let an owner change it safely. The `branding` column and procedures, the settings page with live preview and the contrast failure list, the `Logo` component and the SVG upload path that a security reviewer signs off.

**Scope**

In: `tenant.branding jsonb` schema `{ logoFileId, logoDarkFileId?, accent, neutral?, radius?, fontFamily?, defaultMode }`; procedures `branding.get|update` gated by `can('tenant.branding.update')`; `BrandingSettingsPage` and its spec fragment, mounted by identity's console at `/console/settings/branding` (PAP-583); `Logo`; SVG sanitising with `dompurify`; font allowlist; PGlite cache for offline first paint.

Out: theme generation and provider (sibling), custom CSS injection, font uploads (allowlist only), email and PDF (PAP-235).

**Spec**

* `branding.update` validates with the `TenantBranding` schema, runs `generateBrandTheme` server-side and stores the resulting `css` alongside the input so clients never regenerate; emits `theme.changed { tenantId }` (contract topic) which PAP-143 shapes deliver to open sessions; audit row with before and after.
* Fonts: allowlist of 12 Google fonts plus system stacks, loaded with `font-display: swap` and self-hosted through PAP-37 storage at build time (no runtime Google requests); unknown family rejected.
* `Logo` picks light or dark variant by resolved theme, falls back to the tenant name in the accent colour, sizes `sm|md|lg`; SVG uploads max 512 KB sanitised on upload (`dompurify` with the SVG profile, external references and scripts stripped, `viewBox` required) and re-served as `image/svg+xml` with `Content-Security-Policy: sandbox`; PNG and WebP accepted through PAP-37 variants.
* Settings page: colour pickers (design-system `ColorPicker` from PAP-663, soft: native `<input type=color>` fallback), logo upload with preview, live preview of Button, Badge, Card, Nav and a grid row re-themed within one frame of a change, contrast failure list showing the adjusted colour, reset to defaults, save with confirmation.
* Offline first load: branding cached in PGlite (PAP-36) and applied by the boot path; tenant switch (PAP-58) swaps the injected style without reload.

**Interface contract**

Provides: `TenantBranding` full schema, `branding.get|update`, `BrandingSettingsPage` (`app.settingsBranding`), `Logo` (`ui.logo`), `sanitizeSvg()`, font allowlist `brandFonts`, topic `theme.changed`. Consumes: `generateBrandTheme` and injection (sibling), `tenant` table (PAP-33), procedures (PAP-268), files (PAP-37), permissions (PAP-229), console route (PAP-63, PAP-583), shapes (PAP-143, soft), PGlite cache (PAP-36, soft), `ColorPicker` (soft). Consumed by PAP-62 portal, PAP-235, PAP-193 landing pages, PAP-180 PDFs.

**Definition of done**

* Settings page screenshots at 375, 768, 1280, 1920 in three themes; live preview within one frame (video); tenant switch re-themes without reload (e2e with two tenants).
* Security review of SVG sanitising with a fixture corpus (Sentinel Security Auditor comment); `docs/design/theming.md` branding section; changelog; Linear comment with before and after screenshots.

**Test plan**

* Unit: schema validation; font allowlist; sanitiser strips `<script>`, `on*` attributes, external `href` and `<foreignObject>` from fixtures; `Logo` variant selection.
* Integration: `branding.update` denied for `member`; audit row present; `theme.changed` emitted; second session receives the new CSS within 2 s.
* E2E: pick a purple accent and upload the sample logo as owner, watch the console re-theme live, switch to the second tenant and back, reload offline and see the cached branding.

**Demo**

Reviewer opens `/console/settings/branding` as the seeded owner, picks a purple accent, uploads the sample logo, watches the preview and the console re-theme, then switches tenant. Under two minutes.

**Edge cases**

* Malicious SVG: stripped; if nothing renderable remains, upload rejected with a raster fallback offer.
* Accent nearly white or black: sibling fallback with the warning surfaced in the failure list.

**Dependencies**

Sibling provider (hard), PAP-37 (hard, uploads), PAP-229 (hard, permission), PAP-63 (hard, settings route). Soft: PAP-33, PAP-268, PAP-143, PAP-36, specialised inputs. Blocks PAP-235, PAP-193, PAP-62 branding.

**Agent**

Builder: Iris (Token Keeper). Reviewer: Sentinel (Security Auditor (uploads), Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/design-system/specialised-inputs` = PAP-663, `r4/identity/console-admin-pages` = PAP-583.
