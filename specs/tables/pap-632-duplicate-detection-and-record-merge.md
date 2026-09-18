---
identifier: "PAP-632"
title: "Duplicate detection and record merge: find duplicates by fields with fuzzy matching, review pairs and merge with field-level choice"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-333", "PAP-334"]
blocks: []
key: "r4/tables/duplicate-detection-and-merge"
url: "https://linear.app/paperos/issue/PAP-632/duplicate-detection-and-record-merge-find-duplicates-by-fields-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:20.428Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-632: Duplicate detection and record merge: find duplicates by fields with fuzzy matching, review pairs and merge with field-level choice

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (NJ-19 scope freeze; reinstate via NJ-14). Airtable's Dedupe extension and every CRM's merge flow prevent the second "Acme Corp". Add duplicate detection over chosen fields with fuzzy matching and a merge dialog that keeps one record, re-points relations and trashes the rest.

**Scope**

In: `packages/views/src/dedupe/{DedupeWizard,MergeDialog,match}.ts`; procedures `records.findDuplicates({ datasetRef, fields, strategy })` (job above 5k rows), `records.merge({ keepId, mergeIds, fieldChoices })`; `pg_trgm` similarity for text fields.

Out: automatic merging without review, cross-dataset dedupe, import-time dedupe (PAP-199 has its own preview).

**Spec**

* Strategies per field: `exact`, `caseInsensitive`, `normalized` (trim, fold diacritics, strip punctuation), `fuzzy` (`similarity() > 0.8` via `pg_trgm`), `emailDomain`; groups computed with a `GROUP BY` on the normalised expression or a self-join for fuzzy, capped at 10k rows inline, otherwise a PAP-43 job.
* Wizard: pick fields and strategies, run, review groups as side-by-side records with differing fields highlighted, choose the survivor and per-field values, merge or skip; keyboard-operable.
* `records.merge` runs in one transaction: writes chosen values to `keepId`, repoints every inbound relation and comment anchor (PAP-131 `entity:` grammar) to `keepId`, trashes `mergeIds` (PAP-334 soft delete with reason `merge:<keepId>`), writes one audit row per merged record; undo restores from trash and reverses the repoint within 30 days.
* History (PAP-333) shows a "Merged from" entry with links; CRM (PAP-189) exposes the wizard on contacts and companies.

**Interface contract**

Provides: `records.findDuplicates`, `records.merge`, `<DedupeWizard datasetRef />`, `<MergeDialog />`, `normalizeForMatch(value, strategy)`. Consumes: trash and restore (PAP-334), history (PAP-333), relations (PAP-340), comments repoint (PAP-131), jobs (PAP-43), `pg_trgm` extension (PAP-32 migration). Consumed by PAP-189.

**Definition of done**

* Wizard and merge green in Vitest, integration and Playwright; screenshots at 375, 1024, 1920; axe clean; `docs/views/dedupe.md`; CHANGELOG.

**Test plan**

* Unit: normalisation strategies; group construction; field-choice merge builder; undo plan generation.
* Integration: merge repoints 50 inbound relations and 5 comment threads in one transaction; restore reverses; fuzzy job over 20k rows completes under 60 s.
* E2E: run the wizard on the demo clients, merge two Acme records choosing the newer phone, open the survivor's history, undo.

**Demo**

Reviewer finds duplicate clients by fuzzy name, merges a pair and sees relations follow. Under two minutes.

**Edge cases**

* Survivor and merged record both linked from the same relation field with `limitOne`: keep survivor, report.
* Merge across a posted ledger reference (PAP-179): blocked with explanation.
* Group larger than 50: paginated review.

**Dependencies**

PAP-334 (hard), PAP-333 (hard). Soft: PAP-131, PAP-189. PAP-796 ships the CRM-specific flow first (consent and external refs); this issue generalises `records.merge` to any dataset and reuses its scoring and `MergeDialog`. Deferred; nothing waits on it.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/contact-company-merge-and-dedup` = PAP-796.
