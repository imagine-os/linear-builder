---
identifier: "PAP-743"
title: "Semantic spec diff: section-level changes, access matrix delta and breaking flags posted as a PR comment and consumed by the spec-conformance reviewer"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-116"]
blocks: []
key: "r4/spec-builder/spec-diff-pr-comment"
url: "https://linear.app/paperos/issue/PAP-743/semantic-spec-diff-section-level-changes-access-matrix-delta-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:18.937Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-26"
cycle: null
---

# PAP-743: Semantic spec diff: section-level changes, access matrix delta and breaking flags posted as a PR comment and consumed by the spec-conformance reviewer

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

OpenAPI has `oasdiff`; specs have `git diff` of YAML. Reviewers (PAP-81's spec-conformance agent) and Justin need to know what a PR changed in meaning: who lost access, which component was removed, which transition vanished, whether the change is breaking for generated code. PAP-123 diffs the graph; nothing diffs the pages.

**Scope**

In: `diffSpecs(before, after): SpecDiff` in `packages/spec/src/diff/`, CLI `paperos-spec diff <base>..<head> [--format md|json|github]`, Gate 1 step posting one sticky PR comment through PAP-78's action and attaching `spec-diff.json` as a PAP-239 artefact, `SpecDiff` Zod schema in the contract (PAP-467 patch), `docs/spec/diff.md`. Out: graph diff (PAP-123, linked), auto-approval decisions, editor UI (PAP-378 may render it later).

**Spec**

* Diff units: pages added, removed, renamed (id change with same route); per page: `meta.status` transitions, `access` matrix delta computed with PAP-116 `accessMatrix` (rows `audience x action: granted -> denied`), components added or removed by key, states added or removed, events added or removed with dangling targets, data queries and mutations changed, integrations added, edge cases added or removed.
* Breaking classification (feeds the reviewer): removed component key, removed action, audience losing `page.view`, route change, `status: built` to `deprecated`; `breaking: true` requires a `## Breaking` section in the PR body (PAP-49) or the reviewer posts a blocker.
* Markdown output is under 300 lines with collapsed `<details>` per page; JSON is stable and sorted; `--format github` produces annotations on the YAML lines that changed meaning.
* Runs on `specs/**` changes only; skipped otherwise; under 3 s for 300 specs using PAP-115's content-hash cache.
* Reviewer integration: PAP-244's spec-conformance prompt receives `spec-diff.json` as an input file; PAP-97 status comment links the sticky comment.

**Interface contract**

Provides: `diffSpecs`, `SpecDiff` schema and type, CLI, Gate 1 step `spec-diff`, artefact `spec-diff.json`, sticky comment format. Consumers: PAP-244 spec-conformance reviewer, PAP-97 status comment, PAP-89 digest (spec changes section), PAP-378 (later), PAP-306 weekly re-audit. Requires: PAP-114 parse (hard), PAP-116 `accessMatrix` (hard), PAP-78 sticky-comment action and job slot (soft; runs as a script until then), PAP-239 artefact schema (soft), PAP-49 PR body sections (soft).

**Definition of done**

* Seeded PR removing a component and an audience grant produces the comment with a `breaking` badge and the matrix delta; a docs-only PR skips the step.
* JSON schema snapshot; `docs/spec/diff.md`; comment on PAP-244 with the input file path; CHANGELOG entry.

**Test plan**

* Unit: every diff unit with fixtures; rename detection; breaking classification table; markdown length cap.
* Integration: CLI between two fixture trees; annotations map to correct lines.
* E2E: Gate 1 run on a seeded PR on both forges shows the sticky comment (screenshot).

**Demo**

Remove `markPaid` from the invoices example on a branch, run `paperos-spec diff main..HEAD --format md` and read the breaking badge and the access matrix row that flipped. Under one minute.

**Edge cases**

* Spec moved between folders: detected as rename by `meta.id`, not as remove plus add.
* Base branch lacks `specs/` (first PR of a new app): every page is `added`; no breaking.
* YAML unparseable on one side: diff reports `parseError` for that page and continues.

**Dependencies**

Hard: PAP-114, PAP-116. Soft: PAP-78, PAP-239, PAP-49, PAP-244, PAP-97, PAP-115.

**Agent**

Builder: Quill (Page Spec Writer) with Sentinel pairing on the reviewer input. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
