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
blockedBy: ["PAP-33"]
blocks: ["PAP-189", "PAP-190", "PAP-191", "PAP-193", "PAP-194", "PAP-195", "PAP-197"]
key: "growth/crm-model"
url: "https://linear.app/paperos/issue/PAP-187/model-crm-entities-lead-contact-company-deal-pipeline-stage-activity"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-187: Model CRM entities: lead, contact, company, deal, pipeline stage, activity, segment

**Goal**

Define the customer graph every PaperOS app shares: leads, contacts, companies, deals, pipeline stages, activities and segments, as Drizzle tables on the core entity conventions, with the page specs and data contract that `growth/crm-views`, `growth/outreach-sequences`, `growth/segments` and `growth/support-inbox` build on. This is a Spec issue: schema, procedures, three page specs and the written contract, not UI.

**Scope**

In:
- Drizzle schema `packages/growth/src/crm/schema.ts`: `crm_company`, `crm_contact`, `crm_lead`, `crm_pipeline`, `crm_pipeline_stage`, `crm_deal`, `crm_activity`, `crm_segment`, `crm_segment_member`, `crm_tag`, `crm_entity_tag`, `crm_external_ref`.
- Every table carries `tenant_id` (RLS via `data-layer/rls-tenancy`), `workspace_id`, uuid v7 `id`, `created_at`, `updated_at`, `archived_at`, `created_by` (human or agent principal), `owner_user_id`, `custom jsonb` for fields added through `tables/field-types`.
- `drizzle-zod` types in `packages/growth/src/crm/types.ts`; oRPC routers `crm.companies|contacts|leads|deals|activities|segments.list/get/create/update/archive` plus `crm.leads.convert` and `crm.deals.move` (`data-layer/api-layer` conventions: cursor, `limit<=100`).
- Registration of every entity with `data-layer/search` (tsvector on name, email, domain, notes) and with the tables engine as a data source (`tables/view-model-spec` `DataSource` interface) so views are declarative.
- Page specs `specs/crm/pipeline.spec.yaml`, `specs/crm/contacts.spec.yaml`, `specs/crm/company-detail.spec.yaml` per `spec-builder/schema`.
- `docs/growth/crm-model.md`: Mermaid ER diagram, field table, invariants, mapping to Twenty CRM and HubSpot objects (for `migration/*` importers).

Out: UI, sequences, segments logic, importers, dedupe UI beyond the constraint.

**Spec**

- `crm_contact`: `first_name`, `last_name`, `email citext`, `phone` (E.164), `company_id`, `title`, `lifecycle: subscriber|lead|mql|sql|customer|churned`, `source`, `consent jsonb` (`{ email: { status, at, source }, sms: {...} }`), `unsubscribed_at`, `do_not_contact`; unique `(tenant_id, email)` where email not null.
- `crm_company`: `name`, `domain citext` unique per tenant, `industry`, `size_band`, `billing_customer_id` (link to `business-core/finance-data-model` customer), `address jsonb`.
- `crm_lead`: unqualified inbound; `contact_id` nullable, raw `payload jsonb`, `status: new|working|converted|disqualified`, `converted_contact_id`, `converted_deal_id`, `utm jsonb`.
- `crm_pipeline` + `crm_pipeline_stage(name, position, probability 0-100, kind: open|won|lost)`; default pipeline seeded with Lead, Qualified, Proposal, Negotiation, Won, Lost.
- `crm_deal`: `title`, `company_id`, `primary_contact_id`, `pipeline_id`, `stage_id`, `amount_cents bigint`, `currency`, `expected_close_date`, `won_at`, `lost_at`, `lost_reason`, `sort_order`.
- `crm_activity`: `kind: note|call|email|sms|meeting|task|system`, polymorphic `about_type|about_id`, `body_json` (Tiptap), `occurred_at`, `due_at`, `completed_at`, `external_ref` (message id).
- `crm_segment`: `name`, `definition jsonb` (filter tree from `tables/filter-sort-group-ui`), `mode: dynamic|static`, `last_evaluated_at`, `member_count`; members table for static and cached dynamic membership.
- Triggers: stage change on a deal writes a `system` activity and sets `won_at|lost_at` by stage kind; lead conversion is one transaction.
- Permissions `crm.*.read|write|export` declared in the page specs' access sections; `customer.*` audiences never see CRM tables.

**Definition of done**

- Migration applies and rolls back on fresh Postgres 17; `pnpm db:check` clean.
- Vitest: unique email constraint, conversion transaction, stage trigger, cross-tenant RLS harness test, cursor pagination on each router.
- Three page specs validate with `spec-builder/validator`.
- Search registration returns a contact by partial email in the search test.
- ER diagram renders; contract doc reviewed by Quill and Ledger (customer link).
- Drizzle Studio screenshot of seeded demo data at 1280 and 1920.
- CHANGELOG entry; ADR `docs/adr/00xx-crm-model.md`; Linear comment linking doc, migration and downstream issues notified.

**Edge cases**

- Contact with no email (phone-only lead): allowed; uniqueness on phone is advisory, surfaced as a merge suggestion.
- Same person at two companies: one contact, `crm_contact_company` history rows with `from|to` dates; `company_id` is the current one.
- Deleting a pipeline stage with deals: blocked; must move deals first (`crm.deals.move` bulk).
- Amount in a currency the tenant does not use: stored as given; reporting converts using `business-core/finance-data-model` rates.
- 500k contacts in a segment: membership cache paginated; `member_count` approximate until evaluation completes.
- Consent revoked while a sequence is running: `do_not_contact` checked at send time, not enrol time (`growth/outreach-sequences`).

**Dependencies**

`data-layer/core-entities` (hard). Uses `data-layer/rls-tenancy`, `data-layer/api-layer`, `data-layer/search`, `spec-builder/schema` (draft acceptable), `tables/view-model-spec` (DataSource interface; stub if not merged). Unblocks every other growth issue and `migration/*` CRM mappings.

**Agent**

Built by Beacon (CRM Builder) with Forge (Schema Wright) pairing on migrations and RLS. Reviewed by Sentinel (Security Auditor) and Atlas for fit with finance and PM models.

**Size**

M: twelve tables, but the shape drives five downstream issues and two importers.
