---
key: "child/PAP-205/1"
title: "Export UI, weekly scheduling to S3 or Google Drive with encryption, signed download links, history and audit"
project: "migration"
parent: "PAP-205"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: ["Customer"]
milestone: "Airtable, Notion, ClickUp importers"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
status: "pending"
---

# Export UI, weekly scheduling to S3 or Google Drive with encryption, signed download links, history and audit

**Goal**

Put export in the owner's hands: a settings page to start a scoped export, watch progress, download through a signed link, revoke it, and schedule weekly encrypted exports to the tenant's own S3 bucket or Google Drive.

**Scope**

In: route `_app/settings/export` (start with scope, progress, history, schedule) also shown to portal owners; permission `tenant.export` defaulting to `owner`; signed URLs (7 days, revocable); destinations S3-compatible and Drive via `googleapis`; encryption `age` or zip AES-256 with a passphrase typed twice plus a "PaperOS cannot recover this" confirmation; audit event and owner notification on every export.

Out: format and job (child 1).

**Spec**

* Schedule stored as a PAP-43 cron job per tenant; failures notify owners (PAP-136, email fallback).
* Download link tied to the requesting owner; history shows archive hash and size.
* Destination credentials stored via the data-layer secret helper.

**Interface contract**

Provides: oRPC procedures `export.start`, `export.list`, `export.revokeLink`, `export.schedule.set|get`, permission `tenant.export`, audit action `tenant.exported`, notification kind `export.completed`. Consumes: child 1 job and event, PAP-59 `can()`, PAP-38, PAP-136 (soft), PAP-57 Google connection for Drive.

**Definition of done**

* Start, progress, download, revoke and schedule all work on staging; a scheduled export lands in a MinIO bucket encrypted and decrypts with the passphrase.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for export page and history; axe clean.

**Test plan**

* Vitest: permission checks, link expiry and revocation, schedule serialisation, passphrase confirmation logic.
* Integration: scheduled job to local MinIO, decrypt and verify manifest hash; Drive via recorded API.
* Playwright: full flow with visual baselines at seven widths, both themes.

**Demo**

Reviewer opens Settings > Export, starts a tables-only export, watches progress reach 100 percent, downloads it, revokes the link and confirms it now 403s. Under two minutes.

**Edge cases**

* Passphrase lost: documented as unrecoverable; UI states it before saving.
* Bucket credentials rotated: next run fails with a clear error and notification.
* Exports over 10 GB: UI recommends scheduled destination.

**Dependencies**

Child 1 (hard), PAP-59, PAP-38, PAP-136 (soft), PAP-57.

**Agent**

Built by Scout (Import Mapper) with Iris for the page. Reviewed by Sentinel (Security Auditor for links and redaction, Visual Inspector).

**Size**

M
