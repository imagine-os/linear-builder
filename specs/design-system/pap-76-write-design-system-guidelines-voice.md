---
identifier: "PAP-76"
title: "Write design system guidelines (voice, density, spacing, when to use what) into the docs system"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Docs"
priority: 2
surfaces: ["Developer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-69", "PAP-128"]
blocks: []
key: "design-system/guidelines-docs"
url: "https://linear.app/paperos/issue/PAP-76/write-design-system-guidelines-voice-density-spacing-when-to-use-what"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:13.004Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-76: Write design system guidelines (voice, density, spacing, when to use what) into the docs system

**Goal**

Write the design-system guidelines agents consult when a spec leaves room for judgement: voice and tone, density, spacing rhythm, hierarchy, component choice, forms, feedback and states, responsive behaviour. Published in the docs engine, linked from every story, and partly machine-readable so review agents can check them.

**Scope**

* In: twelve MDX pages under `docs/design/guidelines/`, Do and Don't examples rendered from live components, `rules.json` (60 or more rules, 20 checkable by lint or vision), a glossary, 30 before/after copy rewrites, an agent checklist.
* Out: brand marketing guidelines, illustration tutorials, component API docs (autodocs), motion and accessibility content beyond links (PAP-72, PAP-73).

**Spec**

* Pages: `principles`, `voice-and-tone` (sentence case, plain verbs, error formula: what happened, why, what to do), `layout-and-spacing` (4 px grid, 8/16/24 rhythm, 1200 max content width, 65ch measure), `density`, `typography`, `color-usage` (semantic tokens only, one accent per view), `components-when-to-use` (decision tables: Dialog vs Sheet vs Popover, Select vs Combobox vs Radio, Toast vs inline alert vs banner), `forms` (labels above, validation on blur then submit, destructive confirmations), `feedback-and-states` (loading, empty, error, offline, permission, success mapped to PAP-71 and PAP-234 components), `responsive`, `agent-checklist` (10 questions before a PR), `glossary`.
* Frontmatter `title, summary, owner: Iris, lastReviewed, appliesTo: [web, desktop, mobile]`; rule IDs `DS-<AREA>-<nn>` cited by every Do/Don't; each page under 1 200 words with a summary box; "Related components" and "Related specs" resolved from `registry.json`.
* `rules.json` schema `{ id, area, rule, rationale, severity: 'blocker' | 'major' | 'minor', checkable: 'lint' | 'vision' | 'agent' | 'manual', appliesTo?, when?, locale?, examples: { do, dont } }`; severities follow PAP-79.
* Rendering: PAP-128 docs engine at `/docs/design/...`; Storybook MDX under `Guidelines/` until it merges; embeds via `@storybook/blocks`.

**Interface contract**

* Provides: `docs/design/guidelines/rules.json` (validated by a Zod schema exported from `packages/contracts` as kind `design-rules`), rule ID namespace `DS-*`, the glossary terms file `glossary.json` for the spec editor, page slugs.
* Requires: PAP-69 embeds (hard), PAP-128 (hard for final home; Storybook fallback allowed), PAP-74 `registry.json` (soft), PAP-79 severity names.
* Consumers: PAP-244 spec-conformance reviewer (loads `rules.json`), PAP-84 vision inspector (`checkable: vision` items), PAP-118 spec-authoring skill, PAP-105 page-from-spec skill, PAP-124 editor hints.

**Definition of done**

* Twelve pages merged and rendering with working component embeds (docs engine or Storybook fallback).
* `rules.json` validates and contains at least 60 rules, 20 marked `vision` or `lint`; every rule cited by at least one Do/Don't.
* PAP-244 prompt references `rules.json` (PR or comment agreeing the hook); PAP-84 lists the vision rules it checks.
* Screenshots of two guideline pages at 375 and 1280 light and dark.
* Reviewed by Quill (prose) and Iris (correctness); changelog entry; Linear comment with the docs link.

**Test plan**

* Unit: `rules.json` schema validation, unique IDs, every cited ID exists, `appliesTo` values valid.
* Docs: link checker over the twelve pages; every "Related components" entry resolves in `registry.json`.
* Dry run: Sentinel runs the spec-conformance reviewer over one seeded PR that violates `DS-FORM-03` and confirms the finding cites the rule.
* Visual: two pages at two widths × two themes.

**Demo**

Open `/docs/design/components-when-to-use`, read the Dialog vs Sheet table with live embeds, then open `rules.json` and filter for `checkable: vision`; finally open a seeded PR review citing `DS-FORM-03`. Under two minutes.

**Edge cases**

* Guideline contradicts a story: the story is wrong; open a fix task rather than soften the rule.
* Touch-only or desktop-only rules: `appliesTo` and `when` so reviewers skip irrelevant ones.
* Locale-specific copy rules: `locale: en`.
* Removed rule: deprecate, never renumber.

**Dependencies**

PAP-69, PAP-128 (hard; fallback allowed). Soft: PAP-74, PAP-79.

**Agent**

Iris writes; Quill (Changelog Scribe and Page Spec Writer) edits. Reviewed by Sentinel (reviewer dry run) and Atlas.

**Size**

M.
