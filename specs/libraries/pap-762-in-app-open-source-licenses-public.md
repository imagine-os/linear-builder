---
identifier: "PAP-762"
title: "In-app open source licenses: public `/_public/licenses` page and desktop About dialog rendering `THIRD_PARTY_NOTICES.md` per bundle"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-211"]
blocks: []
key: "r4/libraries/oss-licenses-page"
url: "https://linear.app/paperos/issue/PAP-762/in-app-open-source-licenses-public-publiclicenses-page-and-desktop"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.662Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-762: In-app open source licenses: public `/_public/licenses` page and desktop About dialog rendering `THIRD_PARTY_NOTICES.md` per bundle

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-211 generates `THIRD_PARTY_NOTICES.md` and bundles it into Tauri resources. Attribution licenses (MIT, Apache, OFL for fonts) require the notice to be visible to end users, which a file inside an app bundle is not. Render it: one public page every generated app ships, and the desktop About dialog.

**Scope**

In: route `/_public/licenses` (page spec `public/licenses.spec.yaml`, `layout.template: public`, `seo.noindex: false`) rendering the notices grouped by license with search and a per-bundle switch (web, desktop) from the JSON form PAP-211 emits (`reports/notices.json`); Tauri About dialog (`apps/desktop`, PAP-255 menu) opening the same content in a window with the app version from `/__version`; footer link in the customer portal shell (PAP-62) and the landing template (PAP-750); `docs/libraries/notices.md`. Out: generating notices (PAP-211), license decisions.

**Spec**

* Notices JSON: `{ bundle, generatedAt, packages: [{ name, version, license, licenseText?, repository, notice? }] }`; page virtualises the list (700+ packages), groups by SPDX id, shows the full text on expand, and includes fonts and icons (OFL, ISC) as PAP-211 requires.
* Generated at build by PAP-211's notices step; the page reads a static import so it works offline in Tauri and on GitHub Pages demos (PAP-15).
* About dialog: app name, version and SHA, link to the changelog (PAP-133) and the licenses window; menu item `Help > About PaperOS` (PAP-255).
* Tenant branding (PAP-75) applies; the page is exempt from tenant module toggles (always present).
* Page is registered with the spec validator like any page; conformance test asserts the list renders and the public access.

**Interface contract**

Provides: `/_public/licenses` page spec and view, `LicensesList`, About dialog, footer slot fill `shell.footer.links:licenses`. Consumes: `notices.json` (PAP-211), public layout (PAP-16), Tauri menu (PAP-255), version endpoint (PAP-26), changelog route (PAP-133), branding (PAP-75), slots (PAP-438). Consumed by: PAP-363 starter kit (footer), PAP-256 installers (attribution requirement), every generated app.

**Definition of done**

* Page renders 700 packages under 1 s at 375 and 1280 (virtualised); About dialog opens on Linux desktop with version and licenses; screenshots in light and dark; axe clean.
* Conformance test green; `docs/libraries/notices.md`; CHANGELOG entry.

**Test plan**

* Unit: grouping and search, JSON shape validation.
* Integration: build produces `notices.json` for web and desktop bundles; static import resolves offline.
* E2E (Playwright): open `/_public/licenses` anonymously, search `react`, expand a license text; Tauri smoke opens About.

**Demo**

Open `/_public/licenses` in a private window, search `tiptap`, expand the MIT text, then open Help > About in the desktop build. Under one minute.

**Edge cases**

* Package with `SEE LICENSE IN` text (tldraw): full file text rendered from the notice.
* Notices missing at dev time: page shows 'run `pnpm licenses:notices`' in dev, never in production builds (build fails instead).
* Two bundles differ (desktop-only crates): switch shows both lists.

**Dependencies**

Hard: PAP-211. Soft: PAP-16, PAP-255, PAP-26, PAP-133, PAP-75, PAP-438, PAP-363.

**Agent**

Builder: Scout (Library Evaluator) with Iris. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/spec-builder/page-spec-templates` = PAP-750.
