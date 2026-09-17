---
identifier: "PAP-194"
title: "Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-163", "PAP-187", "PAP-304", "PAP-337"]
blocks: []
key: "growth/attribution"
url: "https://linear.app/paperos/issue/PAP-194/track-acquisition-analytics-utm-referral-funnel-with-a-privacy-first"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:32.030Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-194: Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Know which channel, campaign and page produced each lead, signup and paying customer without a third-party tracker: a first-party cookieless event pipeline that records UTM and referral touches, stitches anonymous visitors to contacts on identify, and renders channel, campaign, funnel and landing-page reports as views.

**Scope**

In: `packages/growth/src/attribution/schema.ts` (`attr_event` partitioned monthly, `attr_identity`, `attr_touch`, `attr_funnel`, `attr_daily` rollups); collector `POST /api/v1/public/collect`; client SDK `client.ts` under 4 KB gzipped wired into `apps/web` and `form.js`; `channels.yaml` classification rules; report views and dashboard blocks; consent handling (GPC, DNT, tenant consent mode).

Out: session replay, heatmaps, ad platform conversion APIs, multi-touch models beyond first and last.

**Spec**

* `attr_event (id uuidv7, tenant_id, anonymous_id, contact_id?, user_id?, name, properties jsonb, utm jsonb, referrer_host, landing_path, session_id, device_class, occurred_at)`; `attr_identity (anonymous_id -> contact_id|user_id, linked_at, method)`; `attr_touch (contact_id, first|last, channel, campaign, source, medium, content, term, at)`.
* Collector: batches up to 50 events and 32 KB, CORS to registered origins, no cookies, 120 events per minute per `anonymous_id`; UA reduced to `device_class`, IP folded into the `session_id` salt and discarded.
* SDK: `track(name, props)`, `page()`, `identify(contactOrUser)`, UTM and referrer auto-capture on first page, offline buffer in `localStorage`.
* Event names `page_viewed`, `form_submitted`, `lead_created`, `signup_completed`, `subscription_started`, `custom.*`.
* Identify stitching attributes prior events with that `anonymous_id`; first touch is the earliest UTM or referrer, last touch the latest before conversion.
* Rollups `attr_daily` refreshed by a PAP-43 job every 15 minutes; reports compile through PAP-163; revenue joins PAP-177 invoices via `crm_company.billing_customer_id`, unmatched shown as "Unattributed revenue".
* Retention: raw events 13 months by partition drop; touches indefinite; `essential-only` consent mode disables stitching.

**Interface contract**

Provides: SDK `@paperos/attribution` (`track`, `page`, `identify`), collector route, `classifyChannel(utm, referrer)`, datasets `attr.channels|campaigns|funnel|landingPages`, number blocks `attr.visits|leads|customers`, event `attr.contact.identified`, `attr_event` counts exposed to PAP-195 segment clauses. Consumes: contacts (PAP-187), `lead.created` and `form.js` hook (PAP-193), compiler and dashboards (PAP-163, PAP-173), jobs (PAP-43), invoices (PAP-177, soft), referral codes (PAP-196, soft), rate limiting (PAP-267), decision on Umami/PostHog versus own table (PAP-188).

**Definition of done**

* Vitest, Playwright, load test and privacy review below green.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the channel report and funnel view.
* `docs/growth/attribution.md` (event names, channel rules, privacy stance); CHANGELOG; Linear comment with report screenshots and the load summary.

**Test plan**

* Unit: channel classification against 40 referrer and UTM fixtures including odd casing; stitching across two anonymous ids; first and last touch; batch limits; bot UA drop list.
* Integration: rollup equals raw aggregation on a 100k-event fixture; partition drop removes month 14; `essential-only` mode never writes `attr_identity`.
* E2E: land with UTM, submit the mock form, sign up, see touches on the contact detail and the channel report after a forced rollup.
* Load: k6 at 1,000 events per second for five minutes on staging, p95 ingest under 100 ms.
* Visual: matrix above.

**Demo**

Reviewer opens the demo site with `?utm_source=newsletter&utm_campaign=sept`, submits the form, signs up, then opens the contact page to see first and last touch and `/marketing/attribution` where the newsletter row shows one lead. Under two minutes.

**Edge cases**

* `localStorage` blocked: per-load `anonymous_id`, visits counted, no stitching.
* Phone then laptop: both ids linked, earliest first touch wins.
* Bot bursts dropped before storage and flagged in the report.
* Contact erased (PAP-221): events keep `contact_id` null, never deleted.
* Referrer stripped: "direct (unknown referrer)".

**Dependencies**

PAP-187 (hard), PAP-163 (hard), PAP-193 (embed hook), PAP-173, PAP-43, PAP-177 and PAP-196 (soft), PAP-188. Feeds PAP-195, PAP-197 metrics.

**Agent**

Builder: Beacon (CRM Builder) with Nova on rollups and views. Reviewer: Sentinel (Security Auditor for privacy, Edge Case Hunter), Ledger for the revenue join.

**Size**

M: collector, SDK and rollups are compact; reports reuse the engine.
