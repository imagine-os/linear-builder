---
identifier: "PAP-37"
title: "Add S3-compatible object storage (MinIO) with signed uploads and image variants"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-43"]
blocks: ["PAP-180", "PAP-185", "PAP-190", "PAP-197", "PAP-199", "PAP-347", "PAP-354", "PAP-396", "PAP-401", "PAP-410"]
key: "data-layer/file-storage"
url: "https://linear.app/paperos/issue/PAP-37/add-s3-compatible-object-storage-minio-with-signed-uploads-and-image"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:39.358Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-37: Add S3-compatible object storage (MinIO) with signed uploads and image variants

**Goal**

Let any app accept files safely: MinIO per environment, presigned direct uploads from browser and native, server-side validation, automatic image variants and tenancy-respecting signed downloads. Variants run on PAP-43 jobs; this is the reference consumer of that package.

**Scope**

In:

* MinIO via Coolify (`ops/compose/minio.yml`): buckets `paperos-prod`, `paperos-staging`; versioning on; lifecycle purging `pending/` after 24 h; console VPN-only.
* `packages/files` server procedures `files.createUpload`, `files.complete`, `files.getUrl`, `files.delete`, `files.list` registered in PAP-35.
* Variants job `files.variants` (`thumb 256`, `md 1024`, `lg 2048` in WebP and AVIF via `sharp` 0.34).
* Client `uploadFile(file, { onProgress })` with multipart resume; `<FileDrop/>` in `@paperos/ui`.
* Nightly reconciliation job.

Out: document previews, virus scanning (Trivy covers images only; ClamAV is a follow-up), CDN.

**Spec**

* Key layout `<tenant_id>/<yyyy>/<mm>/<file_id>/<slug>`; client filename never trusted for keys; `Content-Disposition` set on GET.
* Presign with `@aws-sdk/client-s3` and `s3-request-presigner`; `x-amz-checksum-sha256` required on PUT.
* `files.complete` HEADs the object, verifies size and sha256, sniffs MIME with `file-type`, rejects rows not `pending` for this actor, enqueues variants.
* Variants only for `image/*` up to 50 MP; EXIF stripped; SVG served with `Content-Security-Policy: sandbox`; HEIC converted.
* Download URLs valid 15 minutes, generated after an RLS-scoped row fetch.
* Every create, complete and delete emits an `audit_event` (PAP-38).

**Interface contract**

Provides:

* oRPC `files.*` procedures with `FileDto = { id, name, mime, size, status, variants: Record<'thumb'|'md'|'lg', { webp: string; avif: string }>, createdAt }`.
* Client `uploadFile`, `useUpload()`, `FileDrop`; server helper `getSignedUrl(fileId, { variant? })` for other routers (PAP-131 attachments, PAP-72 logo, PAP-185 receipts).
* Job `files.variants` defined with `defineJob` (PAP-43).
* Env `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` (PAP-17 names).
* Bucket `paperos-<env>` layout the object-storage DR issue backs up.

Consumes: `file` table (PAP-33), API host (PAP-35), jobs (PAP-43), audit (PAP-38), camera capability for mobile uploads (PAP-20, soft).

**Definition of done**

* Upload a 5 MB JPEG from web and from the Android emulator camera; variants within 10 s (recording).
* Multipart resume: pause at 60 percent, reload, resume, complete (Playwright).
* Vitest: presign params, complete validation, key sanitisation, variant queue; integration against MinIO in CI.
* Cross-tenant `getUrl` returns `NOT_FOUND`.
* `<FileDrop/>` states at 375, 768, 1280, 1920; `docs/data/files.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: slug sanitiser with traversal and control characters; MIME sniff versus header mismatch; size and hash mismatch; zero-byte rejection.
* Integration (CI compose with MinIO): full create, PUT, complete, variants, getUrl round trip; lifecycle rule verified by setting a 1-minute expiry in test.
* Permission: `callAs(tenantB)` on tenant A's file returns `NOT_FOUND`.
* E2E: Playwright drag-and-drop upload and resume; Android emulator camera upload recorded.
* Visual: five `<FileDrop/>` states at four widths, light and dark.

**Demo**

Reviewer drags a photo onto `<FileDrop/>` on the settings example page, watches progress, sees the thumbnail appear, opens the signed URL in a new tab and reloads it after 15 minutes to see it expire. Under 2 minutes (expiry checked later).

**Edge cases**

* Same content twice: allowed; `sha256` index enables dedupe later.
* MinIO down during `complete`: 503 with retry-after.
* Leaked presigned URL: 15-minute expiry documented as a bearer secret.
* Object without row: quarantined prefix by reconciliation.
* Mobile upload on cellular: chunk size 5 MB, resume on reconnect.

**Dependencies**

PAP-33, PAP-43 (hard). Soft: PAP-38, PAP-20. Consumed by PAP-72, PAP-131, PAP-134, PAP-185, growth issues.

**Agent**

Built by Forge (Ops Runner for MinIO, Platform Engineer for the service). Reviewed by Sentinel (Security Auditor).

**Size**

M: one service, one job, one component.
