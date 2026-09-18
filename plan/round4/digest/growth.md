# Round 4 digest: Growth: Marketing, Outreach & CRM (`growth`)

Benchmarks: HubSpot (CRM, Marketing Hub, Service Hub), Attio, Twenty CRM, Pipedrive, Mailchimp, Listmonk, Customer.io, Buffer, Postiz, Intercom, Chatwoot, Cal.com, Dub, PostHog and GA4, Formbricks (NPS), Twilio (SMS, WhatsApp), Webflow

Feature matrix: 51 rows (26 covered, 8 partial, 17 gap). New issues: 23 (4 children, 19 gap issues; 20 deferred to v0.2). Amendments: 8. Cross-project suggestions: 5.

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| CRM entities: contacts, companies, leads, deals, pipelines, activities, tags | covered | PAP-187, r4/growth/crm-schema-routers-page-specs | Schema half split out as a child |
| Consent records, suppression list, preference centre, double opt-in | partial | PAP-187, r4/growth/consent-compliance-centre | Inline WP0; now a child |
| Pipeline kanban, contacts grid, detail pages | covered | PAP-189 |  |
| Tasks, follow-ups, My Day, reminders | gap | r4/growth/crm-tasks-followups-my-day | task kind exists, no surface |
| Duplicate detection and merge | gap | r4/growth/contact-company-merge-and-dedup | Referenced by five specs |
| Email logging and mailbox sync (Gmail, Outlook) | gap | r4/growth/email-sync-gmail-outlook |  |
| Meetings and booking pages | gap | r4/growth/booking-pages-and-availability | PAP-352 decides Cal.com mode |
| Deal products and quotes from deals | gap | r4/growth/deal-products-and-quotes | Needs the finance item catalogue |
| Sales dashboard, funnel, forecast | partial | PAP-189, r4/growth/sales-dashboard-and-forecast | PAP-189 stops at pipeline value |
| Lead scoring and routing, SLA on new leads | gap | r4/growth/lead-scoring-and-routing |  |
| Contact and company enrichment, email verification | gap | r4/growth/contact-enrichment-port |  |
| Custom fields on CRM records | covered | PAP-187, PAP-164 | via `custom jsonb` and tables field types |
| Record detail, timeline, comments, attachments | covered | PAP-333, PAP-189 |  |
| Segments from CRM, usage and billing | covered | PAP-195 | Deferred v0.2 |
| Outreach sequences (email, SMS), provider adapters | covered | PAP-404 |  |
| Send-time compliance, warmup, STOP, bounces, replies | covered | PAP-405 |  |
| Sequence builder, template editor, domain wizard | covered | PAP-406 |  |
| One-off email broadcasts and newsletters | gap | r4/growth/email-broadcast-campaigns | Sequences are drip only |
| Open and click engagement tracking | gap | r4/growth/email-engagement-tracking |  |
| Deliverability: DKIM, SPF, DMARC, warmup | covered | PAP-370, PAP-405 | Email package in data-layer |
| Transactional email package and sandbox mode | covered | PAP-370 |  |
| Outbound sandbox proof for reviewers (email, SMS, social, webhooks) | partial | PAP-370, r4/growth/outbound-sandbox-ledger | Email only today; SMS and social attempts not recorded in one place |
| Social scheduler: schema, approval, composer, calendar | covered | PAP-401 |  |
| Social adapters and publishing worker | covered | PAP-402, PAP-403 |  |
| Social analytics and best-time suggestions | partial | PAP-402, r4/growth/social-analytics-report | Metrics fetched, no report |
| Social inbox: comments and DMs | gap | - | PAP-190 out; v0.3, no issue this round |
| Content agent drafting posts and emails | covered | PAP-192 |  |
| Landing pages and Webflow publishing | covered | PAP-193, r4/growth/webflow-landing-publisher-and-editor | Split into two children |
| Lead capture forms and embed | covered | PAP-193, r4/growth/lead-forms-embed-and-submit-pipeline | Child |
| Experiments and A/B tests | gap | r4/growth/experiments-and-ab-tests | Excluded by PAP-193 and PAP-192 |
| Attribution: UTM, referral, funnel, privacy-first collector | covered | PAP-194 | Revenue join needs amendment |
| Short links and QR codes | gap | r4/growth/short-links-and-qr | PAP-188 hypothesises Dub |
| Referral and affiliate programs with payouts | covered | PAP-407, PAP-408, PAP-409 | Deferred; scope clarification amendment |
| Shared support inbox: email parsing, threading | covered | PAP-410 |  |
| Portal chat widget and internal notes | covered | PAP-411 |  |
| Three-pane inbox, macros, metrics | covered | PAP-412 |  |
| Help center and knowledge base | gap | r4/growth/help-center-knowledge-base | PAP-197 out |
| AI reply drafts and FAQ bot with handoff | gap | r4/growth/support-ai-reply-drafts | PAP-197 out (auto-replies); drafts only |
| SLA policies and business hours | partial | PAP-197, r4/growth/support-sla-and-business-hours | `sla jsonb` stored, no policy |
| CSAT, NPS and review requests | gap | r4/growth/nps-csat-and-review-requests |  |
| In-app messages and announcements targeted by segment | gap | r4/growth/in-app-messages-and-announcements | PAP-195 demo assumes it |
| WhatsApp channel | gap | - | v0.3 via Twilio; no issue this round |
| Web push notifications | partial | PAP-381, PAP-136 | Realtime push transport; marketing use v0.3 |
| Consent for cookies and privacy pages | covered | PAP-221 | Identity project |
| DSAR export of CRM and consent data | covered | PAP-221, r4/growth/consent-compliance-centre |  |
| CRM import from spreadsheets and HubSpot | covered | PAP-200, PAP-413 | Migration project |
| Contract package, conformance, kernel wiring | covered | PAP-485, PAP-488, PAP-491 |  |
| Stack survey and ADR (Twenty, Postiz, Listmonk, Dub, Chatwoot) | covered | PAP-188, PAP-351 |  |
| Campaign hub grouping posts, emails, pages with budget | partial | PAP-401, r4/growth/email-broadcast-campaigns | `social_campaign` and `campaign`; unified hub v0.3 |
| Portal customer to contact identity link | partial | r4/growth/crm-schema-routers-page-specs | `crm_contact.user_id` added in the child |
| Agent guardrails: draft only, approval hash, no live sends | covered | PAP-401, PAP-192, PAP-298 |  |

## New issues

| Key | Title | Parent | Size | Model / effort | Prio | Deferred | Milestone |
|---|---|---|---|---|---|---|---|
| `r4/growth/crm-schema-routers-page-specs` | CRM schema, routers, datasets, search registrations and the three page specs (the schema half of PAP-187) | PAP-187 | M (3) | Sonnet 5 / high | 2 | no | CRM core |
| `r4/growth/consent-compliance-centre` | Consent and marketing compliance centre: consent records per channel and purpose, shared suppression list, canContact, public preference and one-click unsubscribe routes, double opt-in | PAP-187 | M (3) | Opus 5 / high | 2 | no | CRM core |
| `r4/growth/outbound-sandbox-ledger` | Outbound sandbox ledger: one record of every email, SMS, social post and webhook the growth module would send, with the gate decision, for sandbox-only verification | - | S (2) | Sonnet 5 / medium | 2 | no | Campaigns and social |
| `r4/growth/lead-forms-embed-and-submit-pipeline` | Lead forms: form builder, 8 KB embed script, public submit endpoint with spam scoring and rate limits, lead upsert with UTM and consent, submissions grid | PAP-193 | M (3) | Sonnet 5 / high | 4 | yes | Campaigns and social |
| `r4/growth/webflow-landing-publisher-and-editor` | Landing page editor and Webflow publisher: block content model, CMS collection mapping, site publish with a GitHub Pages fallback, approval before publish | PAP-193 | M (3) | Sonnet 5 / medium | 4 | yes | Campaigns and social |
| `r4/growth/crm-tasks-followups-my-day` | CRM tasks and follow-ups: task activities with due dates and assignees, snooze, recurring follow-ups, My Day view and due reminders | - | M (3) | Sonnet 5 / medium | 4 | yes | CRM core |
| `r4/growth/contact-company-merge-and-dedup` | Contact and company merge and duplicate detection: fuzzy duplicate candidates, side-by-side merge with field pick, external ref and consent re-pointing, undo window | - | M (3) | Sonnet 5 / high | 4 | yes | CRM core |
| `r4/growth/email-sync-gmail-outlook` | Email logging and mailbox sync: BCC-to-CRM address, Gmail and Microsoft Graph OAuth sync of threads with matched contacts, send-from-CRM with the rep's own mailbox | - | M (3) | Opus 5 / high | 4 | yes | Acquisition analytics |
| `r4/growth/booking-pages-and-availability` | Booking pages and availability: public scheduling links with availability rules, Google and Microsoft calendar busy-time checks, meeting activities, reminders and reschedule links | - | M (3) | Sonnet 5 / high | 4 | yes | Acquisition analytics |
| `r4/growth/email-broadcast-campaigns` | Email broadcast campaigns: one-off sends to a segment with template editor, send-time scheduling, subject-line test, per-campaign stats and compliance gates | - | M (3) | Sonnet 5 / high | 4 | yes | Campaigns and social |
| `r4/growth/email-engagement-tracking` | Email engagement tracking: privacy-respecting open pixel and click wrapping with per-tenant toggle, bot filtering, activity and segment feeds | - | S (2) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/lead-scoring-and-routing` | Lead scoring and routing: fit and engagement score rules, lifecycle promotion thresholds, round-robin and territory assignment, SLA timer on new leads | - | M (3) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/contact-enrichment-port` | Contact and company enrichment port: provider adapter interface with a fixture adapter, domain-based company enrichment, email verification, consent-aware field writes and cost caps | - | S (2) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/short-links-and-qr` | Short links and QR codes: first-party /l/:code redirects with click attribution, optional Dub adapter, UTM builder and printable QR for offline campaigns | - | S (2) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/nps-csat-and-review-requests` | NPS and CSAT surveys and review requests: one-question surveys after resolved conversations and paid invoices, response capture, detractor alerts and Google or Yelp review links | - | M (3) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/help-center-knowledge-base` | Public help center: articles from the docs engine with categories, search, portal embed, article suggestions in the support widget and deflection metrics | - | M (3) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/support-ai-reply-drafts` | Support AI reply drafts and FAQ bot: grounded suggested replies for staff, a help-center-grounded first response in the widget with human handoff, never auto-sent | - | M (3) | Sonnet 5 / high | 4 | yes | Acquisition analytics |
| `r4/growth/support-sla-and-business-hours` | Support SLA policies and business hours: first-response and resolution targets per priority, business-hour calendars, breach warnings and escalation to a manager or Linear | - | S (2) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/in-app-messages-and-announcements` | In-app messages and announcements: banner, modal and tooltip messages targeted by segment and route, scheduling and approval, frequency caps and view or dismiss stats | - | M (3) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/experiments-and-ab-tests` | Experiments and A/B tests: deterministic assignment by anonymous or contact id, variants for landing blocks, email subjects and in-app messages, conversion goals from attribution and significance readout | - | M (3) | Sonnet 5 / high | 4 | yes | Acquisition analytics |
| `r4/growth/deal-products-and-quotes` | Deal products and quote from deal: line items on deals from the finance item catalogue, amount roll-up, one-click quote creation and acceptance syncing the deal to Won | - | M (3) | Sonnet 5 / medium | 4 | yes | CRM core |
| `r4/growth/sales-dashboard-and-forecast` | Sales dashboard and forecast: pipeline funnel, win rate, velocity, weighted forecast by stage probability, activity leaderboard and stale-deal alerts as dashboard blocks | - | M (3) | Sonnet 5 / medium | 4 | yes | Acquisition analytics |
| `r4/growth/social-analytics-report` | Social analytics report: per-post and per-account metrics history, engagement rate by platform and time slot, best-time suggestions in the composer and a campaign roll-up block | - | S (2) | Sonnet 5 / medium | 4 | yes | Campaigns and social |

## Amendments to existing specs

* **PAP-194** (Spec): Round 4 clarification: the revenue join must use tenant revenue, not PaperOS platform billing. Join `attr_touch.contact_id` to `fin_party` (via `crm_contact.party_id` from `r4/growth/crm-schema-routers-page-specs`) and sum `invoice.paid` postings from PAP-397 and connected charges from PAP-181; PAP-177 subscriptions are PaperOS's own revenue and belong only to the platform-admin funnel (PAP-367 `/admin/onboarding`).
* **PAP-407** (Spec): Round 4 clarification: two referral modes exist. Tenant mode (v0.2 scope) attributes a tenant's own customers: 'signup' is portal registration (PAP-62, PAP-64) and 'first payment' is `invoice.paid` from PAP-397 or a connected charge from PAP-181. Platform mode (PaperOS recruiting tenants through PAP-57 signup and PAP-177 Checkout) reuses the same tables with `scope: platform` and is enabled only for the PaperOS demo tenant.
* **PAP-402** (Definition of done): Round 4: the merge gate is the mock-adapter worker run plus X `validate` unit tests and a recorded (`nock`) publish fixture; the single real X publish is optional evidence, requires the NJ item for the X developer account and the tenant's live flag, and is reported as `skipped: no-credentials` otherwise (Security Model section 4 forbids live publishing outside an approved queue item). Record the attempt in `r4/growth/outbound-sandbox-ledger`.
* **PAP-404** (Definition of done): Round 4: CI passes with `noop` providers and recorded Resend and Twilio fixtures; the sandbox delivery to allowlisted addresses is attached when `RESEND_TEST_KEY` and `TWILIO_TEST_SID` exist, otherwise `skipped: no-credentials`. Every attempt is written to `r4/growth/outbound-sandbox-ledger` so reviewers can prove nothing left the allowlist.
* **PAP-410** (Definition of done): Round 4: the 30 fixture emails are the gate; the real staging round trip is attached when the mailbox DNS (NJ) exists and is otherwise `skipped: no-credentials`. Inbound fixtures must include one message with a prompt-injection payload in the body and assert it is wrapped as T3 untrusted content before any agent (PAP-192, `r4/growth/support-ai-reply-drafts`) reads it.
* **PAP-195** (Spec): Round 4: `useInSegment` resolves the current portal user's contact through `crm_contact.user_id` (added by `r4/growth/crm-schema-routers-page-specs`), falling back to `fin_party.user_id` and then email match; the resolution is cached per session and invalidated on `crm.contact.updated`. In-app targeting UI for marketers lives in `r4/growth/in-app-messages-and-announcements`; this issue ships only the hook and the demo banner.
* **PAP-192** (Edge cases): Round 4: changelog entries, spec files and docs the agent reads are T2 or T3 content under the Security Model prompt-injection tiers; wrap them with `<untrusted source= tier=>` and run the scanner before drafting. A draft that quotes an instruction-shaped line from a source is dropped and the source line is reported in the session comment.
* **PAP-197** (Dependencies): Round 4: help center articles (`r4/growth/help-center-knowledge-base`), SLA policies (`r4/growth/support-sla-and-business-hours`) and AI reply drafts (`r4/growth/support-ai-reply-drafts`) extend this umbrella after its three children and depend on PAP-411 and PAP-412; none blocks the children.

## Cross-project suggestions

* **business-core**: Expose `documents.create|accept` and `ItemPicker` through `@paperos/contract-business-core` for deal quotes — `r4/growth/deal-products-and-quotes` must create quotes and pick items via kernel-resolved ports; the contract (PAP-484) should list `DocumentPort.createFromLines` and the picker slot explicitly.
* **collab**: Public rendering mode for the docs engine (unauthenticated, tenant-branded, `noindex` per page) — The help center (`r4/growth/help-center-knowledge-base`) needs PAP-128 or PAP-379 to render selected docs publicly with search; today both assume an authenticated console.
* **identity**: Portal registration writes a `crm.contact.created`-compatible event with `user_id` — Tenant-mode referrals (PAP-407 amendment), surveys and in-app messages need the portal signup to link the new user to a CRM contact; PAP-62 owns the signup flow.
* **libraries**: Decide the enrichment and email-verification vendor set (Clearbit, Apollo, Hunter, OSS MX) in the registry — `r4/growth/contact-enrichment-port` ships adapters in `dryRun`; the Scout rubric should score cost per lookup, data-protection terms and sandbox access before any key is requested.
* **realtime**: Push transport as the carrier for marketing web push — PAP-381 is engineered for job progress; in-app messages and campaign channels would reuse it for opt-in web push in v0.3 if the transport exposes a per-user topic API.

## What was missing and why it matters

1. PAP-187 carried both the schema every growth issue waits on and the consent centre as an inline work package; as one L it could not be claimed cleanly, so both are now children with their own blockers and the portal identity link (`crm_contact.user_id`) three specs assumed.
2. Nothing recorded, in one place, what the module tried to send and why it was allowed; every Definition of done depended on live sends the deny list forbids, so an outbound sandbox ledger and four DoD amendments make the growth stack provable in CI.
3. The CRM had a pipeline and no daily workflow: tasks, merge and dedupe, mailbox sync, booking and a sales dashboard are the features people judge a CRM by in the first week.
4. Marketing stopped at drip sequences: one-off broadcasts, engagement tracking, lead scoring, short links, in-app messages and experiments are what turn attribution data into decisions.
5. Support stopped at the inbox: a help center, grounded AI drafts that never auto-send, SLA policies and NPS close the service loop that referrals and reviews depend on; three cross-cutting confusions between platform billing and tenant revenue (PAP-194, PAP-407) are corrected by amendment.
