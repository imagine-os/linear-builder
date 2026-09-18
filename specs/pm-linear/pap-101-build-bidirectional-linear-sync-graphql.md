---
identifier: "PAP-101"
title: "Build bidirectional Linear sync (GraphQL + webhooks) with conflict rule: Linear wins until cutover"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: ["PAP-708", "PAP-372", "PAP-373", "PAP-374"]
blockedBy: ["PAP-97", "PAP-100"]
blocks: []
key: "pm-linear/linear-sync"
url: "https://linear.app/paperos/issue/PAP-101/build-bidirectional-linear-sync-graphql-webhooks-with-conflict-rule"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:51:46.586Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-101: Build bidirectional Linear sync (GraphQL + webhooks) with conflict rule: Linear wins until cutover

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Keep the PaperOS PM tables and Linear team PAP in step both ways with one rule that removes ambiguity until cutover: when both sides changed, Linear wins. Edits on PaperOS boards reach Linear within seconds and everything the orchestrator does in Linear appears in PaperOS. Umbrella for three children.

**Scope**

* Children (build in order):
  * PAP-372: backfill and inbound webhook upsert.
  * PAP-373: outbox, outbound worker and loop prevention.
  * PAP-374: conflict rule, sync status page and runbook.
* Out: cutover tooling (flipping the winner), ClickUp import (PAP-204), Linear fields PaperOS lacks (stored in `extra`).

**Spec**

* Package `packages/pm-sync` running as a worker in the API process; entities: teams, states, projects, milestones, cycles, issues, relations, labels, comments, attachments; users mapped to principals by email, agents by bot account.
* Field mapping in `@paperos/pm` `mapping.ts`; unknown fields to `pm_issue.extra`.
* Every sync write carries `created_by` = the sync principal (PAP-60) and `source: "linear"` so no outbox row is enqueued.
* Rate limiting respects `X-RateLimit-Requests-Remaining`, batches label updates with aliases and pauses at 10 percent remaining; retry 1 s to 10 min, eight attempts, then `dead`.

**Interface contract**

* Provides: `pm.sync.status()` returning `{ lagSeconds, outboxDepth, deadCount, conflicts24h, lastWebhookAt }`, `pm.sync.backfill()`, `pm.sync.retry(id)`; tables `pm_outbox`, `pm_sync_cursor`, `pm_sync_conflict`; event `pm.sync.conflict` for PAP-136.
* Consumers: PAP-102 (status banner and "changed in Linear" toast), PAP-204 (writes flow out through the same outbox), PAP-113 (assignee mirrors).
* Requires: PAP-100 tables and mapping, PAP-97 verified Linear receiver and event bus, PAP-60 sync principal, PAP-43 jobs queue for the worker.

**Definition of done**

* All three children Done.
* Umbrella round trip: create in PaperOS appears in Linear with state, labels and assignee; edit in Linear appears in PaperOS; simultaneous edit resolves with Linear winning and one conflict row.
* Backfill of PAP completes under five minutes with matching counts for issues, comments and labels printed in the comment.
* Loop test: 1000 synthetic edits produce no echo writes.
* Runbook `docs/pm/linear-sync.md`; changelog; Linear comment with results.

**Test plan**

* Integration suite `packages/pm-sync/test/roundtrip.test.ts` against `nock` fixtures recorded from PAP, covering the three children together.
* e2e on staging against the real PAP team using a `sync-test` label namespace, cleaned up afterwards.
* Visual: sync status page at 375, 768 and 1280 px (child 3).

**Demo**

Drag a card on the PaperOS board (PAP-102) or call `pm.issues.update`, open the Linear issue and watch the state change within ten seconds; edit the title in Linear and see it in PaperOS. Then run `pm.sync.status` and read lag zero. Two minutes.

**Edge cases**

* Webhook arrives before our own outbox write commits: match by the `idempotencyKey` embedded in the Linear description footer.
* Linear user without a principal: placeholder external principal, assignee kept.
* Permanent deletion in Linear: keep the row, set `archived_at` and `deleted_externally`.
* Webhook outage for hours: backfill by `updatedAt > cursor` on reconnect.
* Cycles disabled locally: store, do not surface.

**Dependencies**

Blocked by PAP-97, PAP-100. Soft: PAP-60, PAP-43.

**Agent**

Built by Nova (lead) with Forge (Schema Wright) for the outbox; reviewed by Sentinel.

**Size**

L (umbrella; children M, M, S)

**Module boundary**

This umbrella is the Project Management & Claude Pipeline half of the PaperOS Module System (`docs/module-system.md`). The `pm-linear` module implements `@paperos/contract-pm-linear` (issue contract and states, PM entities, `PmSourcePort`, queue port, webhook envelope). The orchestrator, triage, import and board views talk to Linear only through `PmSourcePort`, so the Linear adapter can be replaced by the native PM module without touching them; the module may import `@paperos/core`, `contract-data-layer`, `contract-tables`, `contract-collab` and its own packages. Its manifest declares `provides: [{ contract: '@paperos/contract-pm-linear', version: '0.1.0' }]`, `owner: { agent: 'Atlas', project: 'pm-linear' }` and `swapRisk: 'high'`. The contract package is published by PAP-465 (`module/pm-linear/contract`), proven by PAP-468 (`module/pm-linear/conformance`) and bound into `@paperos/kernel` by PAP-471 (`module/pm-linear/wire`); children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
