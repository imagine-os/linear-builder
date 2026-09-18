---
identifier: "PAP-751"
title: "Spec versioning tooling: version registry, codemod helpers, `paperos-spec migrate --dry-run`, `x-deprecated` metadata with `SPEC_DEPRECATED` and the weekly 300-fixture rehearsal"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-748"]
blocks: []
key: "r4/spec-builder/spec-versioning-tooling"
url: "https://linear.app/paperos/issue/PAP-751/spec-versioning-tooling-version-registry-codemod-helpers-paperos-spec"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:36.750Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-751: Spec versioning tooling: version registry, codemod helpers, `paperos-spec migrate --dry-run`, `x-deprecated` metadata with `SPEC_DEPRECATED` and the weekly 300-fixture rehearsal

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (Execution Schedule stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

PAP-114 ships only the `migrate/` skeleton and names this follow-up explicitly (FIX-5). Once the issue cap lifted, the tooling gets its home: a version registry, codemod helpers, a dry-run migrator, deprecation metadata and a rehearsal that migrates the synthetic corpus every week so a v2 schema is never the first time the codemods run.

**Scope**

In: `packages/spec/src/migrate/` filled in: `SPEC_VERSIONS` registry with `codemodsFrom`, helpers `renameKey|moveKey|mapEnum|wrapValue|splitSection`, `paperos-spec migrate [--to <v>] [--dry-run] [--write]` printing a unified diff per file and preserving comments through the `yaml` Document API; `x-deprecated: { since, replaceWith, removeAt }` on schema fields with rule `SPEC_DEPRECATED` (warn until `removeAt`, error after); weekly workflow `spec-migrate-rehearsal.yml` migrating `fixtures/corpus/large` from the oldest supported version and asserting zero diagnostics; `docs/spec/versioning.md` completed. Out: data migrations (PAP-443), template upgrades (PAP-430 consumes the CLI).

**Spec**

* Codemods are pure functions over `YAML.Document` returning `Change[]` with paths; every codemod has a fixture pair; a codemod that loses a comment fails its test.
* `migrate` refuses to write when the result fails validation; `--dry-run` exit codes 0 no-op, 1 changes, 3 error.
* Deprecations: the JSON Schema carries `deprecated: true` and `x-replaceWith` so editors (PAP-376) strike the key through; `SPEC_DEPRECATED` hints the codemod name.
* Rehearsal seeds a copy of the corpus with the previous version's shape (generator flag `--version <v>` in PAP-748), migrates, validates, and diffs against the current corpus.
* `paperos upgrade` (PAP-430) calls `migrate --write` for generated apps and lists the changes in its PR body.

**Interface contract**

Provides: version registry, codemod helpers and `Codemod` implementations, CLI, `x-deprecated` schema support, rule `SPEC_DEPRECATED`, rehearsal workflow. Consumes: `migrate/` skeleton and `SpecIssue` (PAP-114), CLI host (PAP-115), corpus generator, `yaml` Document patching from PAP-377, ADR process (PAP-130). Consumed by: PAP-430 template upgrade, PAP-376 editor (deprecation strike-through), PAP-740 codemods (moved here), PAP-306 re-audit.

**Definition of done**

* Helpers and CLI merged with fixtures; a synthetic v1 to v2 rename migrates the large corpus with comments intact and zero diagnostics; rehearsal workflow green once.
* `docs/spec/versioning.md`; CHANGELOG entry; Linear comment with the dry-run diff sample.

**Test plan**

* Unit: each helper on fixtures including comments and anchors; exit codes; deprecation date logic with a fake clock.
* Integration: CLI over the corpus; JSON Schema `deprecated` flags present.
* E2E: none.

**Demo**

Mark `layout.slots` deprecated in a scratch branch with `replaceWith: layout.regions`, run `paperos-spec migrate --dry-run` and read the diff and the `SPEC_DEPRECATED` hint. Under one minute.

**Edge cases**

* Two codemods touch the same path: ordered by version then declaration; conflict fails the registry test.
* Spec with YAML anchors: aliases rewritten once at the anchor.
* Unsupported future version: `SPEC_UNSUPPORTED_VERSION` as PAP-114 defines.

**Dependencies**

Hard: PAP-114, PAP-748. Soft: PAP-115, PAP-377, PAP-430, PAP-130. Deferred: v0.2.

**Agent**

Builder: Quill (Page Spec Writer). Reviewer: Sentinel (Code Reviewer) with Atlas.

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/schema-v1-1-extensions` = PAP-740, `r4/spec-builder/spec-fixture-corpus` = PAP-748.
