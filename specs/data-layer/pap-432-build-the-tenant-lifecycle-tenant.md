---
identifier: "PAP-432"
title: "Build the tenant lifecycle: tenant states, deletion request and cancel flow with grace period, archive metadata, per-tenant storage and row quotas (the purge job itself is `security/retention-pii`)"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: []
blocks: []
key: "gap/data-layer/tenant-lifecycle"
url: "https://linear.app/paperos/issue/PAP-432/build-the-tenant-lifecycle-tenant-states-deletion-request-and-cancel"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:01:57.775Z"
---

# PAP-432: Build the tenant lifecycle: tenant states, deletion request and cancel flow with grace period, archive metadata, per-tenant storage and row quotas (the purge job itself is `security/retention-pii`)

**Goal**

Own the tenant state machine around PAP-33's `deleted_at`: request and cancel deletion with a grace period, the archive metadata kept for legal retention, and per-tenant storage and row counters that feed PAP-178's `storageGb` entitlement. The hard-purge job itself (`tenant.purge`: export first, delete rows, files, docs and keys, tombstone) is owned by `security/retention-pii`; this issue triggers it and displays its progress. Merged: the purge half of this gap moved to `security/retention-pii` on 2026-09-17 (FIX-6).

**Scope**

In:

* States on `tenant`: `active`, `suspended`, `deleted` (soft, `deleted_at`), `purging`, `purged`; grace period default 30 days, configurable per plan.
* Deletion flow: `requestDeletion` sets `deleted_at`, enqueues the PAP-205 export and schedules `tenant.purge` (`security/retention-pii`) at the end of the grace period; `cancelDeletion` clears it; `tenant_archive` (legal minimum: name, owner email, invoice references, dates) is written before the purge runs.
* Quotas: `tenant_usage` (`storage_bytes`, `rows_by_table`, `files`, `users`) refreshed nightly and incrementally on file completion; `checkQuota(tenantId, kind)` helper used by PAP-37 and PAP-35 create procedures; staff usage page.
* Needs Justin gate for purging tenants with paid history in the last 90 days.

Out: the purge job and tombstone (`security/retention-pii`), billing proration (PAP-177), data export format (PAP-205).

**Spec**

* Purge progress is read from the `security/retention-pii` job run and shown on the staff usage page; a tenant in `purging` is inaccessible to every principal.
* Quota overage: soft limit warns at 80 percent, hard limit blocks new writes of that kind with `QUOTA_EXCEEDED`.
* Archive rows encrypted with the `security/field-encryption` helper.

**Interface contract**

Provides: tenant states, tables `tenant_archive`, `tenant_usage`, helper `checkQuota`, error `QUOTA_EXCEEDED`, events `tenant.deletion_requested|deletion_cancelled`, oRPC `tenants.usage|requestDeletion|cancelDeletion`. Consumes: entities (PAP-33), jobs (PAP-43), export (PAP-205), files (PAP-37), audit (PAP-38), entitlements (PAP-178), event bus (`contracts/domain-events`), encryption (`security/field-encryption`), purge job and `tenant.purged` event (`security/retention-pii`).

**Definition of done**

* Demo tenant deletion requested, export enqueued, grace period fast-forwarded in test, `tenant.purge` (`security/retention-pii`) invoked once and the state reaches `purged` (harness output).
* `cancelDeletion` inside the grace period restores `active` (test).
* Quota: uploading past the hard limit returns `QUOTA_EXCEEDED`; usage page screenshots at 768, 1280, 1920.
* `docs/data/tenant-lifecycle.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: state machine; dependency ordering from the table list; quota thresholds.
* Integration (CI compose): request, cancel, re-request; grace expiry invokes the purge job exactly once (idempotency asserted).
* Permission: customer cannot call `requestDeletion` for another tenant.
* Visual: usage page at three widths.

**Demo**

Reviewer requests deletion of a test tenant in the staff console, fast-forwards the grace in test, and watches the state move `deleted` to `purging` to `purged` as the `security/retention-pii` job runs. Under 2 minutes.

**Edge cases**

* User deletes tenant then wants it back within grace: `cancelDeletion` restores `active`.
* Tables added later without a tenant column mapping: the `security/retention-pii` FK-order generator fails the purge dry run; the usage page counts them as unknown.
* Objects still referenced by another tenant (shared templates): reference count check.
* Export older than the grace period: re-export required.

**Dependencies**

PAP-33, PAP-43, PAP-205 (hard). Soft: PAP-37, PAP-38, PAP-178, `contracts/domain-events`, `security/field-encryption`, `security/retention-pii` (purge job).

**Agent**

Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).

**Size**

M
