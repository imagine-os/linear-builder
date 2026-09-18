---
identifier: "PAP-796"
title: "Contact and company merge and duplicate detection: fuzzy duplicate candidates, side-by-side merge with field pick, external ref and consent re-pointing, undo window"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "CRM core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-189", "PAP-790"]
blocks: []
key: "r4/growth/contact-company-merge-and-dedup"
url: "https://linear.app/paperos/issue/PAP-796/contact-and-company-merge-and-duplicate-detection-fuzzy-duplicate"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:45.065Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-796: Contact and company merge and duplicate detection: fuzzy duplicate candidates, side-by-side merge with field pick, external ref and consent re-pointing, undo window

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Five specs mention merging (PAP-187 edge cases, consent centre, PAP-197 'merge suggested manually', PAP-413, PAP-425) and none implements it. Every import and every form doubles contacts; a merge that keeps history, consent and external references intact is the difference between a CRM and a list.

**Scope**

In: `crm.duplicates.scan` job producing `crm_duplicate_candidate (kind, a_id, b_id, score, reasons[])` from normalised email, phone E.164, name plus company (`pg_trgm`), company domain; review page `_app/crm/duplicates`; `crm.merge({ kind, winnerId, loserIds[], fieldPicks })` in one transaction re-pointing activities, deals, segment members, tags, `crm_external_ref`, consent records (most restrictive wins), support conversations and `fin_party` links through contract ports, writing `merged_into` on the loser and an audit row; 30-day undo via a stored merge plan; merge hook for importers (`onDuplicate: merge|skip|create`).

Out: automatic merges without review (only exact-email matches from imports may auto-merge, per tenant setting), cross-tenant dedupe.

**Spec**

* Scoring is explainable: each reason carries a weight; thresholds per kind editable in settings; candidates expire when either record changes materially.
* Merge is idempotent and resumable; a failure mid-transaction rolls back entirely; undo replays the inverse plan and refuses when the winner changed in a conflicting field.
* External references from many systems on one record are allowed (PAP-201 `merged_into` on the mapping side).

**Interface contract**

Provides: `crm.duplicates.*`, `crm.merge`, `crm.unmerge`, review page, `MergeDialog`, importer hook `onDuplicate`. Consumes: CRM schema, views (PAP-189), consent records (PAP-791), external refs (PAP-201, soft), support (PAP-410, soft), audit (PAP-38), `fin_party` link (PAP-175, soft).

**Definition of done**

* Fixture set of 200 contacts with 40 planted duplicates: recall over 90 percent at the default threshold; merge and undo property test returns the graph to its prior hash.
* Playwright review and merge; screenshots at 375, 1024, 1920 light and dark; `docs/growth/merge.md`; CHANGELOG.

**Test plan**

* Unit: normalisers, scoring weights, re-pointing per relation, consent precedence, undo conflict detection.
* E2E: scan the seeded tenant, merge a pair picking fields from both, verify activities and deals moved, undo and verify restoration.

**Demo**

Reviewer opens Duplicates, merges two obvious contacts choosing the newer phone, opens the winner's timeline showing both histories, then undoes. Under two minutes.

**Edge cases**

* Loser has a portal login (`user_id`): both users kept, winner gets the primary; the other can still log in and sees the merged record.
* Two companies with the same domain but different legal entities: 'not a duplicate' marks the pair and suppresses future candidates.

**Dependencies**

Hard: PAP-790, PAP-189. Soft: PAP-791, PAP-201, PAP-410, PAP-38, PAP-175.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Edge Case Hunter, Security Auditor for PII).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/consent-compliance-centre` = PAP-791, `r4/growth/crm-schema-routers-page-specs` = PAP-790.
