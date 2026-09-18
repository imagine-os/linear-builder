---
identifier: "PAP-745"
title: "Public page metadata from specs: `seo` section to `<head>` tags, Open Graph image route, sitemap and robots generation per app"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-314", "PAP-740"]
blocks: ["PAP-517"]
key: "r4/spec-builder/seo-public-metadata"
url: "https://linear.app/paperos/issue/PAP-745/public-page-metadata-from-specs-seo-section-to-head-tags-open-graph"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:35.152Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-26"
cycle: null
---

# PAP-745: Public page metadata from specs: `seo` section to `<head>` tags, Open Graph image route, sitemap and robots generation per app

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Every generated app ships a public landing page and public docs (PAP-363, PAP-128, PAP-133), and PAP-193 publishes marketing pages. None of them emits a `<title>`, description, Open Graph tags, sitemap or robots file from the spec, so the customer-facing half of the golden path is invisible to search and looks broken when shared. Compile the v1.1 `seo` section and generate the two crawl files.

**Scope**

In: head emission in PAP-314's route template for `layout.template: public` pages using TanStack Router `head()` (title, description, canonical, `og:*`, `twitter:card`, `robots`); generator `sitemap` in PAP-362's pipeline writing `apps/web/public/sitemap.xml` and `robots.txt` from public page routes plus PAP-128 public docs and PAP-133 public changelog; OG image route `/_public/og/$pageId.png` rendering a tokenised card (PAP-66 tokens, app name, title) with `@vercel/og`-style satori in the API; `docs/spec/seo.md`. Out: marketing analytics (PAP-194), custom domains (PAP-431; sitemap uses `PAPEROS_DOMAIN`), structured data beyond `WebSite`.

**Spec**

* Defaults: `title` falls back to `purpose.summary` truncated to 60 chars, `description` to the first sentence of `purpose.summary` (155 chars), `ogImage` to the generated card; `noindex: true` emits `robots: noindex` and excludes the route from the sitemap; non-public pages are always `noindex` and never listed.
* Sitemap entries carry `lastmod` from the spec file's git commit date (PAP-128 history helper) and `hreflang` alternates when PAP-738 lands; robots allows public routes and disallows `/_app`, `/api`, `/_public/og` caching aside.
* OG card renders in under 300 ms cached 24 h by `specHash`; light theme only; text from the business profile terminology (PAP-126) when present.
* Per-tenant custom domains (PAP-431) get a per-host sitemap through a route that filters by tenant; until then one sitemap per app.
* Gate 3 (PAP-82) captures the landing page and Lighthouse (PAP-87) SEO score is asserted at or above 90 for public pages.

**Interface contract**

Provides: head emission in the route template, `sitemap` generator, `robots.txt`, OG image route, `seo` defaults resolver. Consumes: v1.1 `seo` section, route template (PAP-314), pipeline registry (PAP-362), tokens (PAP-66), business profile (PAP-126, soft), docs and changelog public routes (PAP-128, PAP-133), domain env (PAP-17), Lighthouse job (PAP-87). Consumed by: PAP-363 landing page, PAP-193 landing pages, PAP-133 public changelog.

**Definition of done**

* Landing and public docs pages emit correct tags (Playwright reads `<head>`); sitemap validates against the [sitemaps.org](<http://sitemaps.org>) XSD; OG image renders for two pages; Lighthouse SEO at or above 90 on the landing page.
* Screenshots of the OG card and a shared-link preview mock at 1200x630; `docs/spec/seo.md`; CHANGELOG entry.

**Test plan**

* Unit: defaults resolver, truncation, sitemap XML snapshot, robots rules, noindex exclusion.
* Integration: OG route through the API with cache headers; `--check` on the sitemap after adding a public page.
* E2E (Playwright): `<head>` assertions on the landing page at 375 and 1280.

**Demo**

Add `seo: { title: 'Book a physio session' }` to the landing spec, run `paperos gen`, open the page source and `sitemap.xml`, then fetch `/_public/og/landing.png`. Under one minute.

**Edge cases**

* Title over 60 characters: kept, warning `SEO_TITLE_LONG`.
* Public page behind a flag (PAP-744): excluded from the sitemap while off.
* App without a domain configured: sitemap uses the preview URL and warns.

**Dependencies**

Hard: PAP-740, PAP-314. Soft: PAP-362, PAP-66, PAP-126, PAP-128, PAP-133, PAP-17, PAP-87, PAP-431, PAP-363.

**Agent**

Builder: Nova with Beacon consulting on defaults. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/collab/docs-i18n` = PAP-738, `r4/spec-builder/flags-modules-compile` = PAP-744, `r4/spec-builder/schema-v1-1-extensions` = PAP-740.
