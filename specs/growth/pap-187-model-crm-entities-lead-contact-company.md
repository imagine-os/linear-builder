---
identifier: "PAP-187"
title: "Model CRM entities: lead, contact, company, deal, pipeline stage, activity, segment"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Staff"]
milestone: "CRM core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-448"]
blocks: ["PAP-189", "PAP-190", "PAP-191", "PAP-193", "PAP-194", "PAP-195", "PAP-197", "PAP-401", "PAP-404", "PAP-410", "PAP-485"]
key: "growth/crm-model"
url: "https://linear.app/paperos/issue/PAP-187/model-crm-entities-lead-contact-company-deal-pipeline-stage-activity"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:04.437Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-187: Model CRM entities: lead, contact, company, deal, pipeline stage, activity, segment

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Spec P1

**Goal**

Define the customer graph every PaperOS app shares: leads, contacts, companies, deals, pipeline stages, activities and segments as Drizzle tables on core conventions, with procedures, three page specs and the written contract that PAP-189, PAP-191, PAP-195 and PAP-197 build on. Spec issue: schema and contract, not UI.

**Scope**

In: `packages/growth/src/crm/schema.ts` with `crm_company`, `crm_contact`, `crm_contact_company`, `crm_lead`, `crm_pipeline`, `crm_pipeline_stage`, `crm_deal`, `crm_activity`, `crm_segment`, `crm_segment_member`, `crm_tag`, `crm_entity_tag`, `crm_external_ref`; `drizzle-zod` types; routers `crm.companies|contacts|leads|deals|activities|segments.*` plus `crm.leads.convert` and `crm.deals.move`; search and dataset registration; page specs `specs/crm/pipeline|contacts|company-detail.spec.yaml`; `docs/growth/crm-model.md` with ER diagram and Twenty/HubSpot mapping.

Also in: work package 0 (below), the consent and marketing compliance centre, formerly the pending issue `gap/growth/consent-centre`, folded into this issue on 2026-09-17 because PAP-191 and PAP-193 depend on it hard and Linear cannot create it (issue cap).

Out: UI (PAP-189), sequences, segment evaluation (PAP-195), importers, cookie banners for the marketing site (PAP-221 owns privacy pages), consent for agent data access (PAP-60).

**Spec**

* Every table: `tenant_id` RLS, `workspace_id`, uuid v7 `id`, timestamps, `archived_at`, `created_by` (human or agent principal), `owner_user_id`, `custom jsonb` for PAP-164 fields.
* `crm_contact`: names, `email citext` unique per tenant where not null, `phone` E.164, `company_id`, `title`, `lifecycle: subscriber|lead|mql|sql|customer|churned`, `source`, `consent jsonb`, `unsubscribed_at`, `do_not_contact`, `email_status`.
* `crm_company`: `name`, `domain citext` unique per tenant, `industry`, `size_band`, `billing_customer_id` (PAP-175 party), `address jsonb`.
* `crm_lead`: `contact_id?`, `payload jsonb`, `status: new|working|converted|disqualified`, `converted_contact_id`, `converted_deal_id`, `utm jsonb`.
* `crm_pipeline` and `crm_pipeline_stage (name, position, probability, kind: open|won|lost)`; default pipeline seeded.
* `crm_deal`: `title`, `company_id`, `primary_contact_id`, `pipeline_id`, `stage_id`, `amount_minor bigint`, `currency`, `expected_close_date`, `won_at`, `lost_at`, `lost_reason`, `sort_key`.
* `crm_activity`: `kind: note|call|email|sms|meeting|task|system`, `about_type|about_id`, `body_json`, `occurred_at`, `due_at`, `completed_at`, `external_ref`.
* `crm_segment`: `name`, `definition jsonb` (`FilterTree`), `mode: dynamic|static`, `last_evaluated_at`, `member_count`.
* Triggers: stage change writes a `system` activity and sets `won_at|lost_at`; conversion is one transaction.
* Permissions `crm.*.read|write|export`; customer audiences never see CRM tables.

**Work package 0: consent and marketing compliance centre (was the pending issue** `gap/growth/consent-centre`**, folded in on 2026-09-17, round-2 FIX-5)**

Numbered 0 because it defines the consent semantics this schema stores; build it after the tables above on branch `PAP-187/wp0-consent-centre`, open the PR as soon as `canContact` and `consent.record` exist, and report it in a comment on this issue. PAP-191 (hard, suppression) and PAP-193 (consent writes) import from that branch and are not blocked by its merge. Replaces three partial implementations (this issue stores it, PAP-191 checks it, PAP-193 writes it) with one: a consent record per contact and channel, a shared suppression list, a public preference and unsubscribe centre, double opt-in, and the rule set that decides whether a message may go out under GDPR, CAN-SPAM and TCPA.

* Tables: `consent_record (contact_id, channel: email|sms|push, purpose: marketing|transactional|product_updates, status: granted|denied|pending_double_opt_in|withdrawn, source, evidence jsonb { ip_hash, user_agent_class, form_id, text_shown, timestamp }, version, granted_at, withdrawn_at)`, append-only with the current row per `(contact, channel, purpose)` exposed through a view; `suppression_entry (tenant_id, kind: email|phone|domain, value_hash, reason: unsubscribe|complaint|hard_bounce|manual|legal, source, created_at)`, global per tenant across sequences, notifications and forms, `suppression.check(values[])` batched; `consent_purpose`. `crm_contact.consent jsonb` becomes a denormalised cache of the current rows.
* `canContact(contactId, channel, purpose)` returns `{ ok, reason }` combining consent, suppression, `do_not_contact`, SMS quiet hours (TCPA) and the purpose rules: transactional allowed without marketing consent, marketing requires `granted`, SMS marketing requires explicit opt-in with evidence.
* Public routes with a signed per-contact token and no login: `/c/:token` preference centre (per channel and purpose toggles, "unsubscribe from all", tenant branding via PAP-74), `/u/:token` one-click unsubscribe (RFC 8058 POST), double opt-in confirm route; changes write consent records and suppression entries. Double opt-in: forms (PAP-169, PAP-193) create `pending_double_opt_in` and send the confirm email through PAP-136 core; unconfirmed after 30 days expires.
* `List-Unsubscribe` and `List-Unsubscribe-Post` headers supplied to PAP-191 and PAP-136 through `unsubscribeHeaders(contactId, channel)`; STOP keywords from PAP-191 write suppression here. Exports: per-contact consent history for DSAR (PAP-221) and a tenant compliance report dataset `growth.compliance`. Staff pages under `_app/marketing/compliance`.
* Interface: `canContact`, `consent.record|withdraw|history`, `suppression.add|check|list`, `preferenceLink(contactId)`, `unsubscribeHeaders`, events `consent.changed`, `suppression.added`. Consumes PAP-136 core, PAP-169 and PAP-193 (write through `consent.record`), PAP-267 rate limiting on the public routes, PAP-74 theming, PAP-43 jobs. Consumed by PAP-191 (hard), PAP-193, PAP-136, PAP-221 exports and PAP-180 work package 4 (reminder consent).
* Edge cases: contact merged (records re-pointed, most restrictive status wins); withdrawal then re-grant (new record with fresh evidence, history intact); suppressed domain refuses every contact at it; leaked token shows no PII beyond a masked email and rotates via `preferenceLink`; `reason: legal` suppression cannot be removed by staff.
* Done when: unit decision table for `canContact` (channel by purpose by status by suppression), token signing and expiry, double opt-in expiry and header generation green; integration: an unsubscribe POST suppresses across a running PAP-191 sequence and a PAP-136 digest in the same test, a form submission with consent goes `pending_double_opt_in` then `granted` on confirm, STOP writes suppression, history export matches records; Playwright: open the preference link, toggle SMS marketing off, confirm the sequence skips the SMS step, one-click unsubscribe from an email header; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the preference centre (two brands) and the staff compliance page, axe clean; `docs/growth/consent.md` with the rule table per jurisdiction; CHANGELOG; Linear comment with a live preference link on the demo tenant. Demo: open a contact's preference link from the CRM page, turn off marketing email, enrol the contact in a sequence and watch `canContact` refuse with the reason, then one-click unsubscribe from a test email and see the suppression entry; under two minutes.

**Interface contract**

Provides: the twelve tables, Zod types `Contact`, `Company`, `Deal`, `Lead`, `Activity`, `Segment`, the routers above with cursor pagination, datasets `crm.contacts|companies|deals|activities`, search registrations, events `crm.deal.stage_changed`, `crm.lead.converted`, `crm.contact.created` on the outbox, three page specs. Consumes: core entities (PAP-33), RLS (PAP-34), API conventions (PAP-268), search (PAP-39), spec schema (PAP-117), `registerDataset` (PAP-161), `FilterTree` (PAP-279), `fin_party` link (PAP-175). Consumed by PAP-189 to PAP-197, PAP-202, PAP-206; work package 0 additionally provides `canContact`, `consent.*`, `suppression.*`, `preferenceLink`, `unsubscribeHeaders`, the public routes `/c/:token` and `/u/:token` and dataset `growth.compliance` to PAP-191, PAP-193, PAP-136, PAP-221 and PAP-180 work package 4.

* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Money`: rename `amount_cents` to `amount_minor bigint` with `currency char(3)` per PAP-175; segment definitions are `FilterTree` from `@paperos/core/filter` (PAP-279), not a CRM-local grammar); §2 (`EntityRef = { type, id }` for activity links where `type` is the PAP-161 dataset key); §3 (register `crm.deal.stage_changed`, `crm.lead.converted`, `crm.contact.created` with `defineTopic`; `segment.entered|exited` belongs to PAP-195); §6 rows "Core entities and Zod types" and "`FilterTree`".

**Definition of done**

* Migration applies and rolls back on Postgres 17; `pnpm db:check` clean; cross-tenant harness green.
* Three page specs validate with PAP-117.
* ER diagram renders; contract doc reviewed by Quill and Ledger.
* Drizzle Studio screenshot of seed data at 1280 and 1920.
* CHANGELOG; ADR `docs/adr/00xx-crm-model.md`; Linear comment linking doc and migration.
* Work package 0 done as listed above (its PR may merge after the schema PR; the issue closes when both are merged).

**Test plan**

* Unit: unique email and domain constraints, conversion transaction rolls back on failure, stage trigger sets `won_at`, cursor pagination on each router, `crm.deals.move` bulk.
* Integration: RLS harness on all tables; search returns a contact by partial email; datasets appear through `getDataset`; outbox events emitted for stage change and conversion.
* E2E and visual: none beyond the Studio screenshots (no UI).

**Demo**

Reviewer runs `pnpm db:seed --profile demo`, opens Drizzle Studio to browse contacts and deals, then runs `pnpm tsx scripts/crm-demo.ts` which converts a lead, moves the deal to Won and prints the resulting system activity and outbox event. Under two minutes.

**Edge cases**

* Phone-only contact allowed; phone uniqueness is a merge suggestion, not a constraint.
* Same person at two companies: `crm_contact_company` history with from and to dates.
* Deleting a stage with deals blocked until moved.
* Foreign-currency amount stored as given; reporting converts via PAP-175 rates.
* Consent revoked mid-sequence: checked at send time by PAP-191 through work package 0's `canContact`.

**Dependencies**

PAP-33 (hard), PAP-34, PAP-268, PAP-39, PAP-117 (draft acceptable), PAP-161 (stub if not merged), PAP-279, PAP-175 (party link). Blocks PAP-189, PAP-190, PAP-191, PAP-193, PAP-194, PAP-195, PAP-197. Work package 0 additionally needs PAP-43 (jobs, hard for double opt-in expiry), PAP-136 core, PAP-169, PAP-74, PAP-267 (soft); PAP-191 and PAP-193 import its `canContact` and `consent.record` from the `PAP-187/wp0-consent-centre` branch, so open that PR early.

**Agent**

Builder: Beacon (CRM Builder) with Forge (Schema Wright) on migrations and RLS; work package 0 by Beacon with Quill on the jurisdiction rule table. Reviewer: Sentinel (Security Auditor, also for the public routes and PII of work package 0; Edge Case Hunter), Atlas for fit with finance and PM models.

**Size**

L: twelve tables whose shape drives five downstream issues and two importers (M), plus work package 0, a decision function, two public pages and append-only tables (M). The Type label stays Spec because the schema contract is the deliverable other issues wait on; work package 0 is Build work carried here only because of the issue cap.
