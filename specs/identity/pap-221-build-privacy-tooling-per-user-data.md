---
identifier: "PAP-221"
title: "Build privacy tooling: per-user data export and erasure (DSAR), consent records, privacy/terms/cookie pages in the portal"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer", "Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-58", "PAP-355"]
blocks: []
key: "identity/privacy-dsar"
url: "https://linear.app/paperos/issue/PAP-221/build-privacy-tooling-per-user-data-export-and-erasure-dsar-consent"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:05.970Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-221: Build privacy tooling: per-user data export and erasure (DSAR), consent records, privacy/terms/cookie pages in the portal

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Let a tenant answer a data subject request without engineering: export everything about one person, erase or anonymise them across every module while keeping ledgers and audit chains intact, record consent, and serve the privacy, terms and cookie pages every business needs. PAP-205 exports a tenant; this issue handles one human.

**Scope**

* In: `packages/privacy` with a subject registry (which tables hold personal data, by column), DSAR job types `privacy.export` and `privacy.erase` on the jobs queue (PAP-43), owner approval step, export bundle, anonymisation strategies, consent table and banner, legal pages with tenant-editable Markdown, request log in the console.
* Out: cookie consent for the marketing site (Webflow, PAP-193), legal text authoring, cross-border transfer assessments.

**Spec**

* Registry: `packages/privacy/src/registry.ts` collects `personalData` annotations from Drizzle schemas (`pii: 'identifier' | 'contact' | 'content' | 'financial'`) plus module registrations; `pnpm privacy:registry` prints the coverage table and fails if a column named `email|phone|name|address` lacks an annotation.
* Export: job gathers rows per registered table where `user_id` or `contact_id` matches, comments and docs authored, files owned (signed URLs), audit events as actor; renders JSON and a human-readable HTML index into a zip in object storage with a 7-day signed link; Postgres reads run under the subject's tenant with RLS.
* Erase: strategies per column `delete | null | hash | pseudonym | retain-legal`; financial documents and ledger lines keep a pseudonym (`Erased user 8f3a`) and the audit chain keeps hashes; Better Auth account deleted last; sessions revoked first. Runs as one transaction per table with a resumable checkpoint.
* Consent: table `consent_record (id, tenant_id, subject_id, purpose, granted, version, source, at)`; `ConsentBanner` for portal users on first visit; purposes declared in `app.spec.yaml` `privacy.purposes`.
* Pages: `/portal/legal/privacy`, `/terms`, `/cookies` rendering tenant Markdown from `tenant.legal jsonb` with version and effective date; console editor at `/console/settings/legal`.
* Requests: `/console/settings/privacy/requests` list with state `requested → approved → running → done`, owner approval required for erase, 30-day SLA timer.

**Interface contract**

* Provides: `registerPersonalData(table, columns)` for modules (growth CRM, business-core, collab); jobs `privacy.export`, `privacy.erase`; events `privacy.request.completed`; routes `privacy.request.create/approve/list` (oRPC).
* Requires: PAP-43 jobs, PAP-58 tenant ownership roles, PAP-37 storage, PAP-38 audit, PAP-179 pseudonym rule for ledgers.
* Tables: `privacy_request`, `consent_record`, `tenant.legal`.

**Definition of done**

* Export for a seeded user with CRM contact, comments, files and invoices yields a zip whose index lists every source table (test asserts table set equals registry).
* Erase then export yields nothing personal; the invoice PDF still renders with the pseudonym; ledger `verifyChain` passes.
* Registry coverage check fails on a seeded unannotated `phone` column.
* Console request flow and portal legal pages screenshotted at 375 and 1280, light and dark; axe clean.
* Sentinel Security Auditor reviews retention exceptions; docs `docs/platform/privacy.md`; changelog under "Identity".

**Test plan**

* Unit: strategy functions, registry validation, SLA timer.
* Integration: export and erase jobs against PGlite fixtures with three modules registered; idempotent re-run after a crash at table 3.
* E2E: owner approves a request, job completes, subject downloads the bundle.
* Visual: request list and legal page stories at seven widths.

**Demo**

In the console open Privacy requests, create an erase request for the seeded customer, approve, watch the job finish, then open that customer's invoice: the name reads `Erased user`. Under two minutes with the seeded tenant.

**Edge cases**

* Subject exists in two tenants: request is per tenant; the other tenant is untouched.
* Erase requested during an open dispute: `retain-legal` hold flag blocks with a reason.
* Files shared with others: ownership transfers to the tenant, content kept, attribution pseudonymised.
* Export larger than 2 GB: streamed zip, multipart upload.
* Consent version bumped: banner reappears once; old records kept.

**Dependencies**

PAP-58, PAP-43 (hard). Soft: PAP-37, PAP-38, PAP-179, PAP-205 (shares exporters), PAP-187 (CRM registration).

**Agent**

Built by Forge (Schema Wright) with Iris on the pages. Reviewed by Sentinel (Security Auditor) and Ledger (financial retention).

**Size**

M: registry plus two jobs and three small pages; correctness of the erase strategies is the risk.
