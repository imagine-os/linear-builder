---
identifier: "PAP-419"
title: "Notion hierarchy, page tree picker, docs placement and conversion report"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: "PAP-203"
children: []
blockedBy: ["PAP-128", "PAP-418"]
blocks: []
key: "child/PAP-203/2"
url: "https://linear.app/paperos/issue/PAP-419/notion-hierarchy-page-tree-picker-docs-placement-and-conversion-report"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:55.136Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: null
cycle: null
---

# PAP-419: Notion hierarchy, page tree picker, docs placement and conversion report

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Let the user choose what to bring and see what happened: a page tree picker with counts, a per-page target choice (docs or table), hierarchy preserved under `docs/imported/notion/`, database page bodies attached to records, and a conversion report that names every unsupported block and unmatched person.

**Scope**

In: wizard steps `NotionTreePicker` (checkboxes, counts, "no access" rows), `TargetChoice`, `ConversionReportView`; placement writer producing `_meta.yaml` order and frontmatter `source: notion`, `sourceUrl`, `imported`; bodies over 2,000 words become linked docs, otherwise a `Content` rich text field; docs written through the PAP-128 import path (branch and PR when the repo is the store).

Out: converter internals (child 2).

**Spec**

* Picker paginates at 200 nodes and estimates duration from the PAP-198 throughput table.
* Report is stored with the run (PAP-199 child 2) and rendered by `RunReport` with a Notion-specific section.

**Interface contract**

Provides: wizard steps registered via PAP-199 child 3, `placeDocs(pages): DocPlan`, frontmatter fields above. Consumes: children 1 and 2, PAP-128 file writer, `RunReport`. Output docs are indexed by PAP-137 search like any other doc.

**Definition of done**

* Test workspace (25 pages, 4 levels, inline database) imports with the tree order preserved in the docs sidebar.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for picker and imported doc; axe clean.

**Test plan**

* Vitest: tree ordering, 2,000-word threshold, frontmatter, "no access" handling.
* Playwright: picker, target choice, report, browse an imported doc and a table view; visual baselines at seven widths, both themes.
* axe on picker and report.

**Demo**

Reviewer opens the Notion wizard, ticks a top-level page and a database, commits, then browses the imported docs tree and the table. Under two minutes.

**Edge cases**

* 50k pages: picker shows top levels first and loads children on expand.
* Page moved in Notion between dry run and commit: placed by commit-time parent, noted.
* Docs store is the repo and the branch already exists: suffixed branch name.

**Dependencies**

Children 1 and 2 (hard), PAP-128 (hard), PAP-199 child 3.

**Agent**

Built by Scout (Import Mapper) with Quill. Reviewed by Sentinel (Visual Inspector).

**Size**

S
