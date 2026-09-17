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
blocks: ["PAP-180", "PAP-185", "PAP-190", "PAP-197", "PAP-199"]
key: "data-layer/file-storage"
url: "https://linear.app/paperos/issue/PAP-37/add-s3-compatible-object-storage-minio-with-signed-uploads-and-image"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-37: Add S3-compatible object storage (MinIO) with signed uploads and image variants

**Goal**

Let any app accept files safely: a MinIO S3-compatible bucket per environment, presigned direct-to-storage uploads from browser and native targets, server-side validation, automatic image variants (thumbnails, WebP/AVIF) and signed download URLs that respect tenancy.

**Scope**

In:
- MinIO deployed via Coolify (`ops/compose/minio.yml`) with buckets `paperos-prod`, `paperos-staging`, `pg-backups` (from `data-layer/postgres-provision`), versioning on, lifecycle rule purging `pending` objects after 24 h; TLS via Caddy; console restricted to VPN.
- `packages/files/` server: `files.createUpload` (returns presigned PUT, key, file row `status:'pending'`), `files.complete` (HEAD object, verify size and sha256, sniff MIME with `file-type`, set `ready`, enqueue variants), `files.getUrl` (presigned GET 15 min), `files.delete` (soft delete + lifecycle purge), `files.list` — all as oRPC procedures in `data-layer/api-layer`.
- Variants worker: in-process queue (pg-boss 10.x on Postgres) generating `thumb 256`, `md 1024`, `lg 2048` as WebP and AVIF with `sharp` 0.34; stored under `variants/<id>/<name>.<ext>`; `file.variants` JSON updated.
- Client `packages/files/client`: `useUpload()` hook with progress, pause/resume via multipart for files over 50 MB, drag-drop zone component `<FileDrop/>` in `packages/ui`, native picker/camera via capabilities (`app-shell/tauri-mobile`).
- Virus/size policy: per-tenant `settings.files.maxBytes` (default 100 MB) and allowed MIME list; ClamAV optional container documented but off by default.

Out: document previews for Office/PDF (later), CDN, image editing, per-file ACL beyond tenant/workspace (identity handles sharing rules).

**Spec**

- Key layout: `<tenant_id>/<yyyy>/<mm>/<file_id>/<sanitised-filename>`; never trust client filename for key; `Content-Disposition` set on GET.
- Presign with `@aws-sdk/client-s3` + `@aws-sdk/s3-request-presigner` against MinIO endpoint; `x-amz-checksum-sha256` required on PUT.
- `files.complete` rejects mismatched size/sha256, disallowed MIME (server-sniffed, not header), and files whose row is not `pending` for this actor.
- Variant generation only for `image/*` up to 50 MP; SVG stored as-is but served with `Content-Type: image/svg+xml` and `Content-Security-Policy: sandbox`.
- EXIF stripped from variants; original retained.
- Reconciliation job nightly: rows `ready` without object -> `failed`; objects without rows -> quarantined prefix.
- Download URLs generated per request after RLS-scoped row fetch, so tenancy is enforced by the row lookup.
- Audit: every create/complete/delete emits `audit_event` via `data-layer/audit-log`.

**Definition of done**

- Upload a 5 MB JPEG from web and from Android emulator camera; variants appear within 10 s; recording attached.
- Multipart resume test: pause at 60 percent, reload, resume, complete (Playwright).
- Vitest: presign params, complete validation (size, hash, MIME), key sanitisation, variant queue; integration test against MinIO in CI compose.
- Cross-tenant `getUrl` returns `NOT_FOUND` (test).
- Screenshots of `<FileDrop/>` idle, dragging, progress, error, done at 375, 768, 1280, 1920.
- `docs/data/files.md`; CHANGELOG; Linear comment with recording and staging console screenshot.

**Edge cases**

- Filename with path traversal or unicode control chars: sanitised to safe slug plus extension.
- Zero-byte file: rejected.
- Same content uploaded twice: allowed, but `sha256` index enables dedupe UI later.
- HEIC from iPhone: converted to JPEG variants; original kept.
- MinIO down during `complete`: procedure returns 503 with retry-after; client retries with backoff.
- Presigned URL leaked: 15-minute expiry; documents that download URLs are bearer secrets.

**Dependencies**

`data-layer/core-entities` (file table), `data-layer/api-layer` (procedures), `data-layer/audit-log` (soft), `app-shell/tauri-mobile` (camera path, soft). Consumed by `collab/comments` (attachments), `collab/screenshot-annotations`, `design-system/theming` (logo upload), `growth/*`.

**Agent**

Built by Forge (Ops Runner for MinIO, core for service). Reviewed by Sentinel (Security Auditor for presign and MIME handling; Visual Inspector for the drop zone).

**Size**

M: standard S3 patterns, but validation, variants and resume have many details to get right.
