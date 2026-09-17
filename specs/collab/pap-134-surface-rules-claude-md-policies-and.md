---
identifier: "PAP-134"
title: "Surface rules (CLAUDE.md, policies) and skills as browsable, editable objects in-app with version history"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent", "Developer"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-105", "PAP-128"]
blocks: []
key: "collab/rules-skills-registry"
url: "https://linear.app/paperos/issue/PAP-134/surface-rules-claudemd-policies-and-skills-as-browsable-editable"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:29.085Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-134: Surface rules (CLAUDE.md, policies) and skills as browsable, editable objects in-app with version history

**Goal**

Make the rules and skills that govern agents visible and governable in the product: every `CLAUDE.md`, rules file, skill, agent definition and policy is a browsable object with owners, version history, usage from the prompt log and a propose-edit flow that opens a PR. Justin sees what agents are told without opening the repo.

**Scope**

In:

* Indexer `pnpm rules:index` in `packages/collab/rules/` over `.claude/CLAUDE.md`, `.claude/rules/**/*.md`, `.claude/skills/*/SKILL.md` (plus `skills.json` from PAP-105), `.claude/agents/*.md` (PAP-104), `docs/policies/**/*.md` → `docs/.generated/rules-index.json`; frontmatter validated with PAP-103 and PAP-105 schemas.
* oRPC `rules.list`, `rules.get(id)`, `rules.history(id)` (commits via the Forgejo API), `rules.diff(id, from, to)`, `rules.usage(id)` (sessions from PAP-129 where `tool_name = 'Skill'` or `SessionStart` with character), `rules.proposeEdit({ id, content, message })`.
* UI `/_app/dev/rules` (developer, `staff.admin`): list grouped by kind with search and filters; detail with markdown via the PAP-128 renderer, metadata sidebar, History tab with diffs (`react-diff-viewer-continued`), Usage tab (30-day sessions, sparkline, links to PAP-135), Propose edit (CodeMirror 6, branch `rules/<id>`, PR link).
* Cross-links skill ↔ agent ↔ referenced rules; registered as `rule_skill` search entity for PAP-138.

Out: executing skills, editing `main` directly, per-tenant rules.

**Spec**

* Content read from the built git ref (`import.meta.glob`) and refreshed from Forgejo for other org repos; ids `repo:kind:name`.
* 1500-word skill limit from PAP-105 shown as a warning badge.
* `rules.propose` permission (staff.admin, Atlas, Quill); agent proposals carry attribution.
* Index rebuilt per deploy; history and usage cached 5 minutes.

**Interface contract**

Exposes: `RuleObject { id, kind: rule|skill|agent|policy, path, title, description, version, owners[], allowedCharacters[], wordCount, updatedAt, lastCommit, tags[] }` and `rules-index.json`; oRPC procedures above; search entity `rule_skill`; comment anchor `entity:rule_skill:<id>` (PAP-131); page consumed by PAP-112 (character docs link here). Consumes: `skills.json` and SKILL frontmatter from PAP-105, character frontmatter from PAP-103/PAP-104, `renderMdx` from PAP-128, Forgejo client from PAP-54's first child when merged (else a 40-line fetch wrapper here), `promptLog.events.list` from PAP-129.

**Definition of done**

* Index covers all objects in paperos-template; a missing frontmatter field fails `docs:lint`.
* Usage tab shows real sessions from a seeded prompt log.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; `docs/collab/rules-registry.md`; CHANGELOG entry; Linear comment with screenshots.
* Justin reviews one rule in-app and comments on it.

**Test plan**

* Vitest: indexer over a fixture `.claude/` tree (valid, missing SKILL.md, oversized skill), frontmatter validation, id derivation across two repos, usage aggregation from fixture events.
* Integration: `rules.history` and `rules.diff` against a mocked Forgejo API; `rules.proposeEdit` creates a branch and PR on a scratch Forgejo repo in CI (PAP-273 stack) and returns the URL; `callAs(customer)` gets 403.
* Playwright: browse to `review-pr`, open History, open a diff, propose an edit and see the PR link; run at 375 and 1280.
* Visual: Gate 3 baselines for list and detail at the seven widths, both themes.

**Demo**

Open `/_app/dev/rules`, filter to skills, open `review-pr`, read the word-count badge, open Usage to see last week's sessions, open History and a diff, click Propose edit, change one line, submit and open the PR. Under two minutes.

**Edge cases**

* Skill folder without SKILL.md: listed as invalid with a fix link.
* Forgejo unreachable: content from the build; history shows retry.
* 20k-word CLAUDE.md: TOC, no word-limit badge.
* Proposed edit conflicts with a merge: PR shows conflict; no auto-resolve.
* Older sessions lack Skill events: "no data before <date>".

**Dependencies**

PAP-128, PAP-105 (hard, encoded). Soft: PAP-104, PAP-276 (Forgejo client), PAP-129, PAP-131. Consumed by PAP-112.

**Agent**

Built by Quill (Prompt Logger) with Nova on UI. Reviewed by Atlas (governance) and Sentinel (Code Reviewer).

**Size**

M: indexer plus a CRUD-like UI with git history and a PR flow.
