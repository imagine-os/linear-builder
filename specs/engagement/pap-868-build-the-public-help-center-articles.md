---
identifier: "PAP-868"
title: "Build the public help center: articles from tenant docs, categories, search, article feedback, contact and assistant entry points, custom domain and SEO basics"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Messaging channels, help center and surveys"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-39", "PAP-128", "PAP-379", "PAP-380", "PAP-431", "PAP-567", "PAP-862"]
blocks: ["PAP-876"]
key: "r4/engagement/help-center"
url: "https://linear.app/paperos/issue/PAP-868/build-the-public-help-center-articles-from-tenant-docs-categories"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-868: Build the public help center: articles from tenant docs, categories, search, article feedback, contact and assistant entry points, custom domain and SEO basics

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Give every tenant a help site their customers can find: published pages from the tenant docs store (PAP-379) organised in categories, full-text search (PAP-39), "was this helpful" feedback, a contact entry that opens the support widget or a form, the assistant's unauthenticated mode when enabled, under the tenant's custom domain with sitemap and metadata, and deep links from the in-app help panel (PAP-380).

**Scope**

In: Public routes `/help`, `/help/:category`, `/help/:slug` on the public layout with tenant branding (PAP-75) and domain (PAP-431); `help_category` and a `published` flag plus `audience` on tenant docs (PAP-379) so drafts and staff-only pages never leak; server-rendered HTML for SEO (Vite SSR route or prerender job) with sitemap, canonical and Open Graph tags. Search: PAP-39 registration `help_article` with `audiences: [customer, anonymous]`; instant search box; "no results" leads to contact. Feedback: thumbs per article with optional comment stored on the article, aggregated in a staff view; `article.feedback` event; low-rated articles surface in the staff docs list. Entry points: `Contact us` opens PAP-411 widget or a forms-runtime form; assistant launcher when `portalEnabled` and the unauthenticated mode exists; the PAP-380 help panel links to articles tagged with the page spec key.

Out: Multi-language articles beyond the PAP-27 locale switch (v0.3 with translation skill). Community forums.

**Spec**

* Only pages with `published` and `audience` including `customer` or `anonymous` are served; the query is an RLS-compatible predicate, not an application filter
* Rendering budget: help pages are static HTML plus a 15 KB island for search and feedback; Lighthouse ≥ 95 on performance and SEO
* Article versions: publishing snapshots the Yjs document to HTML; edits do not change the public page until republished; the snapshot is what search indexes
* Accessibility: heading outline, skip links, focus order; axe clean; the help panel deep link opens the article in the inspector without leaving the app

**Interface contract**

Provides: `HelpCenterPort.publish|search|feedback`, public help routes, categories, feedback aggregation view, sitemap, `help_article` search registration. Consumes: tenant docs (PAP-379), search (PAP-39), domains and branding (PAP-431, PAP-75), help panel (PAP-380), docs engine rendering (PAP-128), support widget (PAP-411), forms runtime (soft). Consumed by: assistant portal grounding, booking pages (policy articles), commerce (return policy), migration packs (starter articles).

**Definition of done**

* Demo tenant help center live on staging with 10 starter articles, search, feedback and contact; Lighthouse ≥ 95; a draft article is proven unreachable; in-app help panel deep-links
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: publish snapshot and predicate; sitemap generation; feedback aggregation.
* E2E: search, open, rate, contact on a phone; crawl test for drafts returning 404.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Publish "How to reschedule" from tenant docs, search for it on the public help center, rate it, then open the same article from the help panel inside the portal.

**Edge cases**

* Article unpublished while indexed: the search row is removed in the same transaction and the URL returns 410 with a search box
* Custom domain not yet verified: help center serves on the platform subdomain and the settings page shows the DNS steps
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-379 (hard), PAP-39 (hard), PAP-431, PAP-75 (soft), PAP-380, PAP-128 (soft), PAP-411 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
