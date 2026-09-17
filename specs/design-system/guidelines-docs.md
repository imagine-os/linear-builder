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
blockedBy: ["PAP-128", "PAP-69"]
blocks: []
key: "design-system/guidelines-docs"
url: "https://linear.app/paperos/issue/PAP-76/write-design-system-guidelines-voice-density-spacing-when-to-use-what"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-76: Write design system guidelines (voice, density, spacing, when to use what) into the docs system

**Goal**

Write the design system guidelines that agents consult when a page spec leaves room for judgement: voice and tone, density, spacing rhythm, hierarchy, when to use which component, forms, feedback, empty and error states, and responsive behaviour. Published in the in-app docs engine and linked from every component story so generated pages feel like one product.

**Scope**

In:
- `docs/design/guidelines/` MDX pages: `principles.md`, `voice-and-tone.md` (sentence case, plain verbs, no exclamation marks, error message formula: what happened, why, what to do), `layout-and-spacing.md` (4px grid, 8/16/24 rhythm, max content width 1200, reading measure 65ch), `density.md` (compact, default, comfortable; when each), `typography.md`, `color-usage.md` (semantic only, never raw ramps, one accent per view), `components-when-to-use.md` (decision tables: Dialog vs Sheet vs Popover, Select vs Combobox vs Radio, Toast vs inline alert vs banner), `forms.md` (labels above, help text, validation timing on blur then on submit, destructive confirmations), `feedback-and-states.md` (loading, empty, error, offline, permission, success), `responsive.md` (what collapses at each breakpoint, touch adaptations), `motion.md` link, `accessibility.md` link, `agent-checklist.md` (10 questions an agent answers before opening a PR).
- Each rule has a Do and Don't example rendered from live components (Storybook story embeds via iframe or `@storybook/blocks`).
- Machine-readable subset `docs/design/guidelines/rules.json` (`id, rule, severity, checkable`) that `quality/review-agents` spec-conformance reviewer and `quality/screenshot-annotation` load as review criteria.
- Glossary of UI terms used across specs.

Out: brand marketing guidelines, illustration drawing tutorials, component API docs (autodocs).

**Spec**

- Docs live in the repo and render via `collab/docs-engine` at `/docs/design/...`; until it merges, render in Storybook MDX under `Guidelines/`.
- Frontmatter: `title, summary, owner: Iris, lastReviewed, appliesTo: [web, desktop, mobile]`.
- Rule IDs `DS-<area>-<nn>` (e.g. `DS-FORM-03: validate on blur, then on submit`); every Do/Don't cites its rule ID.
- `rules.json` schema: `{ id, area, rule, rationale, severity: 'blocker'|'major'|'minor', checkable: 'lint'|'vision'|'agent'|'manual', examples: { do, dont } }`; severities follow `quality/review-rubrics`.
- Length target 6,000-9,000 words across pages; each page under 1,200 words with a summary box on top.
- Each page ends with "Related components" and "Related specs" lists resolved from `registry.json` (`design-system/component-spec-mapping`).
- Voice examples table with 30 before/after copy rewrites.

**Definition of done**

- All 12 pages merged and rendering in the docs engine (or Storybook fallback) with working component embeds.
- `rules.json` validates against its schema in Vitest and contains at least 60 rules, 20 marked `vision` or `lint` checkable.
- `quality/review-agents` conformance prompt references `rules.json` (PR or comment agreeing the hook).
- Screenshots of two guideline pages at 375 and 1280 in light and dark.
- Reviewed by Quill for prose and Iris for correctness; CHANGELOG entry; Linear comment with docs link.

**Edge cases**

- Guidelines contradict a component story: the story is wrong; add a test task rather than softening the rule.
- Rules that only apply on touch or on desktop: `appliesTo` and `when` fields, so review agents skip irrelevant ones.
- Tenant brand overrides that break colour-usage rules (e.g. low-contrast accent): rules reference semantic tokens, generator handles nudging.
- Localisation later changing copy rules: mark language-specific rules `locale: en`.
- Docs engine search indexing MDX with embeds: provide `summary` text for the index.
- Rule removed or renumbered: keep IDs immutable; deprecate instead.

**Dependencies**

`design-system/storybook` (embeds), `collab/docs-engine` (hard for final home; Storybook fallback allowed). Soft: `design-system/component-spec-mapping` (related lists), `quality/review-rubrics` (severity names). Consumed by `quality/review-agents`, `quality/screenshot-annotation`, `spec-builder/spec-authoring-skill`, `agents/skills-library` (page-from-spec skill).

**Agent**

Written by Iris with Quill (Changelog Scribe and Page Spec Writer) editing. Reviewed by Sentinel (spec-conformance reviewer dry run against the rules) and Atlas.

**Size**

M: prose volume is the cost; the machine-readable rules make it load-bearing for review agents.
