# Rewritten specs for growth PAP-193..PAP-197.
SPECS = {}
def add(k, **s): SPECS[k] = s

add("PAP-193",
Goal="""Close the loop from marketing page to CRM record: publish landing pages to the tenant's Webflow site through the Data API, embed a PaperOS form on them, and capture every submission as a `crm_lead` with UTM attribution, spam filtering and notification, so campaigns produce leads without manual export.""",
Scope="""In: `packages/growth/src/landing/schema.ts` (`landing_page`, `lead_form`, `form_submission`); Webflow integration (`webflow-api` 3.x, OAuth per tenant, CMS collection "Landing Pages", site publish) with a GitHub Pages fallback (PAP-15); embed script `form.js` under 8 KB gzipped served at `/embed/forms/<id>.js`; public endpoint `POST /api/v1/public/forms/<id>/submit`; submission pipeline; editors for pages and forms; submissions grid; Webflow settings.

Out: full visual page builder, A/B tests, Designer API extensions, payments on pages.""",
Spec="""* `landing_page (title, slug, webflow_site_id, webflow_page_id, webflow_item_id, status: draft|pending_approval|published|archived, content jsonb blocks, seo jsonb, form_id, published_at)`; `lead_form (name, fields jsonb, success_action, notify_user_ids, honeypot_field, recaptcha: none|turnstile, allowed_origins[])`; `form_submission (form_id, payload jsonb, lead_id, utm jsonb, referrer, ip_hash, user_agent_class, spam_score, status: accepted|spam|error)`.
* The submit endpoint is the only unauthenticated write besides PAP-169 forms: CORS to `allowed_origins`, 20 per minute per IP via PAP-267 rate limiting, 64 KB body, client nonce idempotency for five minutes.
* Pipeline: validate against `fields`, honeypot, optional Turnstile, spam score (disposable domains, link count), upsert `crm_lead` by email, attach UTM from hidden fields and `document.referrer`, write consent through {{gap/growth/consent-centre}} when the consent box is ticked, emit `lead.created`.
* Field types text, email, phone, select, checkbox, textarea, hidden; email and phone validated server-side.
* Publishing needs `landing.publish`; agent drafts stop at `pending_approval`; CMS field mapping stored per site; publish idempotent by `webflow_item_id`.
* `ip_hash` is SHA-256 with a tenant salt; raw IP never stored.""",
Contract="""Provides: `landing.pages.*`, `landing.drafts.create` (for PAP-192), `landing.forms.*`, `form.js` embed contract (`data-form-id`, success callbacks), public submit route, event `lead.created { leadId, formId, utm }` consumed by PAP-194 and PAP-136 core, `form_submission` dataset. Consumes: `crm_lead` and consent (PAP-187, {{gap/growth/consent-centre}}), public route pattern and rate limiting (PAP-267), Pages fallback (PAP-15), notifications (PAP-136 core), drag reorder (PAP-155), attribution client hook (PAP-194), Webflow OAuth app (Needs Justin).""",
DoD="""* Vitest, integration and Playwright below green; `form.js` size budget enforced in CI; works in Chromium, WebKit and Firefox projects.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for editor, form builder and a published page.
* `docs/growth/landing-forms.md` with Webflow setup; CHANGELOG; Linear comment with the live page URL.""",
Test="""* Unit: field validation, spam scoring fixtures, lead upsert by email, UTM extraction and normalisation, CORS and rate-limit middleware, CMS mapping rename safety.
* Integration: publish to the connected Webflow staging site and submit from the live page (recording); Pages fallback publishes static HTML; archived form returns 410; disallowed origin returns 403 with a settings hint in the log.
* E2E: build page, build form, publish, submit, see the lead on the PAP-189 contacts grid with its UTM.
* Visual: matrix above plus the embed rendered inside a third-party test page.""",
Demo="""Reviewer publishes the demo landing page, opens the live Webflow URL, submits the embedded form with a UTM-tagged link, then opens `/crm/contacts` to see the new lead with source and campaign filled. Under two minutes.""",
Edge="""* Webflow quota exceeded: `pending_publish` with retry and banner.
* Double submit: nonce idempotency.
* Email matches an existing customer: lead created and linked, contact untouched.
* Turnstile down: accept with flag when the honeypot passes; flagged rows reviewed in the grid.
* Page embedded on a non-allowlisted origin: 403 logged.""",
Deps="""PAP-187 (hard), PAP-35 children (hard, public route pattern), PAP-15 (fallback), PAP-136 core, PAP-155, {{gap/growth/consent-centre}} (soft), Webflow account (Needs Justin). Feeds PAP-194; receives drafts from PAP-192.""",
Agent="""Builder: Beacon (Campaign Composer for editors, CRM Builder for the pipeline). Reviewer: Sentinel (Security Auditor for the public endpoint, Visual Inspector), Quill.""",
Size="""M: one external API, one public endpoint, an embed script and two editors.""")

add("PAP-194",
Goal="""Know which channel, campaign and page produced each lead, signup and paying customer without a third-party tracker: a first-party cookieless event pipeline that records UTM and referral touches, stitches anonymous visitors to contacts on identify, and renders channel, campaign, funnel and landing-page reports as views.""",
Scope="""In: `packages/growth/src/attribution/schema.ts` (`attr_event` partitioned monthly, `attr_identity`, `attr_touch`, `attr_funnel`, `attr_daily` rollups); collector `POST /api/v1/public/collect`; client SDK `client.ts` under 4 KB gzipped wired into `apps/web` and `form.js`; `channels.yaml` classification rules; report views and dashboard blocks; consent handling (GPC, DNT, tenant consent mode).

Out: session replay, heatmaps, ad platform conversion APIs, multi-touch models beyond first and last.""",
Spec="""* `attr_event (id uuidv7, tenant_id, anonymous_id, contact_id?, user_id?, name, properties jsonb, utm jsonb, referrer_host, landing_path, session_id, device_class, occurred_at)`; `attr_identity (anonymous_id -> contact_id|user_id, linked_at, method)`; `attr_touch (contact_id, first|last, channel, campaign, source, medium, content, term, at)`.
* Collector: batches up to 50 events and 32 KB, CORS to registered origins, no cookies, 120 events per minute per `anonymous_id`; UA reduced to `device_class`, IP folded into the `session_id` salt and discarded.
* SDK: `track(name, props)`, `page()`, `identify(contactOrUser)`, UTM and referrer auto-capture on first page, offline buffer in `localStorage`.
* Event names `page_viewed`, `form_submitted`, `lead_created`, `signup_completed`, `subscription_started`, `custom.*`.
* Identify stitching attributes prior events with that `anonymous_id`; first touch is the earliest UTM or referrer, last touch the latest before conversion.
* Rollups `attr_daily` refreshed by a PAP-43 job every 15 minutes; reports compile through PAP-163; revenue joins PAP-177 invoices via `crm_company.billing_customer_id`, unmatched shown as "Unattributed revenue".
* Retention: raw events 13 months by partition drop; touches indefinite; `essential-only` consent mode disables stitching.""",
Contract="""Provides: SDK `@paperos/attribution` (`track`, `page`, `identify`), collector route, `classifyChannel(utm, referrer)`, datasets `attr.channels|campaigns|funnel|landingPages`, number blocks `attr.visits|leads|customers`, event `attr.contact.identified`, `attr_event` counts exposed to PAP-195 segment clauses. Consumes: contacts (PAP-187), `lead.created` and `form.js` hook (PAP-193), compiler and dashboards (PAP-163, PAP-173), jobs (PAP-43), invoices (PAP-177, soft), referral codes (PAP-196, soft), rate limiting (PAP-267), decision on Umami/PostHog versus own table (PAP-188).""",
DoD="""* Vitest, Playwright, load test and privacy review below green.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the channel report and funnel view.
* `docs/growth/attribution.md` (event names, channel rules, privacy stance); CHANGELOG; Linear comment with report screenshots and the load summary.""",
Test="""* Unit: channel classification against 40 referrer and UTM fixtures including odd casing; stitching across two anonymous ids; first and last touch; batch limits; bot UA drop list.
* Integration: rollup equals raw aggregation on a 100k-event fixture; partition drop removes month 14; `essential-only` mode never writes `attr_identity`.
* E2E: land with UTM, submit the mock form, sign up, see touches on the contact detail and the channel report after a forced rollup.
* Load: k6 at 1,000 events per second for five minutes on staging, p95 ingest under 100 ms.
* Visual: matrix above.""",
Demo="""Reviewer opens the demo site with `?utm_source=newsletter&utm_campaign=sept`, submits the form, signs up, then opens the contact page to see first and last touch and `/marketing/attribution` where the newsletter row shows one lead. Under two minutes.""",
Edge="""* `localStorage` blocked: per-load `anonymous_id`, visits counted, no stitching.
* Phone then laptop: both ids linked, earliest first touch wins.
* Bot bursts dropped before storage and flagged in the report.
* Contact erased (PAP-221): events keep `contact_id` null, never deleted.
* Referrer stripped: "direct (unknown referrer)".""",
Deps="""PAP-187 (hard), PAP-163 (hard), PAP-193 (embed hook), PAP-173, PAP-43, PAP-177 and PAP-196 (soft), PAP-188. Feeds PAP-195, PAP-197 metrics.""",
Agent="""Builder: Beacon (CRM Builder) with Nova on rollups and views. Reviewer: Sentinel (Security Auditor for privacy, Edge Case Hunter), Ledger for the revenue join.""",
Size="""M: collector, SDK and rollups are compact; reports reuse the engine.""")

add("PAP-195",
Goal="""Let staff define audiences once and use them everywhere: segments built from CRM fields, product usage events and billing state through the shared filter builder, evaluated dynamically or frozen, and exposed to outreach, social campaigns, notifications and in-app targeting through one `segments.membersOf` API.""",
Scope="""In: extend `crm_segment` (`definition: FilterTree` over a virtual "audience" source joining contacts, companies, deal aggregates, `attr_event` counts, entitlements and login recency; `refresh: realtime|hourly|manual`; `size_estimate`; `definition_version`); evaluator `packages/growth/src/segments/evaluate.ts`; procedures `segments.*`; hook `useInSegment(key)`; consumers PAP-191, PAP-190, PAP-136; UI `_app/marketing/segments`.

Out: lookalike audiences, ad-audience sync, per-user flags outside segments.""",
Spec="""* Grammar extensions contributed through the PAP-279 extension hook and PAP-166 `extraOperators`: relative dates, `performed X at least N times in window`, `has deal with stage kind won`, `in segment S` (no cycles).
* Evaluation is set-based SQL compiled through PAP-163 producing `(tenant_id, segment_id, contact_id)`; incremental mode recomputes contacts touched since `last_evaluated_at` via `updated_at` and event watermarks; over 1M candidates batched at 50k with a progress row; one evaluation in flight per segment.
* `segments.preview(definition) -> { count, sample[] }` with `statement_timeout 2000`, returning `estimated: true` from `EXPLAIN` when exceeded.
* Membership changes emit `segment.entered|exited { segmentId, contactId }`.
* `segments.contains(contactId, segmentIds[])` indexed for in-app use under 20 ms; `useInSegment` resolves the current user's contact by email link and caches per session.
* Permissions `segment.read|write|use`; `use` allows selecting without seeing the definition.""",
Contract="""Provides: `segments.list|get|create|update|archive|preview|membersOf|contains|freeze`, `useInSegment(key)`, events `segment.entered|exited`, `SegmentRef` type accepted by `outreach.enrol` (PAP-191), campaign audience notes (PAP-190) and notification audience filters (PAP-136), "used by" registry `registerSegmentConsumer`. Consumes: `crm_segment` (PAP-187), `FilterBuilder` and extension hook (PAP-166, PAP-279), compiler (PAP-163), `attr_event` (PAP-194, operator hidden if absent), entitlements (PAP-178, soft), portal shell for the targeting demo (PAP-64), jobs (PAP-43).""",
DoD="""* Vitest, performance and Playwright below green; axe clean, builder keyboard-operable.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for list and builder.
* `docs/growth/segments.md` (operators, refresh modes, targeting hook); CHANGELOG; Linear comment with screenshots and bench numbers.""",
Test="""* Unit: compilation of each new operator, cycle detection for nested segments, enter and exit event derivation, `contains` correctness, version bump on definition change.
* Integration: incremental evaluation equals full evaluation on fixtures; 200k-contact bench with a five-clause segment under 10 s full and 1 s incremental; `contains` under 20 ms; coalesced manual refresh.
* E2E: build a three-clause segment including an event clause, watch the live count, freeze it, select it in a sequence, and see a portal banner gated by `useInSegment`.
* Visual: matrix above.""",
Demo="""Reviewer creates "Customers who viewed pricing twice in 30 days and have no open deal", sees the live count and sample, freezes it, opens a sequence and picks it as the audience, then logs in as a member on the portal and sees the targeted banner. Under two minutes.""",
Edge="""* Custom field deleted: definition invalid, evaluation paused, owner notified, members kept.
* Match then unmatch within one window: exit only if previously a member.
* Nested segment archived: parent invalid with a clear message.
* Staff without a contact: `useInSegment` returns false.
* Relative dates in tenant timezone, documented.""",
Deps="""PAP-187 (hard), PAP-166 (hard), PAP-163 (hard), PAP-194 (soft), PAP-178 (soft), PAP-64, PAP-43, PAP-279. Consumed by PAP-191, PAP-190, PAP-136.""",
Agent="""Builder: Beacon (CRM Builder) with Nova on compiler extensions. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter), Atlas for the shared grammar.""",
Size="""M: grammar extension, evaluator and one builder page.""")

add("PAP-196",
Goal="""Let customers and partners recruit customers: referral codes and affiliate links that attribute signups and paid conversions, calculate rewards (credit, discount or cash), pay cash through Stripe Connect transfers with ledger postings, with fraud checks and a portal referral page. Deferred per the round-2 audit: lowest priority, built only if P2 finishes early. Umbrella for three children.""",
Scope="""Children (same milestone, Backlog):

* {{growth/referral/codes-attribution}} (M) Programs, codes, `/r/{code}` route, attribution window, qualification worker on signup and `invoice.paid` events.
* {{growth/referral/rewards-payouts-ledger}} (M) Reward rules, fraud rules, approval, Connect transfers, ledger postings, monthly statements.
* {{growth/referral/portal-console-ui}} (S) Portal referral page, console programs and referrals grids, approval queue.

Out: multi-level marketing, coupon marketplaces, tax forms beyond storing Stripe's 1099 status, non-Stripe rails.""",
Spec="""Decisions binding all children:

* `referral_program (name, kind: referral|affiliate, reward jsonb { referrer, referee }, terms_url, status, daily_cap)`, `referral_code (program_id, owner_contact_id|owner_user_id, code, landing_url, clicks)`, `referral (code_id, referee_contact_id, referee_customer_id, status: clicked|signed_up|qualified|rewarded|rejected, qualified_at, fraud_flags jsonb)`, `referral_reward (referral_id, beneficiary, type, amount_minor, status: pending|approved|paid|voided, stripe_transfer_id, ledger_entry_id, paid_at)`, `affiliate_account (contact_id, stripe_connect_account_id, onboarding_status, tax_form_status, terms_version, accepted_at)`.
* Codes: 8-character Crockford base32, case-insensitive, vanity codes with a profanity filter; attribution window 30 days, last click wins unless a code was entered at checkout.
* Fraud: self-referral (domain plus payment fingerprint), disposable emails, more than 5 signups per `ip_hash` per day, refunded first invoice voids the reward; flags require staff review.
* Cash rewards `pending` until 30 days past the refund window, then `approved`; payouts through PAP-181 `createTransfer`; postings debit `marketing_referral` expense, credit `affiliate_payable`, then payable to cash; idempotent by `referral_reward.id`.""",
Contract="""Provides: `referrals.programs|codes|referrals|rewards.*`, route `/r/{code}`, `referralTokenFromRequest()` used by signup (PAP-57 children) and checkout (PAP-177), events `referral.qualified`, `referral.reward.paid`, channel `affiliate` for PAP-194, portal route `_portal/referrals`. Consumes: Connect transfers (PAP-181), billing webhooks (PAP-177), posting (PAP-179), statement PDFs (PAP-180, soft), portal shell (PAP-64), attribution click events (PAP-194), contacts (PAP-187).""",
DoD="""* All three children Done.
* Stripe test-mode integration: signup with code, first invoice paid, reward approved after a test-clock advance, transfer to a test Connect account; recording attached.
* Permission tests: customers see only their referrals; `referral.approve` required for payouts.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the portal page and approval queue.
* `docs/growth/referrals.md` with fraud and accounting notes reviewed by Ledger; CHANGELOG; Linear comment with recording.""",
Test="""Umbrella `referrals.e2e.spec.ts` with a test clock: click `/r/CODE`, sign up, pay the first invoice through `stripe trigger`, assert `qualified` and a `pending` reward; advance 31 days past the refund window and assert `approved`; approve payout as staff and assert the transfer id and balanced postings; refund the invoice and assert a negative reward netted against the next payout with a ledger reversal; run the fraud fixtures (self-referral, disposable email, 6 signups from one hash) and assert flags block payout.""",
Demo="""Reviewer copies their code from the portal referral page, signs up a second test user through the link, pays the first invoice with `4242`, then as staff approves the reward in the console queue and sees the Connect transfer and journal entry. Under two minutes.""",
Edge="""* Referee already a customer: `rejected` with a polite notice.
* Cash reward without a Connect account: stays `approved` with an onboarding CTA, voided after 180 days.
* Currency mismatch: converted at invoice-day rate, both stored.
* Public code hitting 1,000 signups a day: program cap pauses rewards, not signups.
* Transfer failure: reward back to `approved` with error and manual retry.""",
Deps="""PAP-181 (hard), PAP-177 (hard), PAP-179 (hard), PAP-180 (soft), PAP-64, PAP-194 (soft), PAP-187. Deferred: schedule only after every other P2 issue in growth and business-core is In Review.""",
Agent="""Builder: Beacon (CRM Builder) with Ledger (Payments Integrator) on Connect and postings. Reviewer: Sentinel (Security Auditor for fraud and money paths, Visual Inspector), Ledger (Bookkeeper) for accounting.""",
Size="""L, split into two M children and one S child; deferred.""")

add("PAP-197",
Goal="""Put every support conversation next to the customer record: a shared inbox receiving email (Resend inbound) and in-app chat from the portal, threaded into conversations linked to contacts and companies, with assignment, tags, replies, internal notes through the comments system, and history on contact and company pages. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{growth/support/email-threading}} Schema, inbound parsing with `mailparser`, quoted-history stripping, threading heuristics, HTML sanitising, contact matching, outbound replies with `Message-ID` threading.
* {{growth/support/chat-notes}} Portal `<SupportChat/>` widget with live sync and presence, unauthenticated email capture, internal notes on PAP-131 threads, status rules.
* {{growth/support/console-ui}} Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts, metrics rollup.

Out: phone, WhatsApp, public knowledge base, AI auto-replies, SLA escalation policies beyond a timer.""",
Spec="""Decisions binding all children:

* `support_mailbox (address, display_name, signature, auto_reply)`, `support_conversation (mailbox_id, contact_id, company_id, channel: email|chat, subject, status: open|pending|snoozed|resolved, assignee_user_id, priority, tags, snoozed_until, first_response_at, resolved_at, sla jsonb)`, `support_message (conversation_id, direction: inbound|outbound|note, author_id, author_kind, body_json, body_text, body_html_sanitised, attachments, provider_message_id unique, headers jsonb, delivered_at, read_at)`, `support_canned_reply`.
* Contact matching: exact email, then plus-address stripped, then domain to company only.
* Sanitiser allowlist: basic formatting, links with `rel="noopener"`, inline images rewritten to stored files; scripts and styles removed.
* Status rules: inbound reopens `resolved` within seven days else new conversation; outbound sets `pending`; inbound unsnoozes.
* Permissions `support.read|reply|assign|manage`; customers see only their conversations; agents may note, not reply.
* Every reply is a `crm_activity kind email`; every inbound event audited.""",
Contract="""Provides: `support.conversations|messages|mailboxes|cannedReplies.*`, inbound route `support.inbound`, `<SupportChat/>`, `<ConversationList contactId? companyId? />` embedded on PAP-189 detail pages, events `support.conversation.opened|resolved`, metrics rollup for a dashboard block. Consumes: contacts and activities (PAP-187), comments threads (PAP-131), record sync and presence (PAP-143, PAP-141, polling fallback), files (PAP-37), portal shell (PAP-64), outreach replies (PAP-191), commands (PAP-151), Resend inbound (provider per PAP-188), notifications (PAP-136 core).""",
DoD="""* All three children Done.
* Integration: a real email to the staging mailbox appears in the inbox, the reply arrives threaded in the sender's client (recording).
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for inbox, conversation and portal widget; axe clean; inbox keyboard-operable.
* `docs/growth/support.md` (mailbox setup, DNS, macros); CHANGELOG; Linear comment with recording.""",
Test="""Umbrella `support.e2e.spec.ts`: post 30 fixture inbound emails (Gmail, Outlook, Apple Mail quoting, one auto-reply, one duplicate webhook) and assert threading, stripped quotes, sanitised HTML, contact matching precedence and exactly one message per `provider_message_id`; reply from the console and assert the outbound `In-Reply-To`; send a portal chat message and assert it appears in the console within one second and the reply returns; add an internal note with a mention; snooze and reopen by an inbound message; assert first-response metrics in the rollup.""",
Demo="""Reviewer sends an email to the staging mailbox, watches it appear in the inbox linked to the seeded contact, replies with a macro using `r`, opens the portal as that customer to send a chat message and sees it land in the console live. Under two minutes.""",
Edge="""* Auto-reply loops: `Auto-Submitted` and `Precedence: bulk` honoured; never auto-reply to auto-replies.
* Attachment over 25 MB or blocked type: reference kept with a warning.
* Same email CC'd to two mailboxes: one conversation each, cross-linked.
* New address from a known customer: merge suggested manually.
* Chat from a company with three contacts links the individual.""",
Deps="""PAP-187 (hard), PAP-131 (hard), PAP-37 (hard), PAP-143 and PAP-141 (soft, polling fallback), PAP-64, PAP-191 (soft), PAP-151, PAP-136 core, mailbox DNS (Needs Justin).""",
Agent="""Builder: Beacon (CRM Builder) with Nova on live chat. Reviewer: Sentinel (Security Auditor for sanitisation and permissions, Visual Inspector, Edge Case Hunter for threading), Quill.""",
Size="""L, split into three M children.""")
