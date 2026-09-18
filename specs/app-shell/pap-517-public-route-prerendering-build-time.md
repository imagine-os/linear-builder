---
identifier: "PAP-517"
title: "Public route prerendering: build-time static HTML for `_public` routes with React 19 hydration checks, `noindex` on preview hosts, wired into the Pages build and the web image"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-15", "PAP-363", "PAP-507", "PAP-745"]
blocks: []
key: "r4/app-shell/public-seo-prerender"
url: "https://linear.app/paperos/issue/PAP-517/public-route-prerendering-build-time-static-html-for-public-routes"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:00.715Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-517: Public route prerendering: build-time static HTML for `_public` routes with React 19 hydration checks, `noindex` on preview hosts, wired into the Pages build and the web image

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 (past 2026-10-01). The starter landing page (PAP-363) is a client-rendered SPA: crawlers and link previews receive an empty shell. PAP-745 emits titles, Open Graph tags, the OG image route, sitemap and robots from the spec; those tags only help if the HTML that carries them exists before JavaScript runs. This issue adds the prerender step so public routes ship as static HTML with the spec-emitted head, and leaves everything about the tags themselves to the spec-builder issue.

**Scope**

In:

* `scripts/prerender.ts` (Playwright against the built bundle, or `vite-plugin-prerender` if the ADR in PAP-213 prefers it) rendering every route with `layout.template: public` from the route tree to `dist/<route>/index.html`, keeping the TanStack `head()` output and a hydration marker; runs in the PAP-15 Pages build and the PAP-26 web image build.
* Hydration check: React 19 hydration warnings during a post-build smoke render fail the build; a `data-prerendered` attribute lets Gate 3 (PAP-82) assert the landing page paints before JavaScript.
* Environment rules: preview and staging hosts add `<meta name="robots" content="noindex">` and `X-Robots-Tag` from the Caddy config (PAP-26); production emits what the spec says.
* Cache and invalidation: prerendered HTML carries the build SHA; the service worker (PAP-18) treats prerendered routes as precached shell entries.

Out: head tags, OG image, sitemap and robots (PAP-745), SSR of authenticated routes, marketing site (PAP-193), per-tenant branding in HTML beyond what the spec emits.

**Spec**

* Prerender is deterministic for a given SHA and spec set; the Pages build fails on a diff between two consecutive renders of the same input.
* Routes with loaders (public pricing from Stripe) prerender with the loader's fallback state and revalidate on hydration; no network at build time.
* Build time budget: under 20 s for ten public routes on the CI runner; routes are rendered in parallel.
* Locale: one HTML per enabled locale under `/<locale>/` when PAP-27 has more than `en` enabled; `hreflang` comes from the spec-builder issue.

**Interface contract**

Provides: `pnpm prerender`, the `data-prerendered` marker, the noindex environment rule, prerender step in Pages and image builds; consumed by PAP-363 (landing), PAP-745 (its tags become visible to crawlers), PAP-87 (SEO Lighthouse category), PAP-407 (referral landing previews).

Consumes: starter landing spec (PAP-363), Pages build (PAP-15), web image (PAP-26), spec-emitted head and crawl files (PAP-745), locales (PAP-27, soft), service worker precache (PAP-18, soft).

**Definition of done**

* `curl` of the preview landing page returns rendered HTML containing the spec-emitted title and OG tags before any script tag; Playwright with JavaScript disabled reads the hero text; hydration produces zero console warnings.
* Preview host serves `noindex`; production build does not; Lighthouse SEO at or above 90 on the preview (the spec-builder issue asserts the tags, this issue asserts they are in static HTML); CHANGELOG; Linear comment.

**Test plan**

* Unit: route selection by `layout.template`; noindex rule by environment; determinism check of two renders.
* E2E: Playwright with JavaScript disabled loads the landing page text from the Pages preview; hydration console assertion on the same page with JavaScript enabled.

**Demo**

Reviewer runs `curl -s https://imagine-os.github.io/<repo>/ | head -40` and reads the rendered hero and Open Graph tags, then pastes the URL into Slack and sees the unfurl. Under a minute.

**Edge cases**

* Public route that depends on the tenant host (PAP-431 custom domains): prerendered once with the default branding; host-specific head values are patched at the edge by the spec-builder issue's per-host route, documented as the limit of static prerendering.
* Route added to `_public` without `layout.template: public` in its spec: validator (PAP-115) warns and the route is skipped, not silently rendered.
* Prerender crashes on one route: build fails naming the route; no partial `dist`.

**Dependencies**

Hard: PAP-363, PAP-15, PAP-745. Soft: PAP-26, PAP-27, PAP-18, PAP-82, PAP-87.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/spec-builder/seo-public-metadata` = PAP-745.
