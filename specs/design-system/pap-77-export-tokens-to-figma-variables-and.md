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
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:13.107Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-77: Export tokens to Figma variables and document the round-trip, or record the decision to skip Figma

**Goal**

Decide before 2026-10-01 whether a design tool belongs in the loop: either wire a token round-trip between the DTCG JSON and Figma variables and document it, or record an ADR to skip Figma in favour of Storybook and code-first design with the criteria that would reopen the question.

**Scope**

* In: one-session research (Figma Variables REST API write access and plan requirements, Tokens Studio plugin with GitHub sync, `@tokens-studio/sd-transforms`, Code Connect and the Figma MCP server, cost, Justin's current workflow via one Needs Justin question defaulting to "no Figma"); the go path converter and Action; the no-go path `design/README.md`, Storybook `proposal` tag and PR template checkbox; `docs/design/design-tooling.md` either way.
* Out: a Figma plugin, redrawing components in Figma, Penpot beyond a paragraph.

**Spec**

* `docs/research/figma-sync.md` (800-1 500 words): options table with cost, write access, automation, maintenance burden, agent usability; recommendation.
* ADR `docs/adr/0007-design-tooling.md` with `status`, `alternatives`, `reopenWhen` (a human designer joins; variables write API reaches the Professional plan).
* Go path: `pnpm --filter ui tokens:figma` converts DTCG `$value/$type` to Tokens Studio sets (`{ "global": { "color": { "accent": { "500": { "value": "#…", "type": "color" } } } } }`), OKLCH to hex via `culori` with `clampChroma`, themes as `$themes.json` with `selectedTokenSets`; protected `figma-tokens` branch; Action `ops/ci/figma-tokens.yml` reverse-converts and opens a PR labelled `tokens` for Iris; code is the source of truth.
* No-go path: `design/README.md` for reference images, Storybook `proposal` tag documented, PR template checkbox "visual proposal attached" (PAP-49).
* Needs Justin comment with options A skip, B Tokens Studio manual sync, C Enterprise API; default A after 48 hours.

**Interface contract**

* Provides: the ADR, `docs/design/design-tooling.md` (how visual proposals are made and reviewed), and on the go path `tokens:figma` plus the `figma-tokens` branch convention; on the no-go path the `proposal` story tag (already reserved by PAP-69) and the PR template line.
* Requires: PAP-66 tokens (hard). Soft: PAP-49 template, PAP-94 question format, PAP-209 scoring.
* Consumers: PAP-92 playbook (how to propose visual changes), PAP-76 (links the tooling page).

**Definition of done**

* Research doc and ADR merged with Justin's answer or the default recorded.
* Go: converter round-trip Vitest on all token files; screenshot of a Figma file with imported variables; Action runs on a test push.
* No-go: `design/README.md`, `proposal` tag documented, PR template updated.
* `docs/design/design-tooling.md` published; changelog entry; Linear comment summarising the decision; Needs Justin item closed.

**Test plan**

* Go: round-trip test DTCG to Tokens Studio to DTCG equals input for every token file; gamut clamping test on an out-of-sRGB OKLCH; composite tokens split correctly.
* No-go: PR template lint (PAP-49) passes with the new checkbox; a `proposal` story renders in Storybook.
* Either: link check on the two docs.

**Demo**

Open the ADR and read the decision and `reopenWhen`; on the go path run `pnpm --filter ui tokens:figma` and open the generated `$themes.json`; on the no-go path open a `proposal`-tagged story. Under one minute.

**Edge cases**

* Out-of-gamut OKLCH: clamped with a noted loss.
* Figma modes limited to 4: light, dark, hc fit; tenant themes never exported.
* Reverse sync renames a token: treated as delete plus add, manual review.
* No Figma seat: research from documentation; limitation recorded.
* No answer in 48 hours: default A applies and the ADR says so.

**Dependencies**

PAP-66 (hard). Soft: PAP-49, PAP-94, PAP-209. Nothing blocks on this issue.

**Agent**

Scout (Library Evaluator) researches; Iris (Token Keeper) builds any converter. Reviewed by Quill (ADR) and Atlas (decision).

**Size**

S.
