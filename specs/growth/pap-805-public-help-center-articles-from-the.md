---
identifier: "PAP-805"
title: "Public help center: articles from the docs engine with categories, search, portal embed, article suggestions in the support widget and deflection metrics"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-39", "PAP-128", "PAP-411", "PAP-567"]
blocks: ["PAP-806"]
key: "r4/growth/help-center-knowledge-base"
url: "https://linear.app/paperos/issue/PAP-805/public-help-center-articles-from-the-docs-engine-with-categories"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:46.959Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-805: Public help center: articles from the docs engine with categories, search, portal embed, article suggestions in the support widget and deflection metrics

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

PAP-197 leaves the public knowledge base out. Intercom and Chatwoot deflect a third of tickets with articles; the docs engine (PAP-128) already renders MDX, so the help center is mostly a public route, a category model and search wired into the chat widget.

**Scope**

In: `help_article` metadata over PAP-128 docs under `docs/help/**` or the runtime docs store (PAP-379) with `category`, `audience`, `status: draft|published`, `keywords`; public route `/help` and `/help/:slug` with tenant branding, category navigation and PAP-39 search; article suggestions in `<SupportChat/>` (PAP-411) from the visitor's typed message before a conversation opens; 'Was this helpful' votes; deflection dataset (suggestions shown, article opened, conversation avoided); staff 'insert article link' in the PAP-412 reply box; sitemap and `noindex` per article.

Out: AI-generated answers (PAP-806), multi-language articles beyond PAP-27 locale routing, community forums.

**Spec**

* Articles are docs: authoring, versioning and comments come from PAP-128 and PAP-131; this issue adds metadata and public rendering only.
* Public search is scoped to `published` articles of the tenant and rate limited per PAP-267; queries are logged without PII for the 'no results' report.
* Suggestion ranking is BM25 from PAP-39 with keyword boosts; the widget shows at most three.

**Interface contract**

Provides: help routes, `helpArticles.*`, `HelpSuggestions` component for the widget, datasets `growth.helpDeflection`, `growth.helpSearchMisses`. Consumes: docs engine and store (PAP-128, PAP-379 soft), chat widget (PAP-411), search (PAP-39), console reply box (PAP-412 soft), theming (PAP-74), rate limits (PAP-267).

**Definition of done**

* Public pages render from fixture articles with search; suggestions appear in the widget in Playwright; deflection dataset increments; screenshots at 320, 375, 768, 1024, 1920 light and dark; axe clean.
* `docs/growth/help-center.md`; CHANGELOG.

**Test plan**

* Unit: metadata validation, ranking boosts, vote idempotency per visitor hash, sitemap generation.
* E2E: publish two articles, search from `/help`, type a matching question in the portal widget and click the suggestion instead of opening a conversation.

**Demo**

Reviewer publishes an article, opens the portal widget, types a related question and clicks the suggested article, then reads the deflection count. Under two minutes.

**Edge cases**

* Article unpublished while linked from a conversation: link shows 'no longer available'.
* Search with zero results: logged for the misses report, widget offers to start a conversation.

**Dependencies**

Hard: PAP-128, PAP-411, PAP-39. Soft: PAP-379, PAP-412, PAP-74, PAP-267.

**Agent**

Builder: Beacon (CRM Builder) with Quill. Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/support-ai-reply-drafts` = PAP-806.
