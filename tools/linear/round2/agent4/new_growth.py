# Children for growth L issues and the growth gap issue.
P = "growth"
CHILDREN = {}
GAPS = []
def child(parent, key, title, type_, size, **s):
    CHILDREN.setdefault(parent, []).append(dict(key=key, title=title, type=type_, size=size, sections=dict(s, Size=size + ": " + s.pop("SizeNote", "one session."))))
def gap(key, title, phase, type_, priority, surfaces, milestone, blockedBy, blocks, state="Backlog", **s):
    GAPS.append(dict(key=key, title=title, phase=phase, type=type_, priority=priority, surfaces=surfaces, milestone=milestone,
                     blockedBy=blockedBy, blocks=blocks, state=state, project=P, sections=s))

# ---------------- PAP-190 social ----------------
child("PAP-190", "growth/social/model-queue-calendar", "Social schema, approval state machine, composer with per-platform variants, approval queue and calendar", "Build", "M",
Goal="""Model posts and accounts, enforce the approval state machine, and give staff the composer, queue and calendar they plan from, before any adapter exists.""",
Scope="""In: `social/schema.ts`, `social.posts.*`, `social.accounts.list` (connect in sibling), composer with variant tabs and live limit counters, approval queue with diff of edits, calendar view bound to `social_post` (list fallback). Out: adapters, worker, OAuth (siblings).""",
Spec="""* Tables per the parent; transitions the only writes to `status`; approval stores `approved_hash`; edits after approval return to `pending_approval`.
* Composer previews platform-faithful cards from `packages/ui`; media via PAP-37; limits from `validatePost` (mock adapter limits until siblings land).
* `social.approve` for owner and admin only; agents create `pending_approval`.
* `scheduled_at` UTC, displayed in tenant timezone.""",
Contract="""Provides: schema, `social.posts.*`, `SocialPostStatus` machine, composer, queue, calendar route, `drafted_by` slot for PAP-192. Consumes: PAP-187, PAP-37, PAP-168 (soft), PAP-38.""",
DoD="""* State machine tests; Playwright draft, submit, approve, edit-returns-to-pending; screenshots at seven widths in light and dark; axe clean.""",
Test="""* Unit: transitions, hash binding, permission checks.
* E2E: the flow above; calendar and list fallback at 375 px.""",
Demo="""Write a post with two variants, submit it, approve as admin, see it on the calendar.""",
Edge="""* Past `scheduled_at` on approval asks to publish now; media over limits blocks scheduling.""",
Deps="""PAP-187, PAP-37 (hard), PAP-168 (soft). Blocks siblings.""",
Agent="""Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

child("PAP-190", "growth/social/adapter-mock-x", "Adapter interface, mock adapter, X API v2 adapter and the pg-boss publishing worker", "Build", "M",
Goal="""Publish for real on one platform through a worker that is safe against duplicates and rate limits, with a mock adapter the rest of the system tests against.""",
Scope="""In: `adapters/types.ts`, `adapters/mock.ts`, `adapters/x.ts` (`twitter-api-v2` 1.x), worker on pg-boss, metrics fetch. Out: the other four adapters (sibling).""",
Spec="""* Interface `validate`, `publish`, `fetchMetrics`, `refreshAuth`, `dryRun` flag.
* Worker: due `approved` posts to `publishing`, adapter call, `published` with external id and url, three retries with backoff, `failed`; `publishing` rows older than 10 minutes re-checked via `externalId` lookup before retry; 429 honours `Retry-After` and delays the account's other posts.
* Token revocation flags `reauth_required` and returns the post to `approved`.""",
Contract="""Provides: `SocialAdapter`, `adapters.mock`, `adapters.x`, `validatePost`, worker job `social.publish`, events `social.post.published|failed`. Consumes: model child, PAP-43 conventions, secrets (PAP-17).""",
DoD="""* Worker tests with the mock; one real X publish in `dryRun: false` recorded; metrics fetched.""",
Test="""* Unit: retry, duplicate protection, 429 handling, X `validate`.
* Integration: end-to-end publish with mock; one recorded real publish.""",
Demo="""Approve a post scheduled one minute ahead and watch the worker publish it via the mock, then show the X recording.""",
Edge="""* Worker crash mid-publish does not duplicate; account rate limit delays queue.""",
Deps="""Model child (hard), PAP-43, PAP-17, X developer account (Needs Justin).""",
Agent="""Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor).""",
SizeNote="one session.")

child("PAP-190", "growth/social/adapters-review-gated", "LinkedIn, Instagram, TikTok and YouTube adapters in dryRun with payload snapshots, OAuth connect flows and re-auth banners", "Build", "M",
Goal="""Implement the remaining adapters and account connection so they are ready the day each platform's app review clears, verified by payload snapshots meanwhile.""",
Scope="""In: `adapters/{linkedin,instagram,tiktok,youtube}.ts`, OAuth connect via Better Auth generic OAuth or SDK, encrypted token storage, refresh 24 hours before expiry, `reauth_required` banner, app-review checklist doc.""",
Spec="""* LinkedIn UGC posts; Instagram container then publish; TikTok Content Posting API; YouTube Data API v3 resumable upload with title under 100.
* Each adapter's `validate` encodes limits; `publish` in `dryRun` writes the exact request payload to a snapshot; live mode enabled per account by Justin.
* Tokens encrypted via {{security/field-encryption}} or PAP-17 helpers.""",
Contract="""Provides: four adapters, `social.accounts.connect|disconnect|refresh`, settings page, `docs/growth/social.md` checklist. Consumes: adapter child, PAP-57 OAuth plumbing, PAP-17, platform apps (Needs Justin).""",
DoD="""* Payload snapshots for all four; connect flow Playwright with a mocked provider; banner state; checklist filed as one Needs Justin item.""",
Test="""* Unit: `validate` per platform; payload snapshots.
* E2E: connect, expiry banner, disconnect.""",
Demo="""Connect a mocked LinkedIn account, schedule a post in `dryRun`, open the payload snapshot.""",
Edge="""* Expired refresh token surfaces banner without failing posts; disconnect keeps history.""",
Deps="""Adapter child (hard), PAP-57 children, PAP-17; app reviews (external, weeks).""",
Agent="""Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor).""",
SizeNote="ships in dryRun.")

# ---------------- PAP-191 outreach ----------------
child("PAP-191", "growth/outreach/model-worker", "Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency", "Build", "M",
Goal="""Send the right step to the right contact at the right time, exactly once, through pluggable providers.""",
Scope="""In: `outreach/schema.ts`, `providers/{types,resend,twilio}.ts`, worker (`SELECT ... FOR UPDATE SKIP LOCKED`), Handlebars-style rendering with an allowlist, sandbox recipient rewrite. Out: compliance, warmup, replies, UI (siblings).""",
Spec="""* Tables per the parent; `outreach_message` unique `(enrolment_id, step_id)`.
* Worker every minute: due enrolments, step conditions, render, send, record message and `crm_activity`; provider errors retried with backoff up to six hours then `failed`.
* Sandbox default rewrites non-allowlisted recipients to `sandbox+<hash>@paperos.test`.""",
Contract="""Provides: schema, `OutreachProvider`, `outreach.sequences|steps|templates|enrolments.*`, `outreach.enrol`, worker job `outreach.tick`. Consumes: PAP-187, PAP-43, PAP-17, PAP-188 decision.""",
DoD="""* Scheduler and rendering tests; one sandbox email and SMS delivered with test credentials, recorded.""",
Test="""* Unit: selection, conditions, rendering with missing variables, idempotency.
* Integration: test-clock run of a two-step sequence.""",
Demo="""Enrol an allowlisted contact and advance the test clock to see both messages with provider ids.""",
Edge="""* Template edited mid-sequence keeps `template_version`; daily cap rolls sends to the next window.""",
Deps="""PAP-187, PAP-43, PAP-17 (hard). Blocks siblings.""",
Agent="""Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Code Reviewer).""",
SizeNote="one session.")

child("PAP-191", "growth/outreach/compliance-warmup-replies", "Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection", "Build", "M",
Goal="""Make outbound lawful and deliverable: every send passes consent, suppression and quiet-hour checks, recipients can leave in one click, domains warm up automatically and replies stop sequences.""",
Scope="""In: send-time gate, List-Unsubscribe (RFC 8058) and footer, STOP and HELP keywords, TCPA quiet hours, warmup state machine on `sending_domain`, bounce and complaint handlers, inbound webhooks and reply matching (`In-Reply-To`, plus-address token, phone), "Unmatched" list. Out: UI (sibling).""",
Spec="""* Gate reads consent and `do_not_contact` (PAP-187) and the suppression list from {{gap/growth/consent-centre}} (stub with `do_not_contact` if absent).
* Quiet hours 8am to 9pm recipient local time; timezone fallback contact, company, tenant, logged on the message.
* Warmup caps 20, 50, 100, 250, 500, 1000; advance after three clean days; regress on bounce over 2 percent or complaints over 0.1 percent.
* Hard bounce sets `email_status: invalid` and stops enrolments; complaint adds to suppression; webhook signatures verified (`svix`, `X-Twilio-Signature`).""",
Contract="""Provides: `canSend(contact, channel) => { ok, reason }`, warmup job, inbound route, events `outreach.replied|bounced|unsubscribed`. Consumes: worker child, consent centre gap, PAP-187, PAP-197 (replies open conversations, soft).""",
DoD="""* Timezone fixtures for five zones; warmup advance and regression tests; STOP round trip in sandbox; three reply-matching strategies tested.""",
Test="""* Unit: gate reasons, quiet hours, warmup, matching.
* Integration: Resend inbound and Twilio STOP webhooks with signatures; replay idempotent.""",
Demo="""Send to a contact in a quiet-hours zone and watch it defer; reply from a mailbox and see the enrolment pause.""",
Edge="""* Forwarded reply from a different address lands in Unmatched; contact in two sequences capped at one send per day.""",
Deps="""Worker child (hard), consent centre gap (hard for suppression), PAP-187.""",
Agent="""Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Edge Case Hunter), Quill on compliance.""",
SizeNote="compliance logic.")

child("PAP-191", "growth/outreach/ui", "Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard", "Build", "M",
Goal="""Let staff build and run sequences without engineering help and see exactly what happened to each enrolment.""",
Scope="""In: builder (steps with delay editors, channel, template picker, conditions via PAP-166 `FilterBuilder`), template editor with live preview and test send to the allowlist, enrolments as a PAP-165 grid, domain wizard with DNS records and warmup status. Out: drafting (PAP-192).""",
Spec="""* Builder validates delays and channel mix; enrol by contacts or segment (PAP-195 `SegmentRef`).
* Template editor shows variables, renders a sample contact, blocks save on missing variables.
* Domain wizard polls `dns_status` and shows warmup stage and daily cap.""",
Contract="""Provides: routes `_app/marketing/outreach/*`, `<SequenceBuilder />`, `<TemplateEditor />`. Consumes: both siblings, PAP-166, PAP-165, PAP-195 (soft).""",
DoD="""* Playwright build, enrol, view enrolments; screenshots at seven widths in light and dark; axe clean.""",
Test="""* Unit: builder validation.
* E2E: the parent's umbrella flow through the UI.""",
Demo="""Build a two-step sequence, send a test email, enrol a contact, open the enrolments grid.""",
Edge="""* Unverified domain blocks activation with the wizard link; template with missing variable fails in preview.""",
Deps="""Both siblings (hard), PAP-166, PAP-165, PAP-195 (soft).""",
Agent="""Builder: Beacon (Campaign Composer). Reviewer: Sentinel (Visual Inspector).""",
SizeNote="one session.")

# ---------------- PAP-196 referral (deferred) ----------------
child("PAP-196", "growth/referral/codes-attribution", "Referral programs, codes, /r/{code} route, attribution window and the qualification worker", "Build", "M",
Goal="""Attribute signups and first payments to referral codes reliably, within a program's rules.""",
Scope="""In: `referral_program`, `referral_code`, `referral`; `/r/{code}` click route; `referralTokenFromRequest`; qualification worker on signup and `invoice.paid`. Out: rewards, payouts, UI (siblings). Deferred with the parent.""",
Spec="""* Codes 8-character Crockford base32, vanity codes with a profanity filter; 30-day window, last click wins unless a code was entered at checkout.
* Click route records an `attr_event` (PAP-194 channel `affiliate`), sets the token, redirects; signup (PAP-57 children) and Checkout (PAP-177) stamp `referral`.
* Worker moves `signed_up` to `qualified` on the first paid invoice.""",
Contract="""Provides: tables, `referrals.programs|codes.*`, route, `referralTokenFromRequest`, event `referral.qualified`. Consumes: PAP-194, PAP-57, PAP-177, PAP-187.""",
DoD="""* Code and window tests; worker tests; click to qualified in an integration test.""",
Test="""* Unit: code normalisation, precedence, window expiry.
* Integration: click, signup, `stripe trigger invoice.paid` yields `qualified`.""",
Demo="""Open `/r/DEMO123`, sign up, trigger payment, see `qualified`.""",
Edge="""* Existing customer as referee rejected; 1,000 signups a day pause rewards not signups (sibling).""",
Deps="""PAP-177, PAP-187, PAP-194 (soft), PAP-57 children. Blocks siblings.""",
Agent="""Builder: Beacon (CRM Builder). Reviewer: Sentinel.""",
SizeNote="deferred.")

child("PAP-196", "growth/referral/rewards-payouts-ledger", "Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements", "Build", "M",
Goal="""Turn qualified referrals into correct, fraud-checked rewards and pay cash rewards with balanced books.""",
Scope="""In: `referral_reward`, `affiliate_account`; reward rule evaluation for the three triggers; fraud flags; `referrals.rewards.approve|void`; Connect transfers via PAP-181; postings; statement PDFs via PAP-180 renderer. Deferred with the parent.""",
Spec="""* Cash rewards `pending` until 30 days past the refund window; credit and discount via Stripe coupons or customer balance.
* Fraud: self-referral, disposable emails, more than five signups per `ip_hash` per day, refunded first invoice voids; flags block payout until review.
* Postings debit `marketing_referral`, credit `affiliate_payable`, then payable to cash; idempotent by reward id; refunds create negative rewards netted against future payouts.""",
Contract="""Provides: `referrals.rewards.*`, `affiliate_account`, events `referral.reward.paid`, statements. Consumes: codes child, PAP-181 `createTransfer`, PAP-179, PAP-180 (soft), PAP-177 coupons.""",
DoD="""* Rule and fraud fixtures; test-mode transfer recorded; postings balance; refund netting test.""",
Test="""* Unit: rules, fraud, netting.
* Integration: approve to transfer to journal entry; refund reversal.""",
Demo="""Approve a pending reward and open the transfer in Stripe and the entry in the journal.""",
Edge="""* No Connect account: `approved` with CTA, voided at 180 days; transfer failure returns to `approved`.""",
Deps="""Codes child (hard), PAP-181, PAP-179 (hard), PAP-180 (soft).""",
Agent="""Builder: Beacon with Ledger (Payments Integrator). Reviewer: Sentinel (Security Auditor), Bookkeeper.""",
SizeNote="deferred.")

child("PAP-196", "growth/referral/portal-console-ui", "Portal referral page, console program and referral grids and the rewards approval queue", "Build", "S",
Goal="""Give customers a place to share and track, and staff a queue to approve, on top of the referral data model.""",
Scope="""In: `_portal/referrals` (code, link, share buttons, status list, rewards, Connect CTA); console programs page, referrals grid, approval queue. Deferred with the parent.""",
Spec="""* Portal page uses PAP-64 shell and tenant branding; console grids are PAP-165 views; approval queue shows fraud flags with reasons.""",
Contract="""Provides: routes above. Consumes: both siblings, PAP-64, PAP-165, PAP-181 onboarding link.""",
DoD="""* Playwright share flow and approval; screenshots at seven widths in light and dark; permission tests (customers see only their own).""",
Test="""* E2E: portal share and status; staff approve; customer denied on `/referrals/admin`.""",
Demo="""Copy the code from the portal, then approve a reward in the console queue.""",
Edge="""* Program paused shows a notice on the portal page.""",
Deps="""Both siblings (hard), PAP-64, PAP-165.""",
Agent="""Builder: Beacon. Reviewer: Sentinel (Visual Inspector).""",
SizeNote="half a session, deferred.")

# ---------------- PAP-197 support inbox ----------------
child("PAP-197", "growth/support/email-threading", "Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies", "Build", "M",
Goal="""Turn raw inbound email into clean, correctly threaded conversations linked to the right contact, and send replies that thread in the customer's client.""",
Scope="""In: `support/schema.ts`, `support.inbound` route (Resend inbound), `mailparser` 3.x, quoted-history stripping, `sanitize-html` 2.x allowlist, threading by `In-Reply-To`, `References`, subject plus sender, contact matching precedence, outbound via Resend with `Message-ID`, attachments via PAP-37. Out: chat, notes, console UI (siblings).""",
Spec="""* Tables per the parent; `provider_message_id` unique for dedupe.
* Status rules: inbound reopens `resolved` within seven days else new; outbound sets `pending`.
* Auto-reply detection via `Auto-Submitted` and `Precedence: bulk`; never auto-reply to auto-replies.""",
Contract="""Provides: schema, `support.conversations|messages|mailboxes.*`, inbound route, `threadInbound(email)`, `sanitiseHtml`. Consumes: PAP-187, PAP-37, PAP-38, provider per PAP-188, mailbox DNS (Needs Justin).""",
DoD="""* 30 fixture emails threaded and sanitised correctly; real email round trip on staging recorded.""",
Test="""* Unit: threading, stripping, sanitiser, matching precedence, status rules.
* Integration: real inbound and threaded reply.""",
Demo="""Send an email to the staging mailbox and read it in a raw conversation view; reply and show it threaded in the client.""",
Edge="""* Same email CC'd to two mailboxes yields cross-linked conversations; 25 MB attachment kept as reference with warning.""",
Deps="""PAP-187, PAP-37 (hard), PAP-38, mailbox DNS. Blocks siblings.""",
Agent="""Builder: Beacon (CRM Builder). Reviewer: Sentinel (Security Auditor for sanitisation, Edge Case Hunter).""",
SizeNote="threading heuristics.")

child("PAP-197", "growth/support/chat-notes", "Portal SupportChat widget with live sync and presence, unauthenticated email capture and internal notes on comment threads", "Build", "M",
Goal="""Add the in-app channel and internal collaboration: customers chat from the portal in real time and staff discuss privately on the same conversation.""",
Scope="""In: `<SupportChat/>` in the PAP-64 shell creating `channel: chat` conversations, live messages via PAP-143 with 3-second polling fallback, presence and typing via PAP-141, email capture for anonymous visitors upgraded on login, internal notes as PAP-131 threads with `visibility: internal`. Out: console UI (sibling).""",
Spec="""* Widget works unauthenticated with email capture; messages land within one second when realtime is available.
* Notes reuse comment mentions and Linear escalation unchanged; agents may note, not reply.""",
Contract="""Provides: `<SupportChat/>`, `support.chat.start|send`, note anchoring convention `anchor_type: entity`. Consumes: threading child, PAP-64, PAP-143, PAP-141, PAP-131.""",
DoD="""* Playwright chat round trip under one second; note with mention; screenshots of the widget at 320, 375, 1024.""",
Test="""* Unit: email capture upgrade, permission matrix for agents.
* E2E: portal message appears in a raw console list and the reply returns; fallback polling works with realtime disabled.""",
Demo="""Open the portal as a customer, send a chat, reply from the console, add an internal note.""",
Edge="""* Company with three contacts links the individual; offline customer sees queued state.""",
Deps="""Threading child (hard), PAP-131 (hard), PAP-64, PAP-143 and PAP-141 (soft).""",
Agent="""Builder: Beacon with Nova on live chat. Reviewer: Sentinel (Security Auditor).""",
SizeNote="one session.")

child("PAP-197", "growth/support/console-ui", "Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics", "Build", "M",
Goal="""Give staff a fast, keyboard-first inbox that shows the whole customer beside every conversation.""",
Scope="""In: `_app/support/` three-pane layout (PAP-169 list view with filters status, assignee, tag; conversation; contact sidebar with CRM fields, deals, past conversations), assign, snooze, canned replies, shortcuts `e`, `a`, `r` via PAP-151, first-response and resolution rollups for a dashboard block, `<ConversationList/>` embedded on PAP-189 pages.""",
Spec="""* Single-pane under `lg`; inbox fully keyboard-operable; snooze unsnoozes on inbound.
* Metrics rolled up daily for a PAP-173 number block.""",
Contract="""Provides: console routes, `<ConversationList contactId? companyId? />`, commands `support.*`, dataset `support.metrics`. Consumes: both siblings, PAP-169, PAP-151, PAP-70, PAP-173.""",
DoD="""* Playwright inbox flows; screenshots at seven widths in light and dark; axe clean; `docs/growth/support.md`.""",
Test="""* Unit: metrics rollup.
* E2E: assign, snooze, macro reply, keyboard-only pass.""",
Demo="""Work three conversations with the keyboard only, then open the metrics block.""",
Edge="""* 10k conversations paginate through the list view; deleted contact shows an unlinked sidebar.""",
Deps="""Both siblings (hard), PAP-169, PAP-151, PAP-70, PAP-173 (soft).""",
Agent="""Builder: Beacon. Reviewer: Sentinel (Visual Inspector), Quill.""",
SizeNote="one session.")

# ---------------- gap issue ----------------
gap("gap/growth/consent-centre",
"Build the consent and marketing compliance centre: preference page, unsubscribe centre, double opt-in, suppression list shared by outreach, notifications and forms, GDPR/CAN-SPAM/TCPA rules",
"P2", "Build", 2, ["Customer", "Staff"], "Campaigns and social", ["PAP-187", "PAP-43"], ["PAP-191", "PAP-193"],
Goal="""Replace three partial consent implementations (PAP-187 stores it, PAP-191 checks it, PAP-193 writes it) with one: a consent record per contact and channel, a shared suppression list, a public preference and unsubscribe centre, double opt-in, and the rule set that decides whether a message may go out under GDPR, CAN-SPAM and TCPA.""",
Scope="""In: tables `consent_record`, `suppression_entry`, `consent_purpose`; `canContact(contactId, channel, purpose)`; public routes `/c/:token` (preferences), `/u/:token` (one-click unsubscribe, RFC 8058 POST), double opt-in confirm route; procedures `consent.*`, `suppression.*`; staff pages under `_app/marketing/compliance`; audit export. Out: cookie banners for the marketing site (PAP-221 owns privacy pages), consent for agent data access (PAP-60).""",
Spec="""* `consent_record (contact_id, channel: email|sms|push, purpose: marketing|transactional|product_updates, status: granted|denied|pending_double_opt_in|withdrawn, source, evidence jsonb { ip_hash, user_agent_class, form_id, text_shown, timestamp }, version, granted_at, withdrawn_at)`; append-only, current row per `(contact, channel, purpose)` via a view.
* `suppression_entry (tenant_id, kind: email|phone|domain, value_hash, reason: unsubscribe|complaint|hard_bounce|manual|legal, source, created_at)`; global per tenant across sequences, notifications and forms; `suppression.check(values[])` batched.
* `canContact` returns `{ ok, reason }` combining consent, suppression, `do_not_contact`, quiet hours for SMS (TCPA) and the purpose rules: transactional allowed without marketing consent, marketing requires `granted`, SMS marketing requires explicit opt-in with evidence.
* Preference centre: per channel and purpose toggles, "unsubscribe from all", tenant branding, no login required with a signed token per contact; changes write consent records and suppression entries.
* Double opt-in: forms (PAP-169, PAP-193) create `pending_double_opt_in` and send a confirm email through PAP-136 core; unconfirmed after 30 days expires.
* `List-Unsubscribe` and `List-Unsubscribe-Post` headers supplied to PAP-191 and PAP-136; STOP keywords from PAP-191 write suppression here.
* Exports: per-contact consent history for DSAR (PAP-221) and a tenant compliance report dataset.""",
Contract="""Provides: `canContact`, `consent.record|withdraw|history`, `suppression.add|check|list`, `preferenceLink(contactId)`, `unsubscribeHeaders(contactId, channel)`, routes above, events `consent.changed`, `suppression.added`, dataset `growth.compliance`. Consumes: contacts (PAP-187), notifications (PAP-136 core), forms (PAP-169, PAP-193 write through `consent.record`), rate limiting (PAP-267), theming (PAP-74), jobs (PAP-43). Consumed by PAP-191 (hard), PAP-193, PAP-136, {{gap/business-core/recurring-dunning}}, PAP-221 exports.""",
DoD="""* Vitest, integration and Playwright below green.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the preference centre (two brands) and the staff compliance page; axe clean.
* `docs/growth/consent.md` with the rule table per jurisdiction; CHANGELOG; Linear comment with a live preference link on the demo tenant.""",
Test="""* Unit: `canContact` decision table (channel by purpose by status by suppression), token signing and expiry, double opt-in expiry, header generation.
* Integration: unsubscribe POST suppresses across a running PAP-191 sequence and a PAP-136 digest in the same test; form submission with consent creates `pending_double_opt_in` then `granted` on confirm; STOP writes suppression; history export matches records.
* E2E: open the preference link, toggle SMS marketing off, confirm the sequence skips the SMS step; one-click unsubscribe from an email header.
* Visual: matrix above.""",
Demo="""Reviewer opens a contact's preference link from the CRM page, turns off marketing email, then enrols the contact in a sequence and watches `canContact` refuse with the reason; finally clicks the one-click unsubscribe from a test email and sees the suppression entry. Under two minutes.""",
Edge="""* Contact merged: consent records re-pointed, most restrictive status wins.
* Withdrawal then re-grant: new record with fresh evidence; history intact.
* Suppressed domain (whole company opted out): every contact at that domain refused.
* Token leaked: preference page shows no PII beyond masked email; rotate via `preferenceLink`.
* Legal hold: `reason: legal` suppression cannot be removed by staff.""",
Deps="""PAP-187 (hard), PAP-43 (hard), PAP-136 core, PAP-169, PAP-193, PAP-74, PAP-267. Blocks PAP-191 (suppression), PAP-193 (consent writes).""",
Agent="""Builder: Beacon (CRM Builder) with Quill on the rule table. Reviewer: Sentinel (Security Auditor for public routes and PII, Edge Case Hunter).""",
Size="""M: a decision function, two public pages and append-only tables.""")


# FIX-5 (2026-09-17): folded into live issues as work packages; never create. See round2/folded-into-live-issues.json.
import json as _json, os as _os
_FOLDED = {f["key"] for f in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "folded-into-live-issues.json")))["folded"]}
GAPS = [g for g in GAPS if g["key"] not in _FOLDED]
