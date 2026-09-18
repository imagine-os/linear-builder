---
identifier: "PAP-708"
title: "Linear sync: mirror initiatives, project updates and health, cycles, estimates, due dates, triage state and attachments both ways with the Linear-wins rule"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: "PAP-101"
children: []
blockedBy: ["PAP-97", "PAP-100", "PAP-372", "PAP-373", "PAP-707"]
blocks: []
key: "r4/pm-linear/pm-sync-initiatives-cycles-attachments"
url: "https://linear.app/paperos/issue/PAP-708/linear-sync-mirror-initiatives-project-updates-and-health-cycles"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:29.684Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-708: Linear sync: mirror initiatives, project updates and health, cycles, estimates, due dates, triage state and attachments both ways with the Linear-wins rule

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). The three PAP-101 children sync the entity set PAP-100 defined. Once round 4 enables estimates, cycles, due dates, initiatives, project updates, triage and attachments in Linear and the PM model gains their tables, the sync must carry them or the mirror lies. This child extends backfill, inbound upsert and the outbox for the new fields and entities.

**Scope**

* In: `mapping.ts` entries for `estimate`, `dueDate`, `cycle`, `triage` state type, `Attachment`, `Initiative`, `InitiativeToProject`, `ProjectUpdate` and project `health|lead|priority|targetDate`; backfill queries (PAP-372) for initiatives, project updates and attachments; inbound handlers for `Initiative`, `ProjectUpdate`, `Attachment`, `Cycle` webhooks; outbox ops `initiative`, `projectUpdate`, `attachment` (PAP-373); conflict rule coverage (PAP-374) for the new fields; runbook update.
* Out: the schema (sibling model issue), UI, PaperOS-originated initiatives before cutover (outbox for initiatives is create-only).

**Spec**

* Field mapping follows Linear's GraphQL types; `estimate` integer, `dueDate` date, `cycle` by external ref, attachments by `url` with `metadata` jsonb; project updates map `health` and `body`, author to principal.
* Backfill order: cycles and initiatives before projects and issues so references resolve; attachments last; cursor per entity type as in PAP-372.
* Outbox: estimate, due date and cycle changes on issues flow out as `issueUpdate`; project updates created in PaperOS flow out as `projectUpdateCreate`; attachments as `attachmentCreate` with dedupe by URL (same rule as the attachments issue).
* Conflicts: Linear wins per field; project `health` set by Atlas's update (round-4 issue) is authoritative until cutover.

**Interface contract**

* Provides: mapping additions, handlers, outbox ops, conflict coverage for the new fields.
* Consumes: PAP-372 backfill and inbound, PAP-373 outbox, PAP-374 conflict rule, the model sibling, PAP-97 webhook types.

**Definition of done**

* Backfill of PAP includes initiatives, project updates and attachments with matching counts; round trip for estimate, due date and cycle changes in both directions (staging).
* Conflict test on `estimate`; runbook update; changelog; Linear comment with counts.

**Test plan**

* Unit: mapping for every new field on snapshot fixtures; ordering of backfill; dedupe of attachments.
* E2E: staging round trip per new entity.

**Demo**

Change an estimate on `/pm/list`, see it in Linear within ten seconds; post a project update in Linear and see it on the project page in PaperOS. Ninety seconds.

**Edge cases**

* Initiative webhook types not delivered by Linear (some entities lack webhooks): nightly backfill covers them; lag shown on the status page.
* Attachment URL expired in Linear: stored as is; the evidence bundle re-signs MinIO URLs on read.
* Cycle deleted in Linear: local cycle archived, issues keep the reference for history.

**Dependencies**

Hard: PAP-372, PAP-373, PAP-707. Soft: PAP-374, PAP-97, PAP-699.

**Agent**

Builder: Nova (Views Engineer) with Forge (Schema Wright). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/pm-linear/issue-attachments-and-evidence-bundle` = PAP-699, `r4/pm-linear/pm-model-initiatives-updates-cycles-rollups` = PAP-707.
