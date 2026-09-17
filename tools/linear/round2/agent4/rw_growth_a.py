# Rewritten specs for growth PAP-187..PAP-192.
SPECS = {}
def add(k, **s): SPECS[k] = s

add("PAP-187",
Goal="""Define the customer graph every PaperOS app shares: leads, contacts, companies, deals, pipeline stages, activities and segments as Drizzle tables on core conventions, with procedures, three page specs and the written contract that PAP-189, PAP-191, PAP-195 and PAP-197 build on. Spec issue: schema and contract, not UI.""",
Scope="""In: `packages/growth/src/crm/schema.ts` with `crm_company`, `crm_contact`, `crm_contact_company`, `crm_lead`, `crm_pipeline`, `crm_pipeline_stage`, `crm_deal`, `crm_activity`, `crm_segment`, `crm_segment_member`, `crm_tag`, `crm_entity_tag`, `crm_external_ref`; `drizzle-zod` types; routers `crm.companies|contacts|leads|deals|activities|segments.*` plus `crm.leads.convert` and `crm.deals.move`; search and dataset registration; page specs `specs/crm/pipeline|contacts|company-detail.spec.yaml`; `docs/growth/crm-model.md` with ER diagram and Twenty/HubSpot mapping.

Out: UI (PAP-189), sequences, segment evaluation (PAP-195), importers, the consent centre ({{gap/growth/consent-centre}} owns preference and suppression semantics; this issue only stores `consent jsonb`).""",
Spec="""* Every table: `tenant_id` RLS, `workspace_id`, uuid v7 `id`, timestamps, `archived_at`, `created_by` (human or agent principal), `owner_user_id`, `custom jsonb` for PAP-164 fields.
* `crm_contact`: names, `email citext` unique per tenant where not null, `phone` E.164, `company_id`, `title`, `lifecycle: subscriber|lead|mql|sql|customer|churned`, `source`, `consent jsonb`, `unsubscribed_at`, `do_not_contact`, `email_status`.
* `crm_company`: `name`, `domain citext` unique per tenant, `industry`, `size_band`, `billing_customer_id` (PAP-175 party), `address jsonb`.
* `crm_lead`: `contact_id?`, `payload jsonb`, `status: new|working|converted|disqualified`, `converted_contact_id`, `converted_deal_id`, `utm jsonb`.
* `crm_pipeline` and `crm_pipeline_stage (name, position, probability, kind: open|won|lost)`; default pipeline seeded.
* `crm_deal`: `title`, `company_id`, `primary_contact_id`, `pipeline_id`, `stage_id`, `amount_minor bigint`, `currency`, `expected_close_date`, `won_at`, `lost_at`, `lost_reason`, `sort_key`.
* `crm_activity`: `kind: note|call|email|sms|meeting|task|system`, `about_type|about_id`, `body_json`, `occurred_at`, `due_at`, `completed_at`, `external_ref`.
* `crm_segment`: `name`, `definition jsonb` (`FilterTree`), `mode: dynamic|static`, `last_evaluated_at`, `member_count`.
* Triggers: stage change writes a `system` activity and sets `won_at|lost_at`; conversion is one transaction.
* Permissions `crm.*.read|write|export`; customer audiences never see CRM tables.""",
Contract="""Provides: the twelve tables, Zod types `Contact`, `Company`, `Deal`, `Lead`, `Activity`, `Segment`, the routers above with cursor pagination, datasets `crm.contacts|companies|deals|activities`, search registrations, events `crm.deal.stage_changed`, `crm.lead.converted`, `crm.contact.created` on the outbox, three page specs. Consumes: core entities (PAP-33), RLS (PAP-34), API conventions (PAP-268), search (PAP-39), spec schema (PAP-117), `registerDataset` (PAP-161), `FilterTree` (PAP-279), `fin_party` link (PAP-175). Consumed by PAP-189 to PAP-197, PAP-202, PAP-206.""",
DoD="""* Migration applies and rolls back on Postgres 17; `pnpm db:check` clean; cross-tenant harness green.
* Three page specs validate with PAP-117.
* ER diagram renders; contract doc reviewed by Quill and Ledger.
* Drizzle Studio screenshot of seed data at 1280 and 1920.
* CHANGELOG; ADR `docs/adr/00xx-crm-model.md`; Linear comment linking doc and migration.""",
Test="""* Unit: unique email and domain constraints, conversion transaction rolls back on failure, stage trigger sets `won_at`, cursor pagination on each router, `crm.deals.move` bulk.
* Integration: RLS harness on all tables; search returns a contact by partial email; datasets appear through `getDataset`; outbox events emitted for stage change and conversion.
* E2E and visual: none beyond the Studio screenshots (no UI).""",
Demo="""Reviewer runs `pnpm db:seed --profile demo`, opens Drizzle Studio to browse contacts and deals, then runs `pnpm tsx scripts/crm-demo.ts` which converts a lead, moves the deal to Won and prints the resulting system activity and outbox event. Under two minutes.""",
Edge="""* Phone-only contact allowed; phone uniqueness is a merge suggestion, not a constraint.
* Same person at two companies: `crm_contact_company` history with from and to dates.
* Deleting a stage with deals blocked until moved.
* Foreign-currency amount stored as given; reporting converts via PAP-175 rates.
* Consent revoked mid-sequence: checked at send time by PAP-191.""",
Deps="""PAP-33 (hard), PAP-34, PAP-268, PAP-39, PAP-117 (draft acceptable), PAP-161 (stub if not merged), PAP-279, PAP-175 (party link). Blocks PAP-189, PAP-190, PAP-191, PAP-193, PAP-194, PAP-195, PAP-197, {{gap/growth/consent-centre}}.""",
Agent="""Builder: Beacon (CRM Builder) with Forge (Schema Wright) on migrations and RLS. Reviewer: Sentinel (Security Auditor), Atlas for fit with finance and PM models.""",
Size="""M: twelve tables whose shape drives five downstream issues and two importers.""")

add("PAP-188",
Goal="""Decide, before growth code is written, which parts of the marketing stack PaperOS borrows and which it builds: evaluate Twenty, Postiz, Listmonk, Dub, Chatwoot and Umami/PostHog against the library rubric and record the outcome as an ADR every growth issue then follows.""",
Scope="""In: rubric from PAP-210 extended with multi-tenancy, embeddability, data ownership, deliverability and AGPL review under PAP-211; three integration shapes scored per product (run as a service, fork and embed, reimplement on the tables engine); `spikes/growth-stack/` with Coolify compose files, screenshots and API smoke scripts; data-model mapping to PAP-187 fields for PAP-202 importers; ADR `docs/adr/00xx-growth-stack.md`; registry entries for PAP-215.

Out: production deployment of any candidate, adapters, paid SaaS beyond a note.""",
Spec="""* Time-box 1.5 agent-days, maximum 3 hours per product; unknowns become penalties.
* Hypothesis to confirm or reject: build CRM and segments on the tables engine; borrow Postiz adapters as reference or run it behind our approval queue; Listmonk only if Resend broadcasts prove insufficient; Dub via API for short links; reject running Twenty because it duplicates the tables engine.
* Score 1 to 5 on license fit, self-host effort, API completeness, tenant isolation, TypeScript quality, velocity (commits in 90 days), cost of exit; per product "what we take", "what we never take", hours per shape.
* Deliverability section: Resend versus Postmark versus SES for transactional and marketing volume, warmup, inbound parsing (feeds PAP-191 and PAP-197).
* Analytics section: Umami versus PostHog self-hosted versus own event table for PAP-194 under the privacy-first rule.
* Record OAuth app-review lead times per social platform so PAP-190 files applications immediately.""",
Contract="""Provides: `results.json` (per-product scores and shape estimates), the ADR decisions consumed as constraints by PAP-190, PAP-191, PAP-194, PAP-197, provider recommendation consumed by PAP-191 and PAP-197, compose files reusable for staging spikes, mapping tables consumed by PAP-202 and PAP-206. Consumes: rubric (PAP-210), license policy (PAP-211), staging host (PAP-25). No code exports.""",
DoD="""* Spikes committed (excluded from `turbo build`), compose files run on staging.
* ADR approved by Atlas and Beacon in PR review; decisions cross-referenced by comment on PAP-190, PAP-191, PAP-194, PAP-197.
* Screenshots of each candidate at 1280 and 1920; comparison table rendered from `results.json`.
* AGPL review for every candidate approved by Sentinel (Security Auditor).
* Registry entries or a Linear comment for Scout; CHANGELOG (docs); Linear comment with the ADR link and table.""",
Test="""* Unit: `results.json` validated against a Zod schema; rubric totals recomputed by script and compared with the table.
* Integration: each compose file starts on staging and its smoke script (create contact, schedule post, send test email, create short link) exits 0; results recorded in `results.json`.
* Docs: link check on all evidence URLs.
* E2E and visual: none beyond the candidate screenshots.""",
Demo="""Reviewer opens the ADR, reads the six one-paragraph decisions, then opens the comparison table and the Postiz screenshot to confirm the "borrow adapters, own the queue" call. Under two minutes.""",
Edge="""* Product needs its own Postgres or Redis: score operational cost; never share our primary database.
* Platform OAuth review measured in weeks: record lead time and start applications.
* License changed recently (Dub): record the exact version evaluated.
* Incomplete self-host docs: score only what the spike achieved.
* Justin prefers a paid tool: open question in the ADR, not a blocker.""",
Deps="""None hard; starts now (moved to Ready for Claude per the round-2 audit). Uses PAP-210 and PAP-211 drafts. Blocks PAP-190; informs PAP-191, PAP-194, PAP-197, PAP-202.""",
Agent="""Builder: Scout (Library Evaluator) paired with Beacon. Reviewer: Atlas (decision), Sentinel (Security Auditor) for licenses.""",
Size="""M: six time-boxed spikes with real installs.""")

add("PAP-189",
Goal="""Give every tenant a working sales workflow on day one: a deal pipeline kanban, a contacts grid and company, contact and deal detail pages, all rendered by the views engine from saved view definitions so CRM screens inherit filtering, grouping, sharing and permissions and prove the engine on a real domain.""",
Scope="""In: routes `apps/web/src/routes/_app/crm/` (`pipeline`, `contacts`, `companies`, `companies/$id`, `contacts/$id`, `deals/$id`) from the PAP-187 specs plus `deal-detail` and `contact-detail` specs; view JSON `packages/growth/src/crm/views/*.view.json` (`deals-pipeline`, `contacts-all`, `companies-all`); per-audience defaults via PAP-172; detail pages from PAP-70 layouts; won and lost dialogs; commands "New deal", "New contact", "Go to pipeline"; demo seed of 40 companies, 200 contacts, 60 deals.

Out: sequences, segment UI, imports, email compose, dashboards beyond pipeline value.""",
Spec="""* Kanban card: title, company avatar, amount in tenant currency, days-in-stage badge (amber over 14, red over 30), owner avatar; stage headers show count and sum from `aggregations`.
* Moving to a `won` or `lost` stage opens a dialog (won: amount and close date; lost: reason) through the PAP-167 `onMove` hook before commit.
* Contacts grid inline-edits `lifecycle`, `owner`, `tags`; bulk actions add to segment, assign owner, export CSV (`crm.contacts.export`).
* Company detail: header, activity `Timeline` (PAP-71), related lists (contacts, deals, activities, support placeholder for PAP-197) as embedded views with URL filter state.
* Detail routes reuse the shared record detail shell when {{gap/tables/record-detail}} lands; until then a local `Inspector` layout.
* Empty states link to PAP-200 import; under `md` the kanban becomes a stage picker plus list and the inspector a drawer.""",
Contract="""Provides: the six routes, three view JSON files as the reference for "views from JSON", `WonLostDialog`, `useDealMove()`, commands `crm.*`, demo seed profile `crm`. Consumes: schema and routers (PAP-187), kanban `onMove` (PAP-167), grid (PAP-165), defaults and sharing (PAP-172, soft), layouts (PAP-70), `Timeline`, `AvatarStack` (PAP-71), keyboard drag (PAP-155), conflict banners (PAP-144, soft), commands (PAP-151). Consumed by PAP-195 (entry points), PAP-197 (related list), PAP-193 (lead landing).""",
DoD="""* Five page specs validate; PAP-123 conformance tests pass.
* Vitest, Playwright and axe below green; kanban has the PAP-155 keyboard alternative.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for pipeline, contacts and company detail.
* `docs/growth/crm-views.md` (adding a CRM field that appears in views); CHANGELOG; Linear comment with Pages demo and screenshots.""",
Test="""* Unit: view JSON validates against `viewSpecSchema`; won and lost dialog reducer; permission-gated bulk actions.
* Integration: `crm.deals.move` through the kanban writes stage and `sort_key`; per-audience default resolves "My deals" for a sales rep.
* E2E: create company, contact and deal; drag a deal across two stages; won dialog; inline lifecycle edit; customer-audience principal redirected from `/crm/*` with a 403 toast.
* Visual: seven widths, light and dark, three pages.""",
Demo="""Reviewer opens `/crm/pipeline` on the seeded tenant, drags a deal to Won and fills the dialog, opens the company page from the card, logs a note in the timeline and sees the contacts grid update lifecycle inline. Under two minutes.""",
Edge="""* 2,000 deals in one stage: virtualised column, server aggregates.
* Deal without a company shows the contact; rollups skip it.
* Concurrent stage moves: last write wins with banner and undo.
* Pipeline with no stages shows a setup prompt.
* Custom field added later appears in the picker, not automatically on cards.""",
Deps="""PAP-187 (hard), PAP-167 (hard), PAP-165 (hard), PAP-172 (soft), PAP-70, PAP-71, PAP-155, PAP-144 (soft), PAP-123. Feeds PAP-195, PAP-197.""",
Agent="""Builder: Beacon (CRM Builder) with Nova consulted on view JSON. Reviewer: Sentinel (Visual Inspector, Code Reviewer), Iris for component usage.""",
Size="""M: mostly configuration of the views engine plus two detail pages and dialogs.""")

add("PAP-190",
Goal="""Let a tenant plan, approve and publish posts to X, LinkedIn, Instagram, TikTok and YouTube from one calendar, with every post passing an approval queue before any adapter publishes. Nothing leaves without an approved state; live publishing only for accounts Justin connects. Umbrella for three children.""",
Scope="""Children (same milestone, Backlog):

* {{growth/social/model-queue-calendar}} (M) Schema, approval state machine, composer with per-platform variants, queue and calendar (list fallback).
* {{growth/social/adapter-mock-x}} (M) Adapter interface, mock adapter, X API v2 adapter, pg-boss publishing worker with retries and duplicate protection.
* {{growth/social/adapters-review-gated}} (M) LinkedIn, Instagram, TikTok and YouTube adapters in `dryRun` with payload snapshots, OAuth connect flows, re-auth banners, app-review checklist.

Out: paid ads, DMs, comment moderation, analytics beyond per-post metrics, Facebook Pages.""",
Spec="""Decisions binding all children:

* `social_account (platform, external_id, handle, oauth jsonb encrypted via {{gap/data-layer/field-encryption}} or PAP-17 helpers, scopes, status, expires_at)`; `social_post (body, media_file_ids, link_url, status: draft|pending_approval|approved|scheduled|publishing|published|failed|rejected, scheduled_at, published_at, approved_by, approved_hash, rejected_reason, source: human|agent, campaign_id)`; `social_post_target (post x account, variant_body, external_post_id, metrics jsonb, error)`; `social_campaign`.
* Adapter interface `validate(post) -> Issue[]`, `publish(target) -> { externalId, url }`, `fetchMetrics(target)`, `refreshAuth(account)`, all behind `dryRun`.
* State transitions are the only writes to `status`; approval binds to a content hash; edits return to `pending_approval`.
* `social.approve` for owner and admin only; agents create `pending_approval` only.
* Limits per adapter (X 280, LinkedIn 3000, Instagram media required, TikTok video only, YouTube title under 100) enforced in `validate` and live in the composer.
* `scheduled_at` stored UTC, displayed in the tenant timezone.""",
Contract="""Provides: `social.posts.create|update|submit|approve|reject|schedule|list`, `social.accounts.connect|list|disconnect`, `SocialAdapter` interface and `adapters[platform]`, `validatePost(post, platforms)` reused by PAP-192 for length limits, events `social.post.published|failed`, calendar view binding for PAP-168. Consumes: schema (PAP-187), decision (PAP-188), files (PAP-37), jobs (pg-boss via PAP-43 conventions), secrets (PAP-17), calendar (PAP-168, list fallback), audit (PAP-38). Consumed by PAP-192, PAP-195 campaign audiences.""",
DoD="""* All three children Done.
* X and LinkedIn exercised once against test accounts with `dryRun: false`, recording attached; the other three verified in `dryRun` with payload snapshots.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for calendar, composer and queue; axe clean; composer keyboard-only.
* `docs/growth/social.md` (connecting accounts, adding an adapter, app-review checklist); CHANGELOG; Linear comment with recording.""",
Test="""Umbrella `social.e2e.spec.ts`: draft a post with two platform variants, submit, approve as admin, schedule for one minute ahead, run the worker with the mock adapter, assert `published` with an external id and a calendar entry; edit an approved post and assert it returns to `pending_approval`; revoke the mock token and assert `reauth_required` with the post back in `approved`; kill the worker mid-publish and assert the `externalId` lookup prevents a duplicate; hit a mocked 429 and assert `Retry-After` is honoured.""",
Demo="""Reviewer writes a post in the composer, watches the X counter turn red past 280, trims it, submits, approves it from the queue as admin, schedules it and sees it appear on the calendar and publish through the mock adapter. Under two minutes.""",
Edge="""* Token revoked: one failure, account flagged, post stays `approved`.
* Scheduled time already past on approval: publish after a confirmation.
* Media over platform limits blocks scheduling.
* Worker crash: `publishing` rows older than 10 minutes re-checked before retry.
* Rate limit: other posts to the same account delayed.""",
Deps="""PAP-187 (hard), PAP-188 (hard), PAP-37 (hard), PAP-43, PAP-17, PAP-168 (soft), platform OAuth apps (Needs Justin, one item covering all five). Blocks PAP-192.""",
Agent="""Builder: Beacon (Campaign Composer for UI, Outreach Sequencer for adapters). Reviewer: Sentinel (Security Auditor for token handling, Code Reviewer, Visual Inspector), Atlas on the approval rule.""",
Size="""L, split into three M children; the third waits on app reviews and ships in `dryRun`.""")

add("PAP-191",
Goal="""Automate compliant outbound: multi-step email and SMS sequences over Resend and Twilio that enrol CRM contacts, pause on reply, honour consent and quiet hours, warm up sending domains and record every touch as an activity. Sending is sandboxed to an allowlist until Justin flips the tenant flag. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{growth/outreach/model-worker}} Schema, provider interface with Resend and Twilio adapters, the per-minute scheduler worker, template rendering and idempotency.
* {{growth/outreach/compliance-warmup-replies}} Consent and suppression checks, quiet hours, List-Unsubscribe and STOP handling, warmup stages, bounce and complaint handling, reply detection webhooks.
* {{growth/outreach/ui}} Sequence builder, template editor with preview and test send, enrolments grid, domain setup wizard.

Out: purchased data, AI drafting (PAP-192), deliverability dashboards beyond counters, WhatsApp.""",
Spec="""Decisions binding all children:

* `outreach_sequence (name, status, channel_mix, settings jsonb)`, `outreach_step (position, channel, delay_minutes, template_id, condition jsonb)`, `outreach_template (subject, body_mjml|body_text, variables, approved_by, version)`, `outreach_enrolment (contact_id, sequence_id, status: active|paused|replied|bounced|unsubscribed|completed|failed, current_step, next_send_at, template_version)`, `outreach_message (enrolment_id, step_id, channel, provider_message_id, status, events jsonb)` unique on `(enrolment_id, step_id)`, `sending_domain (domain, dns_status, warmup_stage, daily_limit, reputation_score)`.
* Provider interface `send`, `verifyWebhook`, `parseEvent`, `parseInbound`; Resend SDK 4.x and Twilio 5.x first; Postmark or SES per PAP-188.
* Worker uses `SELECT ... FOR UPDATE SKIP LOCKED`; consent, `do_not_contact` and the suppression list from {{gap/growth/consent-centre}} are checked at send time.
* Sandbox: `outreach.sandbox = true` rewrites non-allowlisted recipients to `sandbox+<hash>@paperos.test`; flipping it is Needs Justin.
* Warmup caps 20, 50, 100, 250, 500, 1000 per day, advancing after three clean days, regressing on bounce over 2 percent or complaints over 0.1 percent.
* Quiet hours 8am to 9pm recipient local time; contact timezone, then company, then tenant.""",
Contract="""Provides: `outreach.sequences|steps|templates|enrolments.*`, `outreach.enrol({ sequenceId, contactIds | segmentId })`, `OutreachProvider` interface, inbound route `outreach.inbound`, events `outreach.replied`, `outreach.bounced`, `outreach.unsubscribed`, `outreach_message` rows as `crm_activity kind email|sms`. Consumes: contacts, consent, activities (PAP-187), suppression and preference API ({{gap/growth/consent-centre}}), secrets (PAP-17), audit (PAP-38), grid (PAP-165), segments (PAP-195, enrol by segment), provider decision (PAP-188). Consumed by PAP-192 templates, PAP-197 (replies open conversations).""",
DoD="""* All three children Done.
* Integration against Resend and Twilio test credentials in sandbox: one email and one SMS to allowlisted addresses, STOP round trip, recordings attached.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for builder, enrolments and domain wizard; security sign-off on webhooks and template rendering.
* `docs/growth/outreach.md` with the compliance checklist; CHANGELOG; Linear comment with recording.""",
Test="""Umbrella `outreach.e2e.spec.ts` with a test clock: build a two-step sequence (email then SMS after one day), enrol three contacts (one with revoked consent, one in a quiet-hours timezone), advance the clock and assert exactly the compliant sends with correct local times; post a Resend inbound reply matching the plus-address token and assert `replied` and a paused enrolment; send a STOP SMS and assert suppression; simulate three clean days and a bounce spike and assert warmup advance then regression; replay a webhook and assert idempotency.""",
Demo="""Reviewer builds a two-step sequence, enrols a contact from the allowlist, presses the test-clock "advance one day" button, sees the email and SMS rows with provider ids, replies to the email from their inbox and watches the enrolment pause with the reply as an activity. Under two minutes.""",
Edge="""* Contact in two sequences: one outbound per day globally unless overridden.
* Unknown timezone: assumption logged on the message.
* Reply from a different address lands in an "Unmatched" list for manual linking.
* Provider outage: retries up to 6 hours, then `failed` without advancing.
* Template edited mid-sequence: enrolments keep their `template_version`.""",
Deps="""PAP-187 (hard), {{gap/growth/consent-centre}} (hard for suppression; stub with `do_not_contact` if absent), PAP-43 (hard), PAP-17, PAP-38, PAP-165, PAP-188 (decision), PAP-195 (soft). Feeds PAP-192, PAP-197.""",
Agent="""Builder: Beacon (Outreach Sequencer). Reviewer: Sentinel (Security Auditor, Edge Case Hunter for timezones and caps), Quill for compliance docs.""",
Size="""L, split into three M children.""")

add("PAP-192",
Goal="""Turn Beacon's Campaign Composer into a working content agent: a scheduled Claude session that reads merged changelogs, release digests and page specs, drafts social posts, announcement emails and landing copy in the tenant's voice, and files them as `pending_approval` items. It never publishes.""",
Scope="""In: character `packages/agents/characters/campaign-composer.yaml` (parent Beacon, `claude-fable-5-1`, effort high, `permissionMode: dontAsk`, tools Read, Grep, WebFetch and `paperos-growth` draft procedures only, Bash and publish procedures denied); prompt `prompts/campaign-composer.md`; skill `.claude/skills/draft-campaign/SKILL.md`; voice guide `docs/growth/voice.md` with `tenant.settings.brand.voice` overrides; Routine after each release candidate (PAP-88) and on the `Campaign` label; eval fixtures for PAP-110.

Out: publishing, image generation, paid ads, A/B testing.""",
Spec="""* Grounding: every claim traces to a changelog line, spec field or doc; the agent emits a `sources[]` array; unsupported claims fail self-review and are dropped.
* Output contract `{ channel, variant_body, media_slots[], link_url, sources[], confidence }` validated by Zod before filing.
* Limits from PAP-190 `validatePost`; drafts never exceed platform lengths.
* Filing: `social.posts.create({ status: 'pending_approval', source: 'agent' })`, `outreach.templates.create({ approved_by: null })`, `landing.drafts.create`, each stamped with the agent principal (PAP-60) and source references.
* At most 10 items per session; `perSessionUsd` 3 via PAP-111; dedupe on `(source_hash, channel)`.
* Queue UI shows "Drafted by Campaign Composer" with expandable sources; rejection reasons become PAP-109 memory notes.
* Never reads contact PII; the prompt forbids quoting contact data.""",
Contract="""Provides: character and skill definitions, `CampaignDraft` Zod schema, Routine definition `campaign-after-rc`, eval task `campaign-composer` with three golden fixtures and rubric, `drafted_by` badge component for approval queues. Consumes: roster and schema (PAP-104, PAP-103), skills format (PAP-105), evals (PAP-110), cost controls (PAP-111), memory (PAP-109), agent principals (PAP-60), changelog feed (PAP-133), draft procedures (PAP-190 hard; PAP-191 and PAP-193 soft, channel skipped if absent), orchestrator (PAP-96).""",
DoD="""* Character validates (`pnpm agents validate`) and appears in the org chart; smoke transcript attached.
* Skill run on staging against a real changelog range files at least three X posts, one LinkedIn post, one email template and one landing hero variant in `pending_approval`.
* Eval scores at or above 0.8 on the three fixtures, posted to Linear.
* Screenshots of the queue with agent drafts at 375, 1024, 1920.
* `docs/agents/campaign-composer.md` and voice guide; CHANGELOG; Linear comment with draft links and scores.""",
Test="""* Unit: output contract validation, length enforcement per channel, source-tracing check rejects a claim without a source, dedupe key.
* Integration: skill run with a fixture changelog through the PAP-110 runner produces drafts through the real procedures on a test tenant; tool scope test asserts a publish call is denied.
* E2E: approval queue shows the agent badge and sources; reject with reason writes a memory note.
* Visual: queue at the three widths in light and dark.""",
Demo="""Reviewer triggers the Routine manually with a recent changelog range, waits for the session summary comment, opens the social queue to read three drafts with their sources, and rejects one with a reason. Under two minutes after the session ends.""",
Edge="""* Internal-only changelog: agent files nothing and says so.
* No voice settings: default guide, flagged in the comment.
* Spec marked `draft: true` excluded unless named.
* Re-run on the same release updates existing drafts.
* Model refusal or partial output: comment posted, nothing filed.""",
Deps="""PAP-190 (hard), PAP-104 (hard), PAP-105, PAP-110, PAP-111, PAP-109, PAP-60, PAP-133, PAP-96, PAP-191 and PAP-193 (soft). Justin approves the character once via Needs Justin.""",
Agent="""Builder: Beacon (lead) with Quill on prompt and voice guide. Reviewer: Sentinel (Code Reviewer, Security Auditor for tool scope).""",
Size="""M: one character, one skill, filing procedures and evals.""")
