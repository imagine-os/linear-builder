---
identifier: "PAP-112"
title: "Publish the character handbook: who does what, how to summon them, what they may not do"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Agent", "Staff"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104"]
blocks: []
key: "agents/character-docs"
url: "https://linear.app/paperos/issue/PAP-112/publish-the-character-handbook-who-does-what-how-to-summon-them-what"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-112: Publish the character handbook: who does what, how to summon them, what they may not do

**Goal**

Publish the handbook a human opens to understand the agent org: who each character is, what it owns, how to summon it from Linear or the CLI, what it may never do, and how to change it. Written for Justin first and future staff second, generated where possible from the roster so it never drifts from reality.

**Scope**

In:
- `docs/agents/handbook/` in the docs engine: `index.md` (org chart as mermaid, the one-paragraph story of how work flows), one page per lead `atlas.md`...`scout.md` with sub-character sections, `summoning.md`, `limits.md`, `changing-the-org.md`, `glossary.md`.
- Per-character page content: role and remit, reports to, sub-characters with triggers, tools and MCP servers (generated table), access scopes (generated), skills, budgets, escalation rules, example tasks it excels at, tasks to route elsewhere, three real example issues it completed (linked), and its memory file link.
- Summoning: assign the Character label in Linear and move to `Ready for Claude`; `pnpm agents run <name> --issue PAP-123` for local; `@character` mention convention in Linear comments picked up by the orchestrator to request a specific character's opinion as a comment (implemented here as a small handler using the existing comment webhook).
- Limits page: the shared deny list, the `Needs Justin` criteria, the kill switch, budgets, what "no merge rights" means for Sentinel.
- Changing the org: how to add a character (YAML, label, bot account, approval), retire one, change a budget, edit a prompt (PR plus smoke run), with a checklist.
- Generation: `pnpm agents docs` renders the generated tables from `roster.json` and `privilege-matrix.md`; hand-written prose lives in `docs/agents/handbook/_prose/<name>.md` and is merged, so regeneration never overwrites writing.

Out: the org chart UI (`agents/org-chart-ui`), end-user documentation of product features, the review rubrics text.

**Spec**

- Reading level: plain language, no internal jargon without a glossary entry; each page under 1200 words; the index under 600.
- Every "may not" statement links to the enforcing mechanism (deny list, hook, branch protection) so claims are verifiable.
- Pages carry frontmatter `generatedFrom` and `lastVerified`; CI fails if `roster.json` changed and docs were not regenerated.
- The `@character` handler: on a Comment `create` webhook containing `@atlas`...`@scout` from a human, spawn a short read-only session (plan mode, `maxTurns` 8, Sonnet 5 unless the question is architectural) that replies in a comment with the footer; cost capped at $3 per mention.
- Screenshots of two handbook pages on phone width are required because Justin reads on mobile.

**Definition of done**

- All pages present and rendering in the docs engine (or the repo, if the engine is not yet live) with generated tables matching `roster.json`.
- `pnpm agents docs --check` in CI.
- `@sentinel` mention on a test issue produces a relevant reply comment within 2 minutes (screenshot).
- Read-through by Sentinel for accuracy against the privilege matrix and by Quill for clarity; every "may not" has a link.
- Screenshots at 375 and 1280 px; changelog entry; Linear comment with links and screenshots.

**Edge cases**

- Character retired: page moves to `handbook/retired/` with the retirement ADR; mentions of it reply with a redirect.
- Mention by an agent (not human): ignored to prevent loops.
- Mention asks for an action, not an opinion: the reply explains that actions come from issues and offers to draft one (creates a Backlog issue in contract format on `yes`).
- Roster and prose disagree (prose claims a tool the YAML denies): CI lint flags tool names in prose that are not in the generated table.
- Docs engine down: pages still readable on the forge as markdown; links are relative.
- Very long generated access tables (Atlas): collapse into a details block.

**Dependencies**

- `agents/roster-v1` (roster.json, prompts) and, through it, `agents/tool-scopes` for the privilege matrix.
- Uses `collab/docs-engine` when available and `pm-linear/webhooks` for the mention handler.

**Agent**

Built by Quill (lead); reviewed by Sentinel (accuracy) and Atlas; Justin reads the index as the acceptance test and leaves one comment.

**Size**

M: nine generated-plus-prose pages and one small webhook handler.
