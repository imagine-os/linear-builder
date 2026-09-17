---
identifier: "PAP-77"
title: "Export tokens to Figma variables and document the round-trip, or record the decision to skip Figma"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Research"
priority: 4
surfaces: ["Developer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66"]
blocks: []
key: "design-system/figma-sync"
url: "https://linear.app/paperos/issue/PAP-77/export-tokens-to-figma-variables-and-document-the-round-trip-or-record"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-77: Export tokens to Figma variables and document the round-trip, or record the decision to skip Figma

**Goal**

Decide whether a design tool belongs in the PaperOS loop before 2026-10-01. Either wire a token round-trip between the DTCG JSON and Figma variables and document it, or record a clear ADR to skip Figma in favour of Storybook and code-first design, with the criteria that would reopen the question.

**Scope**

In:
- Time-boxed research (one session): Figma Variables REST API availability (Enterprise plan only for writes), Tokens Studio plugin with GitHub sync, `@tokens-studio/sd-transforms` for Style Dictionary, Figma-to-code paths (Code Connect, MCP server), cost, and what Justin's current design workflow is (ask via a Needs Justin question with a default of "no Figma").
- If go: `pnpm --filter ui tokens:figma` exporting `tokens/*.tokens.json` into Tokens Studio format (`$themes.json`, sets per theme), import instructions, and a GitHub Action that opens a PR when the Tokens Studio sync branch changes; conflict rule: code is the source of truth, Figma is a mirror.
- If no-go: ADR plus a lightweight alternative: Storybook as the design surface, a `design/` folder for reference images, and a rule that agents propose visual changes as Storybook stories with screenshots.
- Either way: a `docs/design/design-tooling.md` page describing how visual proposals are made and reviewed.

Out: building a Figma plugin, redrawing components in Figma, Penpot evaluation beyond a paragraph.

**Spec**

- Research writeup `docs/research/figma-sync.md` (800-1,500 words): options table with columns cost, write access, automation, maintenance burden, agent usability; recommendation.
- Decision recorded as ADR `docs/adr/0007-design-tooling.md` with `status`, `alternatives`, `reopenWhen` (e.g. a human designer joins, or Figma variables write API reaches Professional plan).
- Go path technical details: Tokens Studio expects `{ "global": { "color": { "accent": { "500": { "value": "#...", "type": "color" } } } } }`; converter maps DTCG `$value/$type` and resolves OKLCH to hex with `culori`; themes exported as `$themes.json` entries with `selectedTokenSets`.
- Sync branch `figma-tokens` protected; Action `ops/ci/figma-tokens.yml` runs converter in reverse (Tokens Studio to DTCG) and opens a PR labelled `tokens` for Iris to review; CI runs `tokens:check` on it.
- No-go path deliverable: `design/README.md` describing reference images, Storybook "Proposal" stories tag, and the PR template checkbox "visual proposal attached" (`forge/pr-templates`).
- Ask Justin: a single Linear comment in Needs Justin with options A (skip), B (Tokens Studio free plugin, manual sync), C (Enterprise API); default A after 48 hours.

**Definition of done**

- Research doc and ADR merged with Justin's answer (or the default) recorded.
- Go: converter has Vitest round-trip tests on all token files; a Figma file with imported variables screenshot attached; Action runs on a test push.
- No-go: `design/README.md`, Storybook `Proposal` tag documented, PR template updated.
- `docs/design/design-tooling.md` published; CHANGELOG entry.
- Linear comment summarising the decision and linking the ADR; Needs Justin item closed.

**Edge cases**

- OKLCH colours outside sRGB gamut: clamp with `culori` `clampChroma` before hex export and note loss.
- Composite tokens (typography, shadow) map differently in Tokens Studio; export as composite types where supported, else split.
- Figma variable modes limited to 4 on lower plans: light, dark, hc fit; tenant themes never exported.
- Reverse sync renames a token: treat as delete plus add and require manual review.
- No Figma seat available: research proceeds on documentation alone; record that as a limitation.
- Justin does not answer in 48 hours: default A applies, ADR states this.

**Dependencies**

`design-system/tokens` (hard). Soft: `forge/pr-templates` (checkbox), `pm-linear/justin-queue` (question format), `libraries/eval-rubric` (scoring). Nothing blocks on this issue.

**Agent**

Researched by Scout (Library Evaluator) with Iris (Token Keeper) building any converter. Reviewed by Quill for the ADR and Atlas for the decision.

**Size**

S: a bounded research task; the converter, if built, is a few hundred lines with tests.
