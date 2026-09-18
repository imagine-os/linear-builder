---
identifier: "PAP-821"
title: "Import duplicate detection and merge preview: fuzzy matching of incoming rows against existing records, per-collection dedupe strategies and a review step before commit"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-201", "PAP-348", "PAP-349"]
blocks: []
key: "r4/migration/import-duplicate-detection-and-merge-preview"
url: "https://linear.app/paperos/issue/PAP-821/import-duplicate-detection-and-merge-preview-fuzzy-matching-of"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:50.450Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-821: Import duplicate detection and merge preview: fuzzy matching of incoming rows against existing records, per-collection dedupe strategies and a review step before commit

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

The framework dedupes on exact keys and mappings. Real migrations arrive with 'Acme Inc' and 'ACME, Inc.', two spellings of an email and a phone with and without a country code. A fuzzy pass in dry run, with a review step and per-collection strategies, is what prevents the first import from doubling the CRM.

**Scope**

In: dry-run pass `detectDuplicates` scoring incoming rows against existing records by normalised email, phone E.164, company domain, name trigram (`pg_trgm`), configurable per collection (`strategy: skip|update|create|review`, threshold); `import_duplicate (run_id, item_id, target_id, score, reasons[])`; wizard step `DuplicateReview` (PAP-349) listing candidates with side-by-side values and bulk decisions; decisions applied at commit through PAP-201 mappings; growth merge hook (PAP-796 `onDuplicate`) when the target is a CRM table; report section in `RunReport`.

Out: post-import dedupe across the whole CRM (growth issue), cross-tenant matching.

**Spec**

* Normalisers are shared with growth through `@paperos/contract-growth` where they exist; the framework ships its own for generic tables.
* Scoring is explainable and deterministic; the same input yields the same candidates; thresholds default per field kind.
* Review decisions are stored on the mapping so a re-run applies them without asking again.

**Interface contract**

Provides: `detectDuplicates` pass, `import_duplicate`, `DuplicateReview` step, strategies in `MappingDefinition`, report section. Consumes: dry run (PAP-348), wizard (PAP-349), mappings (PAP-201), growth merge hook (soft), record API (PAP-164).

**Definition of done**

* Fixture of 1,000 incoming rows with 120 planted near-duplicates: recall over 90 percent, false positives under 2 percent at defaults; review decisions survive a rerun; Playwright review step; screenshots at 375, 1024, 1920 light and dark.
* `docs/migration/dedupe.md`; CHANGELOG.

**Test plan**

* Unit: each normaliser, scoring, threshold defaults, decision persistence.
* E2E: import the messy contacts CSV over a seeded CRM, review candidates, choose update for most and create for two, commit and verify counts.

**Demo**

Reviewer imports `contacts-messy.csv`, sees 14 likely duplicates with reasons, accepts the suggestions and commits without creating a single duplicate. Under two minutes.

**Edge cases**

* Two incoming rows match each other and one existing: grouped as one candidate set.
* Target record archived: match offered with 'unarchive' option per PAP-201 rules.
* Very large run: detection sampled to 10k in dry run with a notice unless `--full`.

**Dependencies**

Hard: PAP-348, PAP-349, PAP-201. Soft: PAP-164, PAP-796.

**Agent**

Builder: Scout (Import Mapper). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/contact-company-merge-and-dedup` = PAP-796.
