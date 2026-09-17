# growth — Growth: Marketing, Outreach & CRM
PHASE P2 prio 2 dependsOn ['tables', 'business-core']
SUMMARY: A CRM on the tables engine, social scheduling, outreach sequences, landing pages via Webflow, attribution and a support inbox, with a content agent drafting for approval.
DESC: Goal: every business gets customer acquisition machinery, not just an app. CRM entities (lead, contact, company, deal, activity, segment) live on the tables engine with pipeline and contact views. A social scheduler with platform adapters and an approval queue, outreach sequences over email and SMS with reply detection, Webflow-published landing pages capturing forms, and a privacy-first attribution pipeline cover acquisition. Segments from CRM plus product usage drive campaigns and in-app targeting; a referral program pays out through Stripe Connect; a support inbox links conversations to contacts. A content agent drafts posts and emails from changelogs and specs for human approval. Non-goal: sending anything without approval in this build.
MILESTONES: ['CRM core 2026-09-28: CRM model, OSS research, pipeline and contact views', 'Campaigns and social 2026-09-30: Social scheduler, outreach sequences, content agent, landing forms', 'Acquisition analytics 2026-10-01: Attribution, segments, referrals, support inbox']


## PAP-187 [P1 Spec M prio2 Backlog] Model CRM entities: lead, contact, company, deal, pipeline stage, activity, segment
key=growth/crm-model milestone=CRM core agent=Built by Beacon (CRM Builder) with Forge (Schema Wright) pai
blockedBy=['PAP-33'] blocks=['PAP-197', 'PAP-195', 'PAP-194', 'PAP-193', 'PAP-191', 'PAP-190', 'PAP-189']
GOAL: Define the customer graph every PaperOS app shares: leads, contacts, companies, deals, pipeline stages, activities and segments, as Drizzle tables on the core entity conventions, with the page specs and data contract that `growth/crm-views`, `growth/outreach-sequences`, `growth/segments` and `growth/support-inbox` build on. This is a Spec issue: schema, procedures, three page specs and the written contract, not UI.
SCOPE: In:

* Drizzle schema `packages/growth/src/crm/schema.ts`: `crm_company`, `crm_contact`, `crm_lead`, `crm_pipeline`, `crm_pipeline_stage`, `crm_deal`, `crm_activity`, `crm_segment`, `crm_segment_member`, `crm_tag`, `crm_entity_tag`, `crm_external_ref`.
* Every table carries `tenant_id` (RLS via `data-layer/rls-tenancy`), `workspace_id`, uuid v7 `id`, `created_at`, `updated_at`, `archived_at`, `created_by` (human or agent principal), `owner_user_id`, `custom jsonb` for fields added through `tables/field-types`.
* `drizzle-zod` types in `packages/growth/src/crm/types.ts`; oRPC routers `crm.companies|contacts|leads|deals|activities|segments.list/get/create/update/archive` plus `crm.leads.convert` and `crm.deals.move` (`data-layer/api-layer` conventions: cursor, `limit<=100`).
* Registration of every entity with `data-layer/search` (tsvector on name, email, domain, notes) and with the tables
SPEC(first 1200): * `crm_contact`: `first_name`, `last_name`, `email citext`, `phone` (E.164), `company_id`, `title`, `lifecycle: subscriber|lead|mql|sql|customer|churned`, `source`, `consent jsonb` (`{ email: { status, at, source }, sms: {...} }`), `unsubscribed_at`, `do_not_contact`; unique `(tenant_id, email)` where email not null.
* `crm_company`: `name`, `domain citext` unique per tenant, `industry`, `size_band`, `billing_customer_id` (link to `business-core/finance-data-model` customer), `address jsonb`.
* `crm_lead`: unqualified inbound; `contact_id` nullable, raw `payload jsonb`, `status: new|working|converted|disqualified`, `converted_contact_id`, `converted_deal_id`, `utm jsonb`.
* `crm_pipeline` + `crm_pipeline_stage(name, position, probability 0-100, kind: open|won|lost)`; default pipeline seeded with Lead, Qualified, Proposal, Negotiation, Won, Lost.
* `crm_deal`: `title`, `company_id`, `primary_contact_id`, `pipeline_id`, `stage_id`, `amount_cents bigint`, `currency`, `expected_close_date`, `won_at`, `lost_at`, `lost_reason`, `sort_order`.
* `crm_activity`: `kind: note|call|email|sms|meeting|task|system`, polymorphic `about_type|about_id`, `body_json` (Tiptap), `occurred_at`, `due_at`,
DOD:
* Migration applies and rolls back on fresh Postgres 17; `pnpm db:check` clean.
* Vitest: unique email constraint, conversion transaction, stage trigger, cross-tenant RLS harness test, cursor pagination on each router.
* Three page specs validate with `spec-builder/validator`.
* Search registration returns a contact by partial email in the search test.
* ER diagram renders; contract doc reviewed by Quill and Ledger (customer link).
* Drizzle Studio screenshot of seeded demo data at 1280 and 1920.
* CHANGELOG entry; ADR `docs/adr/00xx-crm-model.md`; Linear comment linking doc, migration and downstream issues notified.
EDGE:
* Contact with no email (phone-only lead): allowed; uniqueness on phone is advisory, surfaced as a merge suggestion.
* Same person at two companies: one contact, `crm_contact_company` history rows with `from|to` dates; `company_id` is the current one.
* Deleting a pipeline stage with deals: blocked; must move deals first (`crm.deals.move` bulk).
* Amount in a currency the tenant does not use: stored as given; reporting converts using `business-core/finance-data-model` rates.
* 500k contacts in a segment: membership cache paginated; `member_count` approximate until evaluation completes.
* Consent revoked while a sequence is running: `do_not_contact` checked at send time, not enrol time (`growth/outreach-sequences`).
DEPS: `data-layer/core-entities` (hard). Uses `data-layer/rls-tenancy`, `data-layer/api-layer`, `data-layer/search`, `spec-builder/schema` (draft acceptable), `tables/view-model-spec` (DataSource interface; stub if not merged). Unblocks every other growth issue and `migration/*` CRM mappings.


## PAP-188 [P1 Research M prio2 Backlog] Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR
key=growth/growth-research milestone=CRM core agent=Researched by Scout (Library Evaluator) paired with Beacon f
blockedBy=[] blocks=['PAP-190']
GOAL: Decide, before any growth code is written, which parts of the marketing stack PaperOS borrows and which it builds: evaluate Twenty (CRM), Postiz (social scheduling), Listmonk (email campaigns), Dub (links and attribution), plus Chatwoot (support inbox) and Umami/PostHog (analytics) against the library rubric, and record the outcome as an ADR that every growth issue then follows without re-litigating.
SCOPE: In:

* Rubric from `libraries/eval-rubric` extended with growth-specific criteria: multi-tenant model, embeddability (API, iframe, or fork), data ownership and export, deliverability tooling, license under `libraries/license-policy` (all six candidates are AGPL-3.0 or similar; document exactly what "review AGPL" means for a self-hosted, network-exposed service).
* Three integration shapes scored per product: (a) run as a Docker service on the VPS and integrate via API, (b) fork and embed components, (c) reimplement the relevant subset on the tables engine.
* Spike folder `spikes/growth-stack/` with Coolify compose files that stand each candidate up on staging for a day; screenshots of each product's core screen; API smoke scripts (create a contact, schedule a post, send a test email, create a short link).
* Written mapping of each candidate's data model to `growth/crm-model` fields, reus
SPEC(first 1200): * Time-box: 1.5 agent-days total, maximum 3 hours per product; unknowns become rubric penalties.
* Default hypothesis to confirm or reject: build CRM and segments on the tables engine (because views, permissions and RLS are already ours), borrow Postiz's platform adapters as reference or run it as a service behind an approval queue we own, use Listmonk only if Resend's broadcast API proves insufficient, use Dub for short links via API, and reject running Twenty because it duplicates the tables engine.
* Each product scored 1-5 on: license fit, self-host effort, API completeness, tenant isolation, TypeScript quality, community velocity (commits last 90 days), cost of exit.
* Deliverables per product: score table, "what we would take", "what we would never take", hours estimate for each integration shape.
* Deliverability section: compare Resend, Postmark and SES for transactional plus marketing volume, warmup features and inbound parsing, feeding `growth/outreach-sequences` and `growth/support-inbox`.
* Analytics section: Umami vs PostHog self-hosted vs a hand-rolled event table for `growth/attribution`; must respect the privacy-first requirement (no third-party cookies, EU hosting 
DOD:
* Spikes committed under `spikes/growth-stack/` (excluded from `turbo build`), compose files runnable on staging.
* ADR approved by Atlas and Beacon via PR comment; decisions cross-referenced in the descriptions of `growth/social-scheduler`, `growth/outreach-sequences`, `growth/attribution`, `growth/support-inbox` (comment on each).
* Screenshots of each candidate's core screen at 1280 and 1920 attached, plus a one-page comparison table rendered from `results.json`.
* License review for every AGPL candidate written up and approved by Sentinel (Security Auditor).
* `libraries/registry` entries or a Linear comment for Scout to add them.
* CHANGELOG entry; Linear comment with the ADR link and table.
EDGE:
* Product requires its own Postgres or Redis: score the operational cost, do not share our primary database.
* API needs an OAuth app review that takes weeks (LinkedIn, TikTok): note lead time so `growth/social-scheduler` starts applications immediately.
* Candidate license changed recently (Dub moved parts to a commercial license): record the exact version evaluated.
* Self-hosted docs incomplete: score self-host only on what was actually achieved in the spike.
* Two candidates overlap (Postiz and Listmonk both send email): pick one owner per capability.
* Justin prefers a paid tool: capture as an open question in the ADR, not a blocker.
DEPS: None (can start now). Informs `growth/social-scheduler` (hard, listed dependency), `growth/outreach-sequences`, `growth/attribution`, `growth/support-inbox`, `migration/format-research`. Uses `libraries/eval-rubric` and `libraries/license-policy` if merged; otherwise apply their draft rubric.


## PAP-189 [P2 Build M prio2 Backlog] Build CRM pipeline (kanban), contact list and company views on the tables engine
key=growth/crm-views milestone=CRM core agent=Built by Beacon (CRM Builder) with Nova (Views Engineer) con
blockedBy=['PAP-167', 'PAP-187'] blocks=[]
GOAL: Give every tenant a working sales workflow on day one: a deal pipeline kanban, a contacts grid and a company detail page, all rendered by the tables/views engine from saved view definitions rather than bespoke components, so CRM screens inherit filtering, grouping, sharing and permissions for free and prove the engine on a real domain.
SCOPE: In:

* Routes in `apps/web/src/routes/_app/crm/`: `pipeline`, `contacts`, `companies`, `companies/$id`, `contacts/$id`, `deals/$id`, built from the three page specs in `growth/crm-model` (extend with `deal-detail` and `contact-detail` specs here).
* Saved view definitions in `packages/growth/src/crm/views/*.view.json` following `tables/view-model-spec`: `deals-pipeline` (kanban grouped by `stage_id`, swimlane option by `owner_user_id`, card fields title, company, amount, expected close, WIP limit per stage optional), `contacts-all` (grid: name, email, company, lifecycle, owner, last activity; default sort last activity desc), `companies-all` (grid with rollup columns open deals count and pipeline value), plus per-audience defaults via `tables/view-sharing` (sales rep sees "My deals" by default).
* Detail pages composed from `design-system/layout-components` (`Inspector`, `SplitPane`): he
SPEC(first 1200): * Kanban card: `title`, company avatar (`AvatarStack`), amount formatted by tenant currency, days in stage badge (amber over 14, red over 30), owner avatar.
* Stage columns show count and sum aggregates from the view's `aggregations`.
* Moving to a `won` or `lost` stage opens a small dialog (won: confirm amount and close date; lost: reason select) before committing.
* Contacts grid inline-edits `lifecycle`, `owner`, `tags`; bulk actions: add to segment, assign owner, export CSV (`crm.contacts.export` permission).
* Company detail related lists: contacts, deals, activities, support conversations (placeholder until `growth/support-inbox`), each an embedded view with its own filter state in the URL.
* Empty states use `EmptyState` with a primary action ("Import contacts" linking to `migration/csv-excel`).
* All pages responsive: under `md` the kanban becomes a stage picker plus single-column list; inspector becomes a drawer.
DOD:
* Five page specs validate; conformance tests from `spec-builder/conformance-tests` pass.
* Vitest: view JSON validates against the view model schema; move-stage dialog logic; permission-gated bulk actions.
* Playwright: create company, contact and deal; drag deal across two stages; won dialog; inline edit lifecycle; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for pipeline, contacts and company detail.
* axe clean; kanban drag has the keyboard alternative from `input/drag-drop`.
* `docs/growth/crm-views.md` (how to add a CRM field and have it appear in views); CHANGELOG entry; Linear comment with Pages demo link and screenshots.
EDGE:
* 2,000 deals in one stage: column virtualised; aggregates come from the server, not rendered cards.
* Deal with no company: card shows contact instead; grid rollups skip it.
* Concurrent stage move by two staff: last write wins with a banner and undo (`realtime/conflict-ux`).
* Pipeline with a single stage or zero stages: pipeline page shows setup prompt, not a blank board.
* Custom field added via `tables/field-types` after views exist: appears in the field picker, not automatically in cards.
* Customer-audience principal hitting `/crm/*`: redirected to portal with a 403 toast; permission tests cover it.
DEPS: `growth/crm-model` and `tables/kanban-view` (hard). `tables/grid-view`, `tables/view-sharing`, `design-system/layout-components`, `design-system/data-display`, `input/drag-drop` (keyboard alternative), `realtime/conflict-ux` (soft). Unblocks `growth/segments` UI entry points and `growth/support-inbox` related list.


## PAP-190 [P2 Build L prio2 Backlog] Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and an approval queue
key=growth/social-scheduler milestone=Campaigns and social agent=Built by Beacon (Campaign Composer for UI, Outreach Sequence
blockedBy=['PAP-43', 'PAP-188', 'PAP-187'] blocks=['PAP-192']
GOAL: Let a tenant plan, approve and publish posts to X, LinkedIn, Instagram, TikTok and YouTube from one calendar, with every post passing through an approval queue before any adapter is allowed to publish. Nothing leaves the system without an approved state; in this build, live publishing is enabled only for accounts Justin connects.
SCOPE: In:

* Drizzle schema `packages/growth/src/social/schema.ts`: `social_account` (`platform`, `external_id`, `handle`, `oauth jsonb` encrypted via `app-shell/env-config` secret helpers, `scopes`, `status`, `expires_at`), `social_post` (`body`, `media_file_ids uuid[]`, `link_url`, `status: draft|pending_approval|approved|scheduled|publishing|published|failed|rejected`, `scheduled_at`, `published_at`, `approved_by`, `rejected_reason`, `source: human|agent`, `campaign_id`), `social_post_target` (post x account, per-platform `variant_body`, `external_post_id`, `metrics jsonb`, `error`), `social_campaign`.
* Adapter interface `packages/growth/src/social/adapters/types.ts`: `validate(post) -> Issue[]` (length, media count, aspect ratio), `publish(target) -> { externalId, url }`, `fetchMetrics(target)`, `refreshAuth(account)`; adapters for X (API v2, `twitter-api-v2` 1.x), LinkedIn (Marketing API
SPEC(first 1200): * Character limits and media rules encoded per adapter and enforced in `validate` and live in the composer (X 280, LinkedIn 3000, Instagram requires media, TikTok video only, YouTube video with title under 100).
* OAuth connect flow via Better Auth generic OAuth or platform SDK; tokens stored encrypted; refresh 24 h before expiry; `status: reauth_required` surfaces a banner.
* State machine transitions are the only writes to `status`; illegal transitions throw `CONFLICT`.
* Every publish writes an `audit_event` and a `crm_activity` when the post links to a campaign contact list.
* Preview renders platform-faithful cards from `packages/ui` components, not iframes.
* Timezone: `scheduled_at` stored UTC, shown in tenant timezone; calendar day boundaries follow tenant.
DOD:
* Vitest: state machine, each adapter's `validate` against fixtures, worker retry and failure paths with mocked adapters, permission checks.
* Integration: X and LinkedIn adapters exercised against sandbox or test accounts in `dryRun: false` once, recording attached; Instagram, TikTok and YouTube verified in `dryRun` with request payload snapshots (app reviews pending, see edge cases).
* Playwright: draft, submit, approve, schedule, worker publishes (mock), calendar shows result; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for calendar, composer and queue.
* axe clean; composer keyboard-only usable.
* `docs/growth/social.md` (connecting accounts, adding an adapter, app review checklist); CHANGELOG entry; Linear comment with recording and screenshots.
EDGE:
* Token revoked at platform: publish fails once, account flagged `reauth_required`, post returns to `approved` with a banner, not `failed`.
* Post approved then edited: returns to `pending_approval`; approval is of exact content (hash stored).
* Scheduled time in the past on approval: publish immediately after confirmation dialog.
* Media over platform limit (LinkedIn 5 images, X 4): validation blocks scheduling.
* Worker crash mid-publish: `publishing` rows older than 10 min are re-checked via `externalId` lookup before retry to avoid duplicates.
* Platform rate limit (429): backoff honours `Retry-After`; other posts to the same account are delayed.
DEPS: `growth/crm-model` (campaign to contact link) and `growth/growth-research` (adapter borrow-vs-build decision) are hard. `data-layer/file-storage`, `tables/calendar-timeline-gantt` (fallback: list view), `app-shell/env-config` (secret storage). Unblocks `growth/content-agent`.


## PAP-191 [P2 Build L prio2 Backlog] Build email and SMS outreach sequences (Resend, Twilio) with warmup and reply detection
key=growth/outreach-sequences milestone=Campaigns and social agent=Built by Beacon (Outreach Sequencer). Reviewed by Sentinel (
blockedBy=['PAP-43', 'PAP-187'] blocks=[]
GOAL: Automate compliant outbound: multi-step email and SMS sequences over Resend and Twilio that enrol CRM contacts, pause on reply, honour consent and quiet hours, warm up new sending domains, and record every touch as a CRM activity. Sending is sandboxed (allowlisted recipients) until Justin flips the tenant flag.
SCOPE: In:

* Schema `packages/growth/src/outreach/schema.ts`: `outreach_sequence` (`name`, `status`, `channel_mix`, `settings jsonb` for quiet hours, timezone mode, daily cap), `outreach_step` (`position`, `channel: email|sms`, `delay_minutes`, `template_id`, `condition jsonb`), `outreach_template` (`subject`, `body_mjml|body_text`, variables, `approved_by`), `outreach_enrolment` (`contact_id`, `sequence_id`, `status: active|paused|replied|bounced|unsubscribed|completed|failed`, `current_step`, `next_send_at`), `outreach_message` (`enrolment_id`, `step_id`, `channel`, `provider_message_id`, `status`, `events jsonb`), `sending_domain` (`domain`, `dns_status`, `warmup_stage`, `daily_limit`, `reputation_score`).
* Providers: Resend Node SDK 4.x (send, domains, webhooks), Twilio Node 5.x (Messaging Service, status callbacks, inbound webhook); provider interface `packages/growth/src/outreach/provid
SPEC(first 1200): * Sandbox mode: tenant setting `outreach.sandbox=true` (default) restricts recipients to `settings.allowlist` and rewrites others to `sandbox+<hash>@paperos.test`; flipping it is `Needs Justin`.
* Warmup schedule: stage caps 20, 50, 100, 250, 500, 1000 per day, advancing after 3 clean days (bounce under 2 percent, complaint under 0.1 percent); regression drops a stage.
* Idempotency: `outreach_message` unique on `(enrolment_id, step_id)`; worker uses `SELECT ... FOR UPDATE SKIP LOCKED`.
* Webhook signatures verified (Resend `svix` headers, Twilio `X-Twilio-Signature`); events appended to `events jsonb` and mapped to status.
* Bounce (hard) sets contact `email_status: invalid` and stops all enrolments; complaint adds to suppression.
* Templates render in a sandboxed renderer with an allowlist of variables; missing variable fails the step in preview, not at send.
DOD:
* Vitest: scheduler selection, condition evaluation, quiet hours across timezones (fixtures for 5 zones), warmup advancement and regression, consent gating, webhook signature verification, reply matching by three strategies.
* Integration test against Resend and Twilio test credentials in sandbox mode: one email and one SMS delivered to allowlisted addresses; STOP round trip; recordings attached.
* Playwright: build a two-step sequence, enrol a contact, fast-forward clock (test hook), see messages and a reply pause; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for builder, enrolments and domain wizard.
* Security review sign-off on webhook endpoints and template rendering.
* `docs/growth/outreach.md` incl. compliance checklist; CHANGELOG entry; Linear comment with demo recording.
EDGE:
* Contact enrolled in two sequences: allowed but a global per-contact cap of one outbound per day unless overridden.
* Contact timezone unknown: fall back to company, then tenant timezone; log the assumption on the message.
* Reply arrives from a different address (forwarded): unmatched inbound lands in an "Unmatched" inbox for manual linking.
* Provider outage: step retried with backoff up to 6 h, then marked `failed` without advancing.
* Template edited while enrolments are mid-sequence: existing enrolments keep the version they started with (`template_version`).
* Daily cap reached mid-batch: remaining sends roll to next window, never dropped.
DEPS: `growth/crm-model` (hard: contacts, consent, activities). `app-shell/env-config` for secrets, `data-layer/audit-log`, `tables/grid-view` for enrolment table. Sequencing templates will be drafted by `growth/content-agent`; replies feed `growth/support-inbox`. Decision on provider set from `growth/growth-research`.


## PAP-192 [P2 Build M prio2 Backlog] Create the content agent character that drafts posts and emails from changelogs and specs for human approval
key=growth/content-agent milestone=Campaigns and social agent=Built by Beacon (lead) with Quill drafting the prompt and vo
blockedBy=['PAP-104', 'PAP-190'] blocks=[]
GOAL: Turn Beacon's Campaign Composer sub-character into a working content agent: a scheduled Claude session that reads merged changelogs, release digests and page specs, drafts social posts, announcement emails and landing copy in the tenant's voice, and files them as `pending_approval` items in the social scheduler and outreach templates. It never publishes; humans approve.
SCOPE: In:

* Character definition `packages/agents/characters/campaign-composer.yaml` completed per `agents/character-schema` (parent Beacon, model `claude-fable-5-1`, effort `high`, `permissionMode: dontAsk` with tools limited to Read, Grep, WebFetch and MCP `paperos-growth` write procedures for drafts only; deny Bash and any publish procedure), prompt `packages/agents/prompts/campaign-composer.md` (identity, voice rules, hard limits, output contract).
* Skill `.claude/skills/draft-campaign/SKILL.md`: inputs (changelog range or spec key, audience segment, channels), steps (gather sources, extract customer-facing changes, draft per-channel variants within limits from `growth/social-scheduler` adapters, self-review against the voice guide, file drafts), output (Linear comment with links to drafts).
* Voice guide `docs/growth/voice.md` per tenant override in `tenant.settings.brand.voice` (tone a
SPEC(first 1200): * Grounding rule: every claim in a draft must trace to a changelog line, spec field or doc; the agent appends a `sources` array; unsupported claims fail self-review and are dropped.
* Output contract JSON: `{ channel, variant_body, media_slots[], link_url, sources[], confidence }` validated by Zod before filing.
* Limits pulled from the adapter `validate` functions so drafts are never over length.
* One session drafts at most 10 items; cost cap from `agents/cost-controls` (`perSessionUsd` 3).
* Approval UI in the social queue shows "Drafted by Campaign Composer" with sources expandable; reject with reason feeds back as a memory note (`agents/memory`).
* Never reads customer PII beyond segment names; prompt forbids quoting contact data.
DOD:
* Character validates (`pnpm agents validate`) and appears in the org chart; smoke task run transcript attached.
* Skill runs end to end against a real changelog range on staging producing at least: 3 X posts, 1 LinkedIn post, 1 announcement email template, 1 landing hero variant, all in `pending_approval`.
* Eval harness scores the three golden fixtures at or above 0.8 on the rubric; results posted to Linear.
* Vitest: output contract validation, limit enforcement, source tracing check.
* Screenshots of the approval queue showing agent drafts with sources at 375, 1024 and 1920.
* `docs/agents/campaign-composer.md` and voice guide; CHANGELOG entry; Linear comment with draft links and eval scores.
EDGE:
* Changelog contains only internal changes: agent files nothing and comments "no customer-facing changes" rather than inventing.
* Tenant has no voice settings: uses the PaperOS default guide and flags it in the comment.
* Spec marked `draft: true`: excluded from sources unless the request names it explicitly.
* Same release drafted twice (re-run): dedupe on `(source_hash, channel)`; existing drafts updated, not duplicated.
* Draft references a feature behind an entitlement: adds an audience note so approvers target the right segment.
* Model refusal or partial output: session ends with a Linear comment and no partial drafts filed.
DEPS: `growth/social-scheduler` and `agents/roster-v1` (hard). `agents/skills-library`, `agents/eval-harness`, `agents/cost-controls`, `identity/agent-principals`, `collab/changelog` (source), `growth/outreach-sequences` and `growth/landing-forms` for the other draft targets (soft; skip channel if absent).


## PAP-193 [P2 Build M prio3 Backlog] Publish landing pages via the Webflow API and capture forms into the CRM
key=growth/landing-forms milestone=Campaigns and social agent=Built by Beacon (Campaign Composer for editor, CRM Builder f
blockedBy=['PAP-187'] blocks=[]
GOAL: Close the loop from marketing page to CRM record: publish landing pages to the tenant's Webflow site through the Webflow Data API, embed a PaperOS form on them, and capture every submission as a `crm_lead` with UTM attribution, spam filtering and instant notification, so campaigns produce leads without manual export.
SCOPE: In:

* Schema `packages/growth/src/landing/schema.ts`: `landing_page` (`title`, `slug`, `webflow_site_id`, `webflow_page_id`, `webflow_item_id`, `status: draft|pending_approval|published|archived`, `content jsonb` blocks, `seo jsonb`, `form_id`, `published_at`), `lead_form` (`name`, `fields jsonb` schema, `success_action`, `notify_user_ids`, `honeypot_field`, `recaptcha: none|turnstile`), `form_submission` (`form_id`, `payload jsonb`, `lead_id`, `utm jsonb`, `referrer`, `ip_hash`, `user_agent`, `spam_score`, `status: accepted|spam|error`).
* Webflow integration `packages/growth/src/landing/webflow.ts` using `webflow-api` 3.x: OAuth connect per tenant, list sites, publish to a CMS collection "Landing Pages" (created if missing with fields matching `content`) and trigger site publish; fallback path writes static HTML to the app's GitHub Pages demo (`app-shell/gh-pages-demo`) when no Webflo
SPEC(first 1200): * Public submit endpoint is the only unauthenticated write in the API: CORS restricted to origins registered on the form (`allowed_origins[]`), 20 req/min per IP, 64 KB body max.
* Field types: text, email, phone, select, checkbox, textarea, hidden; email and phone validated server-side; consent checkbox writes `crm_contact.consent`.
* Publishing requires `landing.publish` permission; agent drafts (`growth/content-agent`) stop at `pending_approval`.
* Webflow CMS mapping stored per site so renaming fields does not break publish; publish is idempotent by `webflow_item_id`.
* Success action: inline message, redirect URL, or calendar link; all render without JS errors when embedded on a third-party page.
* PII: `ip_hash` is SHA-256 with tenant salt; raw IP never stored.
DOD:
* Vitest: field validation, spam scoring, lead upsert, UTM extraction, CORS and rate limit middleware, Webflow mapping.
* Integration: publish a page to the connected Webflow staging site and submit the embedded form from the live page (recording attached); Pages fallback verified too.
* Playwright: build page, build form, publish, submit, see lead in `growth/crm-views`; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for editor, form builder and a published page.
* `form.js` size budget test under 8 KB gzipped; works in Chrome, Safari and Firefox (Playwright projects).
* `docs/growth/landing-forms.md` with the Webflow setup steps; CHANGELOG entry; Linear comment with live page URL and screenshots.
EDGE:
* Webflow publish quota exceeded: page stays `pending_publish` with retry at next window and a banner.
* Duplicate submission (double click): idempotency key from client nonce for 5 minutes.
* Submission for a form that was archived: 410 with friendly message, no lead created.
* Email matches an existing customer contact: lead created and linked, contact not overwritten; activity logged.
* Page embedded on an origin not in the allowlist: 403 and a settings hint in the submissions log.
* Turnstile unavailable: fail open for accepted-with-flag when honeypot passes; flagged submissions reviewed in grid.
DEPS: `growth/crm-model` (hard). `data-layer/api-layer` (public route pattern), `app-shell/gh-pages-demo` (fallback), `collab/notifications`, `input/drag-drop`. Feeds `growth/attribution` and receives drafts from `growth/content-agent`.


## PAP-194 [P2 Build M prio3 Backlog] Track acquisition analytics (UTM, referral, funnel) with a privacy-first event pipeline
key=growth/attribution milestone=Acquisition analytics agent=Built by Beacon (CRM Builder) with Nova (Views Engineer) for
blockedBy=['PAP-43', 'PAP-187'] blocks=[]
GOAL: Know which channel, campaign and page produced each lead, signup and paying customer without shipping a third-party tracker: a first-party, cookieless event pipeline that records UTM and referral touches, stitches anonymous visitors to CRM contacts on identify, and renders funnel and channel reports as table views.
SCOPE: In:

* Schema `packages/growth/src/attribution/schema.ts`: `attr_event` (`id uuidv7`, `tenant_id`, `anonymous_id`, `contact_id` nullable, `user_id` nullable, `name`, `properties jsonb`, `utm jsonb`, `referrer_host`, `landing_path`, `session_id`, `device_class`, `occurred_at`; partitioned monthly), `attr_identity` (`anonymous_id` -> `contact_id|user_id`, `linked_at`, `method`), `attr_touch` (first and last touch per contact: `channel`, `campaign`, `source`, `medium`, `content`, `term`, `at`), `attr_funnel` (named step sequences).
* Collector: `POST /api/v1/public/collect` accepting batched events (max 50, 32 KB), CORS to registered origins, no cookies; `anonymous_id` generated client-side and kept in `localStorage`; server derives `device_class` from UA and discards UA and IP after hashing into `session_id` salt.
* Client SDK `packages/growth/src/attribution/client.ts` (under 4 KB gzipped
SPEC(first 1200): * Event names namespaced: `page_viewed`, `form_submitted`, `lead_created`, `signup_completed`, `subscription_started`; custom events `custom.*`.
* Identify stitching: when `identify` arrives, all prior events with that `anonymous_id` are attributed to the contact; first touch is the earliest event's UTM or referrer; last touch is the latest before conversion.
* Retention: raw events 13 months (partition drop), touches indefinite.
* Aggregations computed by the view query compiler (`tables/query-compiler`) over materialised daily rollups `attr_daily` refreshed by a pg-boss job every 15 minutes.
* Revenue attribution joins Stripe invoices paid to contact via company; unknown mapping reported as "Unattributed revenue", never silently dropped.
* Public collector rate limit 120 events/min per `anonymous_id`.
DOD:
* Vitest: channel classification against 40 referrer and UTM fixtures, identify stitching, first and last touch computation, batch validation and limits, rollup correctness against raw events.
* Playwright: land with UTM, submit a form (mock), sign up, see the contact's touches on the CRM detail and the channel report updated after rollup; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for channel report and funnel view.
* Load test: 1,000 events/s sustained for 5 minutes on staging with p95 ingest under 100 ms (k6 script committed).
* Privacy review by Sentinel (Security Auditor): no IP or UA stored raw; consent modes verified.
* `docs/growth/attribution.md` (event names, adding a channel rule, privacy stance); CHANGELOG entry; Linear comment with report screenshots and load test summary.
EDGE:
* `localStorage` blocked (private mode): `anonymous_id` per page load; events still count as visits, stitching unavailable.
* Two anonymous ids for one contact (phone then laptop): both linked in `attr_identity`; first touch is the earliest across devices.
* UTM with unusual casing or spaces: normalised lowercase and trimmed before classification.
* Bot traffic: known bot UA list drops events before storage; suspicious bursts flagged in the report.
* Contact deleted or exported (`migration/export`): events anonymised by nulling `contact_id`, not deleted.
* Referrer stripped by browser policy: classified as direct, counted separately as "direct (unknown referrer)".
DEPS: `growth/crm-model` (hard). `growth/landing-forms` (embed hook), `tables/query-compiler`, `tables/dashboard-blocks`, `business-core/stripe-billing` (revenue join, soft), `growth/referral-program` (affiliate channel, soft). Decision on Umami/PostHog vs own table from `growth/growth-research`.


## PAP-195 [P2 Build M prio3 Backlog] Build audience segments from CRM and product usage that feed campaigns and in-app targeting
key=growth/segments milestone=Acquisition analytics agent=Built by Beacon (CRM Builder) with Nova (Views Engineer) on 
blockedBy=['PAP-166', 'PAP-187'] blocks=[]
GOAL: Let staff define audiences once and use them everywhere: segments built from CRM fields, product usage events and billing state through the shared filter builder, evaluated dynamically or frozen as static lists, and exposed to outreach sequences, social campaigns and in-app targeting (banners, feature flags, portal messages) through one `segments.membersOf` API.
SCOPE: In:

* Extend `crm_segment` from `growth/crm-model`: `definition jsonb` uses the filter tree grammar of `tables/filter-sort-group-ui` over a virtual "audience" data source joining `crm_contact`, `crm_company`, `crm_deal` aggregates, `attr_event` counts (`growth/attribution`), entitlements and plan (`business-core/entitlements`), and `user` login recency; `refresh: realtime|hourly|manual`; `size_estimate`; `owner`.
* Evaluator `packages/growth/src/segments/evaluate.ts`: compiles the filter tree through `tables/query-compiler` to SQL producing `(tenant_id, segment_id, contact_id)` membership; incremental mode recomputes only contacts touched since `last_evaluated_at` (via `updated_at` and event watermarks); pg-boss job per segment on its refresh schedule.
* API: `segments.list/get/create/update/archive`, `segments.preview(definition) -> { count, sample[] }` (limit 10, under 2 s), `segments
SPEC(first 1200): * Grammar additions to the filter builder: relative dates (`in the last 30 days`), event count comparators (`performed X at least N times in window`), aggregate on related (`has deal with stage kind won`), set membership (`in segment S`, no cycles).
* Evaluation is set-based SQL; a segment with over 1M candidate rows runs in batches of 50k with a progress row.
* Dynamic membership changes emit `segment.entered|exited` events with the contact id for consumers.
* Segment definitions are versioned (`definition_version`, previous stored) so a sequence can show which version enrolled a contact.
* `preview` runs with `statement_timeout 2000` and returns `estimated: true` from `EXPLAIN` row estimates when exceeded.
* Permissions `segment.read|write|use`; `use` allows selecting a segment without seeing its definition.
DOD:
* Vitest: grammar compilation for each new operator, incremental evaluation equals full evaluation on fixtures, cycle detection for nested segments, enter/exit events, `contains` correctness.
* Performance: 200k contact fixture; full evaluation of a five-clause segment under 10 s, incremental under 1 s, `contains` under 20 ms (bench committed).
* Playwright: build a segment with three clauses including an event clause, see live count, freeze, use it in a sequence; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for list and builder.
* axe clean; filter builder keyboard-operable (inherits from `tables/filter-sort-group-ui`).
* `docs/growth/segments.md` (operators, refresh modes, targeting hook); CHANGELOG entry; Linear comment with screenshots and bench numbers.
EDGE:
* Segment references a custom field later deleted: definition marked invalid, evaluation paused, owner notified; members retained.
* Contact matches then unmatches within one refresh window: exit event only if it was a member at the last evaluation.
* Nested segment archived: parent becomes invalid with a clear message rather than silently shrinking.
* User with no CRM contact (staff testing portal): `useInSegment` returns false, no error.
* Timezone-relative dates: evaluated in tenant timezone; documented.
* Manual refresh spammed: coalesced; at most one evaluation in flight per segment.
DEPS: `growth/crm-model` and `tables/filter-sort-group-ui` (hard). `tables/query-compiler`, `growth/attribution` (event clauses; skip operator if absent), `business-core/entitlements` (plan clauses, soft), `identity/customer-portal-shell` for the targeting hook demo.


## PAP-196 [P2 Build L prio4 Backlog] Implement a referral and affiliate program with Stripe Connect payouts
key=growth/referral-program milestone=Acquisition analytics agent=Built by Beacon (CRM Builder) with Ledger (Payments Integrat
blockedBy=['PAP-181'] blocks=[]
GOAL: Let customers and partners recruit customers: referral codes and affiliate links that attribute signups and paid conversions, calculate rewards (credit, discount or cash), and pay cash rewards through Stripe Connect transfers with ledger postings, all with fraud checks and a customer-facing referral page in the portal.
SCOPE: In:

* Schema `packages/growth/src/referral/schema.ts`: `referral_program` (`name`, `kind: referral|affiliate`, `reward jsonb` `{ referrer: { type: credit|discount|cash, amount, currency|percent, trigger: signup|first_payment|each_payment, months? }, referee: {...} }`, `terms_url`, `status`), `referral_code` (`program_id`, `owner_contact_id|owner_user_id`, `code` unique per tenant, `landing_url`, `clicks`), `referral` (`code_id`, `referee_contact_id`, `referee_customer_id` (Stripe), `status: clicked|signed_up|qualified|rewarded|rejected`, `qualified_at`, `fraud_flags jsonb`), `referral_reward` (`referral_id`, `beneficiary`, `type`, `amount_cents`, `status: pending|approved|paid|voided`, `stripe_transfer_id`, `ledger_entry_id`, `paid_at`), `affiliate_account` (`contact_id`, `stripe_connect_account_id`, `onboarding_status`, `tax_form_status`).
* Link handling: `/r/{code}` route records a c
SPEC(first 1200): * Codes: 8 characters, Crockford base32, case-insensitive, customisable vanity codes with profanity filter.
* Attribution window 30 days from click (per program); last click wins unless a code was entered manually at checkout.
* Fraud rules: self-referral (same email domain plus same payment fingerprint), disposable emails, more than 5 signups from one `ip_hash` per day, refunded first invoice voids the reward; flags require staff review before payout.
* Cash rewards accrue in `pending` until the referee's first invoice is 30 days past refund window; then `approved`.
* Ledger accounts used: `6200 Marketing - Referral rewards`, `2100 Affiliate payables`, `1000 Cash`; all postings idempotent by `referral_reward.id`.
* Terms acceptance recorded per affiliate with version and timestamp.
DOD:
* Vitest: code generation and normalisation, attribution window and precedence, reward rule evaluation for the three trigger types, fraud rules against fixtures, ledger posting balances.
* Stripe test mode integration: signup with code, pay first invoice, reward approved after fast-forward, transfer created to a test Connect account; recording attached.
* Playwright: portal referral page share flow and status list; console approval queue; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for portal page and approval queue.
* Permission tests: customer sees only own referrals; staff `referral.approve` required for payouts.
* `docs/growth/referrals.md` incl. fraud and accounting notes reviewed by Ledger; CHANGELOG entry; Linear comment with recording.
EDGE:
* Referee already an existing customer: referral `rejected` with reason, referrer notified politely.
* Referrer without a Connect account earns cash: reward stays `approved`, portal shows onboarding CTA; expires after 180 days to `voided` with notice.
* Currency mismatch between program and referee invoice: convert at invoice-day rate from finance rates; store both amounts.
* Refund after payout: negative reward created and netted against future payouts; ledger reversal posted.
* Code shared publicly and hits 1,000 signups a day: program-level daily cap pauses rewards, not signups.
* Stripe transfer fails (account restricted): reward back to `approved` with error surfaced; retry manual.
DEPS: `business-core/stripe-connect` (hard). `business-core/stripe-billing` (webhooks), `business-core/ledger` (postings), `business-core/invoicing` (statement PDF, soft), `identity/customer-portal-shell`, `growth/attribution` (click channel), `growth/crm-model` (contacts).


## PAP-197 [P2 Build L prio3 Backlog] Build a shared support inbox (email and in-app chat) linked to CRM contacts
key=growth/support-inbox milestone=Acquisition analytics agent=Built by Beacon (CRM Builder) with Nova consulted on live ch
blockedBy=['PAP-131', 'PAP-187'] blocks=[]
GOAL: Put every support conversation next to the customer record: a shared inbox that receives email (Resend inbound) and in-app chat from the customer portal, threads them into conversations linked to CRM contacts and companies, lets staff assign, tag, reply and add internal notes using the comments system, and shows the conversation history on contact and company pages.
SCOPE: In:

* Schema `packages/growth/src/support/schema.ts`: `support_mailbox` (`address`, `display_name`, `signature`, `auto_reply`), `support_conversation` (`mailbox_id`, `contact_id`, `company_id`, `channel: email|chat`, `subject`, `status: open|pending|snoozed|resolved`, `assignee_user_id`, `priority`, `tags`, `snoozed_until`, `first_response_at`, `resolved_at`, `sla jsonb`), `support_message` (`conversation_id`, `direction: inbound|outbound|note`, `author_id`, `author_kind`, `body_json`, `body_text`, `body_html_sanitised`, `attachments uuid[]`, `provider_message_id`, `headers jsonb`, `delivered_at`, `read_at`), `support_canned_reply`.
* Inbound email: Resend inbound webhook -> `support.inbound`; parse with `mailparser` 3.x, sanitise HTML with `sanitize-html` 2.x, strip quoted history, thread by `In-Reply-To`, `References` and subject plus sender fallback, upsert `crm_contact` by sender.
*
SPEC(first 1200): * Contact matching: exact email, then plus-address stripped, then domain to company only (conversation unlinked from contact but linked to company).
* Sanitisation allowlist: basic formatting, links with `rel="noopener"`, inline images rewritten to stored files; scripts and styles removed.
* Status rules: inbound message reopens `resolved` within 7 days, else new conversation; outbound reply sets `pending`; snooze unsnoozes on inbound.
* Permissions: `support.read|reply|assign|manage`; customers see only their own conversations in the portal; agents (`identity/agent-principals`) may add notes, not reply.
* Chat widget works unauthenticated with email capture, upgrading to the contact on login.
* All inbound events audited; every reply logged as `crm_activity kind email`.
DOD:
* Vitest: threading heuristics on 30 fixture emails (Gmail, Outlook, Apple Mail quoting), sanitiser, contact matching precedence, status rules, permission matrix.
* Integration: send a real email to the staging mailbox, see it in the inbox, reply, receive reply threaded (recording attached).
* Playwright: portal chat message appears in console within 1 s and reply returns; internal note with mention; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for inbox, conversation and portal widget (single-pane under `lg`).
* axe clean; inbox fully keyboard-operable.
* `docs/growth/support.md` (mailbox setup, DNS, macros); CHANGELOG entry; Linear comment with recording and screenshots.
EDGE:
* Auto-reply loops (out-of-office ping-pong): detect `Auto-Submitted` and `Precedence: bulk` headers; never auto-reply to auto-replies.
* Attachment over 25 MB or blocked type: stored reference with warning, not dropped silently.
* Same email CC'd to two mailboxes: one conversation per mailbox, cross-linked.
* Customer writes from a new address: new contact suggested for merge with existing (manual).
* Chat from a customer whose company has 3 staff contacts: conversation links the individual; company visible in sidebar.
* Resend inbound webhook retried: dedupe on `provider_message_id`.
DEPS: `growth/crm-model` and `collab/comments` (hard). `realtime/record-sync` and `realtime/presence` for chat (fallback: 3 s polling), `data-layer/file-storage`, `identity/customer-portal-shell`, `growth/outreach-sequences` (replies to sequences open conversations), `input/command-registry`.
