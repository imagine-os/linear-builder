---
identifier: "PAP-194"
title: "Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-163", "PAP-187", "PAP-43"]
blocks: []
key: "growth/attribution"
url: "https://linear.app/paperos/issue/PAP-194/track-acquisition-analytics-utm-referral-funnel-with-a-privacy-first"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-194: Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline

**Goal**

Know which channel, campaign and page produced each lead, signup and paying customer without shipping a third-party tracker: a first-party, cookieless event pipeline that records UTM and referral touches, stitches anonymous visitors to CRM contacts on identify, and renders funnel and channel reports as table views.

**Scope**

In:
- Schema `packages/growth/src/attribution/schema.ts`: `attr_event` (`id uuidv7`, `tenant_id`, `anonymous_id`, `contact_id` nullable, `user_id` nullable, `name`, `properties jsonb`, `utm jsonb`, `referrer_host`, `landing_path`, `session_id`, `device_class`, `occurred_at`; partitioned monthly), `attr_identity` (`anonymous_id` -> `contact_id|user_id`, `linked_at`, `method`), `attr_touch` (first and last touch per contact: `channel`, `campaign`, `source`, `medium`, `content`, `term`, `at`), `attr_funnel` (named step sequences).
- Collector: `POST /api/v1/public/collect` accepting batched events (max 50, 32 KB), CORS to registered origins, no cookies; `anonymous_id` generated client-side and kept in `localStorage`; server derives `device_class` from UA and discards UA and IP after hashing into `session_id` salt.
- Client SDK `packages/growth/src/attribution/client.ts` (under 4 KB gzipped): `track(name, props)`, `page()`, `identify(contactOrUser)`, auto-capture of UTM and referrer on first page, offline buffer; wired into `apps/web` route changes and the `form.js` embed from `growth/landing-forms`.
- Channel classification rules (`utm_medium`, referrer host lists for search, social, email, direct, referral, affiliate via `growth/referral-program` codes) in `channels.yaml`, editable per tenant.
- Reports as views (`tables/view-model-spec`): channel performance (visits, leads, customers, revenue from `business-core/stripe-billing` via `crm_company.billing_customer_id`), campaign table, funnel view for `attr_funnel` (step conversion), landing page table; embedded on a marketing dashboard page via `tables/dashboard-blocks`.
- Consent: honours `navigator.globalPrivacyControl` and tenant consent mode (`essential-only` disables identify stitching); DNT respected.

Out: session replay, heatmaps, ad platform conversion APIs, multi-touch weighting models beyond first and last touch (documented as follow-on).

**Spec**

- Event names namespaced: `page_viewed`, `form_submitted`, `lead_created`, `signup_completed`, `subscription_started`; custom events `custom.*`.
- Identify stitching: when `identify` arrives, all prior events with that `anonymous_id` are attributed to the contact; first touch is the earliest event's UTM or referrer; last touch is the latest before conversion.
- Retention: raw events 13 months (partition drop), touches indefinite.
- Aggregations computed by the view query compiler (`tables/query-compiler`) over materialised daily rollups `attr_daily` refreshed by a pg-boss job every 15 minutes.
- Revenue attribution joins Stripe invoices paid to contact via company; unknown mapping reported as "Unattributed revenue", never silently dropped.
- Public collector rate limit 120 events/min per `anonymous_id`.

**Definition of done**

- Vitest: channel classification against 40 referrer and UTM fixtures, identify stitching, first and last touch computation, batch validation and limits, rollup correctness against raw events.
- Playwright: land with UTM, submit a form (mock), sign up, see the contact's touches on the CRM detail and the channel report updated after rollup; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for channel report and funnel view.
- Load test: 1,000 events/s sustained for 5 minutes on staging with p95 ingest under 100 ms (k6 script committed).
- Privacy review by Sentinel (Security Auditor): no IP or UA stored raw; consent modes verified.
- `docs/growth/attribution.md` (event names, adding a channel rule, privacy stance); CHANGELOG entry; Linear comment with report screenshots and load test summary.

**Edge cases**

- `localStorage` blocked (private mode): `anonymous_id` per page load; events still count as visits, stitching unavailable.
- Two anonymous ids for one contact (phone then laptop): both linked in `attr_identity`; first touch is the earliest across devices.
- UTM with unusual casing or spaces: normalised lowercase and trimmed before classification.
- Bot traffic: known bot UA list drops events before storage; suspicious bursts flagged in the report.
- Contact deleted or exported (`migration/export`): events anonymised by nulling `contact_id`, not deleted.
- Referrer stripped by browser policy: classified as direct, counted separately as "direct (unknown referrer)".

**Dependencies**

`growth/crm-model` (hard). `growth/landing-forms` (embed hook), `tables/query-compiler`, `tables/dashboard-blocks`, `business-core/stripe-billing` (revenue join, soft), `growth/referral-program` (affiliate channel, soft). Decision on Umami/PostHog vs own table from `growth/growth-research`.

**Agent**

Built by Beacon (CRM Builder) with Nova (Views Engineer) for rollups and views. Reviewed by Sentinel (Security Auditor for privacy, Edge Case Hunter) and Ledger for revenue join semantics.

**Size**

M: collector, SDK and rollups are compact; the view reports reuse the engine.
