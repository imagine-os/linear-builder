---
key: "pm-linear/linear-sync/inbound"
title: "Linear sync: backfill and inbound webhook upsert into pm_* tables"
project: "pm-linear"
parent: "PAP-101"
phase: "P2"
type: "Build"
priority: null
size: "M"
surfaces: ["Staff"]
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: ["pm-linear/linear-sync/outbound", "pm-linear/linear-sync/conflicts"]
source: "round2/agent2/new_pm.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-pm-linear-9-d4829fc00859"
identifier: "PAP-372"
status: "created"
createdAt: "2026-09-17"
---

# Linear sync: backfill and inbound webhook upsert into pm_* tables

**Goal**

Bring Linear into PaperOS: a resumable backfill of team PAP and an incremental inbound path that upserts every webhook payload into the `pm_*` tables through `pm_external_ref`, so PaperOS always has a faithful read-only mirror before any outbound writes exist.

**Scope**

* In: `packages/pm-sync/src/{backfill,inbound,mapping-apply}.ts`, `pm_sync_cursor` table, principal mapping by email and bot account, `pm.sync.backfill()` procedure, handler registration on the PAP-97 receiver.
* Out: outbound writes (`pm-linear/linear-sync/outbound`), conflict resolution and status page (`pm-linear/linear-sync/conflicts`).

**Spec**

* Backfill: paginated `issues(first: 100, after, includeArchived: true, orderBy: updatedAt)` plus teams, states, projects, milestones, cycles, labels, comments, attachments and relations; cursor per entity type in `pm_sync_cursor(entity_type, cursor, last_updated_at)`; resumable; full PAP backfill under five minutes at 300 ms between requests.
* Inbound: on `Issue | Comment | Project | ProjectMilestone | IssueLabel | Cycle | IssueRelation | Attachment` events, map `data` through `mapping.ts` (PAP-100), upsert by `(system: "linear", external_id)`, set `external_updated_at`, `source: "linear"`; `updatedFrom` records changed fields into `pm_sync_change(entity, field, at)` for the conflict child; `remove` and archive set `archived_at`.
* Users: `pm_external_ref` for Linear users to principals by email; unknown users become placeholder external principals (PAP-60 `kind: external`); the nine bot accounts map to agent principals.
* Unknown fields stored in `extra` jsonb; nothing dropped.

**Interface contract**

* Provides: `backfill({ since? })`, `applyInbound(event)`, `pm.sync.backfill()`, table `pm_sync_cursor`, `pm_sync_change`, event `pm.sync.inbound.applied { entity, id }`.
* Consumers: sibling children; PAP-102 renders mirrored data; PAP-204 reuses `applyInbound` mapping helpers for ClickUp shapes.
* Requires: PAP-100 tables and `mapping.ts`, PAP-97 receiver and event bus, PAP-60 principal kinds, PAP-43 jobs for the backfill worker.

**Definition of done**

* Backfill of PAP completes; counts of issues, comments, labels and relations equal Linear's (printed).
* Replaying 100 recorded webhooks upserts idempotently (second replay changes nothing).
* Cross-tenant RLS still holds on `pm_*` after sync writes.
* Changelog; Linear comment with counts.

**Test plan**

* Unit: mapping of every Linear field in the snapshot fixture; placeholder principal creation; archive mirroring.
* Integration: `nock` fixtures for the paginated backfill including a mid-run `RATELIMITED`; webhook replay idempotency.
* e2e: staging backfill.
* No UI.

**Demo**

Run `pnpm pm-sync backfill`, watch the progress log, then `pnpm api call pm.issues.list --limit 5` and see live PAP issues with states and labels. Two minutes.

**Edge cases**

* Rate limit mid-backfill: sleep 60 s, resume from cursor.
* Webhook for an entity not yet backfilled (parent project missing): fetch the parent on demand.
* Issue moved to another team: keep with `external_team` in `extra`, archive locally.
* Duplicate deliveries: `webhookId` dedupe from PAP-97.
* Strays PAP-6..PAP-12: mirrored as `Duplicate` state, nothing special.

**Dependencies**

Blocked by PAP-100, PAP-97 (through the parent). Blocks both sibling children.

**Agent**

Built by Nova (lead); reviewed by Forge (Schema Wright).

**Size**

M
