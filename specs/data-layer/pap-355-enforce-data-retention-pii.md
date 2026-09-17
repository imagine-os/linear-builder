---
identifier: "PAP-355"
title: "Enforce data retention, PII classification and tenant hard-purge: `pii` column annotations driving redaction and OTel filters, per-table retention jobs, and the export-first purge after the grace period"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-38", "PAP-43"]
blocks: ["PAP-221"]
key: "security/retention-pii"
url: "https://linear.app/paperos/issue/PAP-355/enforce-data-retention-pii-classification-and-tenant-hard-purge-pii"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:36.963Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-355: Enforce data retention, PII classification and tenant hard-purge: `pii` column annotations driving redaction and OTel filters, per-table retention jobs, and the export-first purge after the grace period

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

GDPR storage limitation and the platform's own hygiene need three things nobody owns: a single PII classification on the schema that redaction, telemetry filters and the DSAR registry (PAP-221) all read; retention rules per table executed by scheduled jobs; and the tenant hard-purge PAP-33 defers to "a separate job", which must export first (PAP-205), then delete every row, file, Yjs document and key for the tenant.

Merges `gap/data-layer/retention-pii` (same deliverable) and the hard-purge half of `gap/data-layer/tenant-lifecycle` (merged 2026-09-17, FIX-6). From them: tenant-level retention overrides within legal bounds with defaults picked by the PAP-126 compliance profile (7-year finance retention), tables tagged immutable (PAP-179, PAP-180) are never touched, the purge refuses without a completed PAP-205 export and lands in Needs Justin when the tenant has paid history in the last 90 days, and the PAP-88 digest reports rows deleted and anonymised per table. `gap/data-layer/tenant-lifecycle` keeps tenant states, quotas and the `requestDeletion`/`cancelDeletion` flow and schedules `tenant.purge` from here.

**Scope**

* In: `pii()` Drizzle column annotation and `packages/db/src/pii/registry.ts`, generated `pii.json`, consumers (PAP-38 `audit_redactions`, PAP-40 span processor, PAP-107 redaction map, PAP-221 registry), `retention.yaml` and job `retention.run` (PAP-43), tenant purge job `tenant.purge` with grace period, legal hold flag, `docs/data/retention.md`.
* Out: per-user erasure (PAP-221 uses the registry), legal text, backups (immutable; purge propagates when retention expires, documented), marketing consent (growth consent centre).

**Spec**

* Annotation: `pii(column, { kind: 'identifier' | 'contact' | 'content' | 'financial' | 'credential' | 'location', subject: 'user' | 'contact' | 'employee' })`; `pnpm pii:build` writes `packages/db/generated/pii.json`; lint fails when a column named `email|phone|name|address|ssn|tax_id|iban|dob|ip` lacks an annotation (PAP-221 currently plans the same check; this issue owns it and PAP-221 imports).
* Consumers: PAP-38 redactions for `credential` and `financial`; PAP-40 span processor denies attribute keys matching any annotated column name; PAP-107 hook adds annotated sample values from fixtures to its redaction set; PAP-41 data dictionary shows the PII kind; PAP-205 export marks PII files in the manifest.
* Retention: `ops/data/retention.yaml` entries `{ table, column: created_at|updated_at|ended_at, keep: '24 months' | '90 days', action: delete | anonymise, anonymise?: { column: strategy } }`; defaults: `audit_event` 24 months (PAP-38 archive then drop), `prompt_event` 180 days (PAP-129 already), `session` 90 days after expiry, `impersonation` records 24 months, `webhook_delivery` 30 days, `import_run_item` 90 days, `presence` none (ephemeral), analytics events (PAP-194) 13 months anonymised after 90 days (IP truncated, user id hashed); job `retention.run` nightly 02:00 UTC in batches of 5,000 with a per-run time box, writes one `audit_event` summary per table.
* Tenant purge: tenant `deleted_at` starts a 30-day grace (configurable per plan); day 0 owners receive notice with an export link (PAP-205 job enqueued automatically); day 30 `tenant.purge` runs: revoke sessions and keys, delete Yjs docs (PAP-140), delete MinIO prefix (PAP-37), delete rows table by table in FK order using `paperos_owner` inside an audited `app.bypass` transaction (PAP-34), retire data keys (PAP-353), keep a `tenant_tombstone (tenant_id, purged_at, export_sha256, row_counts jsonb)`; refuses when `legal_hold = true`.
* Legal hold: `tenant.legal_hold` and `user.legal_hold` booleans settable by owner or admin with reason; retention and purge skip held scopes and report them.

**Interface contract**

* Provides: `pii()` annotation, `pii.json`, `retention.yaml` schema, jobs `retention.run`, `tenant.purge`, `tenant.export_before_purge`, events `tenant.purged`, `retention.completed`, table `tenant_tombstone`, `legal_hold` flags.
* Consumers: PAP-221 (registry), PAP-38, PAP-40, PAP-107, PAP-41, PAP-205, PAP-33 (`deleted_at` semantics), PAP-178 (plan grace period), PAP-219 controls `SEC-PRIV-*`.
* Requires: PAP-33 entities, PAP-43 jobs, PAP-38 audit, PAP-37 storage, PAP-140 docs table.

**Definition of done**

* Lint catches an unannotated `phone` column; `pii.json` lists every annotated column with kind and subject.
* Retention run on a seeded database deletes and anonymises exactly the expected rows (fixture with rows straddling the boundary); audit summary rows present.
* Tenant purge on a seeded tenant with tables, files, docs and encrypted secrets leaves zero rows (`pnpm tenant:verify-purged` checks every tenant table), zero objects and a tombstone whose `export_sha256` matches the export produced at day 0 (compressed schedule in tests).
* Legal hold blocks purge and retention with a clear report.
* OTel test: an annotated attribute never reaches the exporter.
* Docs; changelog under "Security"; Linear comment.

**Test plan**

* Unit: annotation parser, retention schema, boundary arithmetic, anonymisation strategies.
* Integration: PGlite fixtures for retention and purge; FK-order deletion generated from `information_schema`.
* e2e: staging tenant deleted with a 1-minute grace override; export link works; purge verified.
* No UI beyond the existing settings page adding `Delete organisation` with the grace explanation.

**Demo**

Delete a seeded tenant in the console, open the export link from the notice, fast-forward the grace in staging, watch `tenant.purge` complete and `pnpm tenant:verify-purged <id>` print zeros. Two minutes.

**Edge cases**

* Purge fails mid-way: job is resumable per table with checkpoints; tombstone written only at the end; partial state is invisible because the tenant is already inaccessible.
* Backups still contain the data: documented; backups expire per PAP-30 and PAP-354 retention; restores of purged tenants re-run the tombstone check and purge again.
* Shared global rows (`user` in two tenants): membership rows deleted, user retained; PAP-221 handles the person.
* Ledger periods locked (PAP-179): purge of a tenant deletes its ledger too; per-user erasure keeps pseudonyms (PAP-221).
* Retention on partitioned tables: drop whole partitions when every row is past retention, else row deletes.

**Dependencies**

Blocked by PAP-33, PAP-43, PAP-38. Blocks PAP-221. Soft: PAP-37, PAP-140, PAP-205, PAP-353.

**Agent**

Built by Forge (Schema Wright sub-agent); reviewed by Sentinel (Security Auditor) and Ledger for finance tables.

**Size**

M
