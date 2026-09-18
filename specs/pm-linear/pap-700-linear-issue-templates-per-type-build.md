---
identifier: "PAP-700"
title: "Linear issue templates per Type (Build, Spec, Research, Review, Infra, Docs), a child template, a Needs Justin card template and a project template, all generated from `docs/pm/templates/`"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Infra"
priority: 3
surfaces: ["Staff"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91", "PAP-93"]
blocks: []
key: "r4/pm-linear/issue-templates-per-type-and-card"
url: "https://linear.app/paperos/issue/PAP-700/linear-issue-templates-per-type-build-spec-research-review-infra-docs"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:24.243Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-700: Linear issue templates per Type (Build, Spec, Research, Review, Infra, Docs), a child template, a Needs Justin card template and a project template, all generated from `docs/pm/templates/`

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Infra S

**Goal**

One template (`PaperOS Spec`) serves every issue type, so a Research spike, a Needs Justin card and a Build issue all start from the same eleven headings and humans skip half of them. Type-specific templates with pre-filled labels, the right Model and Effort defaults and the exact section prompts the validator checks make hand-created issues pass PAP-93 on the first try.

**Scope**

* In: `docs/pm/templates/{build,spec,research,review,infra,docs,child,needs-justin-card,project}.md` with frontmatter (`labels`, `state`, `estimate`, `modelDefault`, `effortDefault`), `templateCreate`/`templateUpdate` in `configure-workspace.ts` keyed by name prefix `PaperOS:`, the project template with the three-milestone skeleton and `Contract` section headings, `pnpm linear:configure --templates`, docs section "Templates".
* Out: the validator rules (PAP-93), the `PaperOS Spec` template's deletion (kept, marked legacy), PM-module templates (v0.2).

**Spec**

* Each template body carries the eleven sections with one-line prompts under each (for Research: time box and decision owner in Goal; for Review: the artefact under review and the rubric; for Infra: runbook and rollback under Spec), the `**Model / Effort:**` first line prefilled with the Type default from the cost rule (Spec P0 Opus/high, Build Sonnet/medium, Research S Sonnet/medium, Review Opus/high, Docs Sonnet/low) and `**Size**`.
* Template `templateData` sets labels: `Type/*`, a placeholder surface, `Model: *` and `Effort: *` per default; state `Triage` for humans; estimate from the default Size.
* Needs Justin card template mirrors PAP-94: Decision needed, Recommendation, Options (max 3), Deadline, Default if no answer, Context links; labels `Staff`; state `Needs Justin` reserved to Atlas.
* Project template: description skeleton with Goal, Contract (Provides, Requires, Milestone exit criteria), Module contract placeholders and three milestones named by phase.
* Generation is create-or-update by name; the legacy `PaperOS Spec` template body is updated to point at the typed ones; drift reported by `--check`.

**Interface contract**

* Provides: templates named `PaperOS: <Type>`, `PaperOS: Child`, `PaperOS: Needs Justin card`, `PaperOS: Project`; ids in `linear-workspace.json.templates`; the frontmatter schema in `docs/pm/templates/README.md`.
* Consumes: PAP-91 configure script, PAP-93 section names and codes, PAP-94 card format, the cost rule defaults in `docs/cost-and-duration-estimate.md` section 4b.

**Definition of done**

* Nine templates exist; an issue created from `PaperOS: Build` and filled minimally passes `pnpm contract:audit` with warnings only (recording).
* `--check` clean after `--apply`; screenshots of the template picker at 1280 px and on a phone; docs; changelog.

**Test plan**

* Unit: frontmatter to `templateData` mapping, section prompt presence per Type, idempotent update.
* E2E: live create and update on the workspace.

**Demo**

Create a new issue in Linear, pick `PaperOS: Research`, see the time-box prompt and the prefilled labels; save and run `pnpm contract:audit PAP-<n>`. Under one minute.

**Edge cases**

* Linear changes template fields: the script logs the unsupported field and continues.
* Justin edits a template in the UI: `--check` reports drift with a `manual` marker; `--apply --force-templates` is the only way to overwrite.
* A Type default model changes in the cost doc: templates regenerate from the doc's table (single source).

**Dependencies**

Hard: PAP-91, PAP-93. Soft: PAP-94, docs/cost-and-duration-estimate.md.

**Agent**

Builder: Quill (Changelog Scribe). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
