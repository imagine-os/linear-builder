---
identifier: "PAP-870"
title: "Build review requests and reputation: Google, Facebook and Yelp review links after positive scores, review capture, display widgets for landing pages and a reputation dashboard"
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
blockedBy: ["PAP-136", "PAP-193", "PAP-725", "PAP-794", "PAP-869"]
blocks: []
key: "r4/engagement/reviews-requests"
url: "https://linear.app/paperos/issue/PAP-870/build-review-requests-and-reputation-google-facebook-and-yelp-review"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:37.704Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-870: Build review requests and reputation: Google, Facebook and Yelp review links after positive scores, review capture, display widgets for landing pages and a reputation dashboard

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Turn happy customers into public reviews: after a promoter score (or directly after a completed booking or order) send a review request with the tenant's Google, Facebook or Yelp links, capture first-party reviews on a PaperOS page, display approved reviews as a widget on landing pages (PAP-193) and the public site, and show a reputation dashboard with request, click and review counts.

**Scope**

In: `review_profile` (platform links per location), `review_request` (contact, trigger, sent, clicked platform), `review` (first-party: rating, text, author display consent, status pending|approved|hidden, reply); request flow as a `survey` follow-up (promoters) or standalone trigger with the same throttle and consent. Public page `/reviews/:token` to leave a first-party review; approved reviews dataset; widget `reviews.js` (shares the PAP-193 embed mechanics) and a `portal.home.cards` fill. Reputation dashboard blocks (PAP-173): requests sent, click-through per platform, first-party rating average and volume trend; staff reply to first-party reviews with the reply shown publicly.

Out: Scraping or importing reviews from platforms (API terms vary; v0.3 ADR). Incentivised reviews (refused by policy text in the flow).

**Spec**

* Review gating (only asking promoters to post publicly) is off by default and labelled with the platform-policy warning when enabled; the setting is audited
* First-party reviews are published only after staff approval; author names use the display consent captured on the page
* Widget budget under 8 KB; renders server-provided HTML with structured data (`schema.org/Review`) for SEO

**Interface contract**

Provides: `ReviewsPort.request|record`, review tables and pages, `reviews.js`, reputation blocks, `review.requested|received` events. Consumes: surveys (promoter follow-up), landing embeds (PAP-193), notifications (PAP-136), dashboards (PAP-173), consent (PAP-187). Consumed by: growth landing pages, migration packs (salon and restaurant packs enable review requests), platform-ops tenant health.

**Definition of done**

* Promoter fixture receives a review request, clicks Google (tracked), a first-party review is captured, approved and appears in the widget on the demo landing page; dashboard renders
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: gating default and warning; approval state machine; structured data output.
* E2E: review page on a phone; widget embed; reply flow.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Score 10 on the NPS demo, receive the review request, leave a first-party review, approve it in the console and see it appear on the landing page widget.

**Edge cases**

* Tenant with multiple locations: profiles per location; the request picks the location from the booking resource
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-869 (hard), PAP-193 (soft: embed mechanics), PAP-136, PAP-173 (soft).

**Agent**

Builder: Beacon. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/engagement/surveys-nps` = PAP-869.
