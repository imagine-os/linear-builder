---
identifier: "PAP-575"
title: "Platform maintenance and read-only mode: `maintenance` flag, API 503 with `Retry-After` for writes, outbox-aware client banner and `pnpm ops:maintenance on|off|status`"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-267"]
blocks: []
key: "r4/data-layer/maintenance-mode"
url: "https://linear.app/paperos/issue/PAP-575/platform-maintenance-and-read-only-mode-maintenance-flag-api-503-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:09.780Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-575: Platform maintenance and read-only mode: `maintenance` flag, API 503 with `Retry-After` for writes, outbox-aware client banner and `pnpm ops:maintenance on|off|status`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Build S

**Goal**

Migrations with table rewrites, the DR drill, a key rotation and a bad deploy all need a moment where the platform answers reads but refuses writes without breaking clients. Because clients already have an outbox, a maintenance window can be invisible: writes queue locally, the banner explains, and everything replays when the window closes.

**Scope**

In: `packages/api-contract/src/middleware/maintenance.ts` (first in the PAP-267 chain after request id), flag `platform.maintenance` (PAP-366 when present, else `MAINTENANCE_MODE` env plus a `platform_state` row polled every 5 s), response `503 { code: 'MAINTENANCE', message, retryAfter, until? }`, `/api/health` field `maintenance: true`, client handling in `packages/sync` (treat 503 MAINTENANCE like offline for the outbox, no attempt counting) and `MaintenanceBanner` in the shell `banner` slot, CLI `pnpm ops:maintenance on --until <iso> --message`, `docs/ops/maintenance.md`.

Out: Blue-green deploys (PAP-26), per-tenant suspension (PAP-432 states), scheduled announcements (PAP-136 kinds may consume the flag event).

**Spec**

* Read procedures, shapes, health and auth session refresh keep working; every mutation, `files.createUpload`, Hocuspocus writes (`connection.readOnly` set from the same flag through PAP-140's permission re-check) and jobs that write user data pause; `events.dispatch` keeps running.
* Staff and agents may bypass with header `X-PaperOS-Maintenance-Bypass` when the flag rule allows (`bypass: ['staff']`); bypass requests are audited.
* Client: `useConnectionStatus()` (PAP-609, soft) or `useSyncStatus()` reports `maintenance` with `until`; the outbox retries at `Retry-After` without counting attempts; the banner shows the message and the time.
* Flag change publishes `flags.changed` so open clients switch within 5 s; CLI prints the current state and who set it.
* Gate: the deploy pipeline (PAP-26) may wrap `db:migrate` in `on`/`off` when the migration is tagged `requires-maintenance` by PAP-569.

**Interface contract**

Provides: Middleware `maintenance()`, error code `MAINTENANCE`, flag `platform.maintenance`, `MaintenanceBanner`, CLI `ops:maintenance`, health field.

Consumes: Middleware chain (PAP-267), flags (PAP-366, soft), outbox and sync status (PAP-272, PAP-148, soft), shell banner slot (PAP-16), Hocuspocus permission re-check (PAP-140, soft), audit (PAP-38), deploy hook (PAP-26, soft).

**Definition of done**

* With maintenance on, reads succeed, a create returns 503 with `Retry-After`, the sync demo queues the write and the banner shows; turning it off replays within 5 s (Playwright).
* Staff bypass works and is audited; health reports the state; CLI round trip; docs; CHANGELOG; Linear comment with the recording.

**Test plan**

* Unit: middleware decision table (method, procedure kind, bypass header, role), `Retry-After` from `until`, client classification of 503 MAINTENANCE as non-counting.
* E2E: Playwright on the dev stack: toggle through the CLI while editing in the sync demo; assert queue, banner and replay.

**Demo**

Reviewer runs `pnpm ops:maintenance on --until +5m --message 'Migrating'`, edits a workspace name in the app, sees the banner and the pending indicator, runs `off` and watches the edit land. Under a minute.

**Edge cases**

* Flag service down: middleware falls back to the `platform_state` row, then to env; never fails open into writes when the row says on.
* Long window past the outbox's 24 h idempotency expiry: clients regenerate keys on replay (PAP-148 documents), documented as accepted.
* Webhooks from Stripe during maintenance: `/webhooks/*` are exempt and write to their inbox tables (PAP-177); noted in the exemption list.

**Dependencies**

Blocked by PAP-267 (hard). Soft: PAP-366, PAP-272, PAP-148, PAP-16, PAP-140, PAP-38, PAP-26, PAP-569, PAP-609.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/data-layer/migration-safety` = PAP-569, `r4/realtime/connection-status` = PAP-609.
