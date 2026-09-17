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
children: []
blockedBy: ["PAP-100", "PAP-97"]
blocks: []
key: "pm-linear/linear-sync"
url: "https://linear.app/paperos/issue/PAP-101/build-bidirectional-linear-sync-graphql-webhooks-with-conflict-rule"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-101: Build bidirectional Linear sync (GraphQL + webhooks) with conflict rule: Linear wins until cutover

**Goal**

Keep the PaperOS PM tables and Linear team PAP in step both ways so the same issues are visible in either tool, with one rule that removes all ambiguity until cutover: when both sides changed, Linear wins. Edits made in PaperOS boards (`pm-linear/board-views`) reach Linear within seconds, and everything the orchestrator does in Linear appears in PaperOS.

**Scope**

In:
- Sync service `packages/pm-sync` in paperos-template (runs inside the API process or as a worker): initial backfill, incremental inbound via Linear webhooks (reusing the receiver from `pm-linear/webhooks`), and outbound on PaperOS mutations via an outbox table.
- Entities: teams, workflow states, projects, milestones, cycles, issues, relations, labels, comments, attachments; users mapped to principals by email, agents mapped by bot account.
- Inbound: webhook `data` upserted into `pm_*` tables using `pm_external_ref`; `updatedFrom` used to detect which fields changed; deletions and archives mirrored as `archived_at`.
- Outbound: `pm_outbox(id, entity_type, entity_id, op, payload, attempts, next_attempt_at, last_error)` written in the same transaction as the PaperOS mutation; a worker drains it with `@linear/sdk` mutations (`issueCreate`, `issueUpdate`, `commentCreate`, `issueLabelCreate`...), stores the returned Linear id in `pm_external_ref`.
- Conflict rule: compare `external_updated_at` with the PaperOS `updated_at` of the last applied inbound change; if Linear changed after our local edit and the field sets intersect, discard the local field change, apply Linear's, and record a `pm_sync_conflict` row plus an in-app notice (hook for `collab/notifications`).
- Loop prevention: mutations performed by the sync's own Linear API key are recognised by `actor.id` in webhooks and skipped; PaperOS writes originating from inbound sync set `source: "linear"` and do not enqueue outbox rows.
- Admin page spec `specs/pm/sync-status.spec.yaml` and oRPC `pm.sync.status/backfill/retry` showing lag, outbox depth, conflicts.

Out: cutover tooling (flipping the winner), ClickUp import (`migration/clickup-linear`), field types Linear lacks.

**Spec**

- Backfill uses paginated `issues(first: 100, after)` with `includeArchived: true`, ordered by `updatedAt`, resumable via a `pm_sync_cursor` table; full PAP backfill (a few hundred issues) must finish under 5 minutes.
- Field mapping table lives in `packages/pm-sync/src/mapping.ts`, shared with `pm-linear/pm-data-model` docs; unknown Linear fields are stored in `pm_issue.extra` jsonb so nothing is lost.
- Rate limiting: Linear's complexity-based limits; the worker respects `X-RateLimit-Requests-Remaining` headers, batches label updates and pauses at 10 percent remaining.
- Retry policy: exponential backoff 1 s to 10 min, 8 attempts, then `dead` state visible on the status page.
- Every sync write carries `created_by` = the sync principal from `identity/agent-principals`.

**Definition of done**

- Round-trip tests with a Linear sandbox team (or recorded fixtures via `nock`): create in PaperOS appears in Linear with correct state, labels, assignee; edit in Linear appears in PaperOS; simultaneous edit resolves with Linear winning and a conflict row.
- Backfill of PAP completes and counts match (`issues`, `comments`, `labels`) printed in the comment.
- Loop test: 1000 synthetic edits produce no echo writes (outbox count equals user edits).
- Sync status page screenshot at 375, 768 and 1280 px; Playwright coverage in `quality/playwright-matrix`.
- Runbook `docs/pm/linear-sync.md` (backfill, retry, dead-letter, key rotation); changelog entry; Linear comment with test results.

**Edge cases**

- Webhook arrives before the outbox write that caused it is committed (our own create): match by an `idempotencyKey` we embed in the Linear description footer or `attachment` metadata, not just by id.
- Linear user with no PaperOS principal: create a placeholder external principal rather than dropping the assignee.
- Label group missing in PaperOS: create it on the fly, flagged `source: linear`.
- Issue deleted permanently in Linear (not archived): keep the PaperOS row, set `archived_at`, add `deleted_externally` flag.
- Description contains Linear-specific markup (mentions `@user`, issue embeds): store raw; render with a fallback formatter.
- Webhook outage for hours: backfill by `updatedAt > last cursor` on reconnect closes the gap.
- Cycle changes on a team where PaperOS has cycles disabled: store but do not surface.

**Dependencies**

- `pm-linear/pm-data-model` (tables, procedures).
- `pm-linear/webhooks` (verified receiver and event bus).
- Uses `identity/agent-principals` for the sync principal.

**Agent**

Built by Nova (lead) with Forge (Schema Wright) for the outbox migration; reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Atlas for Linear behaviour.

**Size**

L: bidirectional sync with conflicts, backfill and loop prevention against a live third-party API.
