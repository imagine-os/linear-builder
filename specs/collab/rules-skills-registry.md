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
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-134: Surface rules (CLAUDE.md, policies) and skills as browsable, editable objects in-app with version history

**Goal**

Make the rules and skills that govern agents visible and governable inside the product: every `CLAUDE.md`, rules file, skill, agent definition and policy appears as a browsable object with owners, version history, usage statistics from the prompt log and a propose-edit flow that opens a PR. Justin can see what agents are told to do without opening the repo.

**Scope**

In:
- Indexer `pnpm rules:index` in `packages/collab/rules/` scanning `.claude/CLAUDE.md`, `.claude/rules/**/*.md`, `.claude/skills/*/SKILL.md` (plus `skills.json` from `agents/skills-library`), `.claude/agents/*.md` (from `agents/roster-v1`), `docs/policies/**/*.md`, producing `docs/.generated/rules-index.json`: `[{ id, kind: rule|skill|agent|policy, path, title, description, version, owners[], allowedCharacters[], wordCount, updatedAt, lastCommit, tags[] }]`; frontmatter validated with the schemas from `agents/character-schema` and `agents/skills-library`.
- oRPC `rules.list`, `rules.get(id)` (content rendered from the repo at the deployed SHA), `rules.history(id)` (commits touching the path via the Forgejo API, `forge/in-app-git` client), `rules.diff(id, fromSha, toSha)`, `rules.usage(id)` (sessions that loaded the skill or agent, from `collab/prompt-log-store` events where `tool_name = 'Skill'` or `event = 'SessionStart'` with character), `rules.proposeEdit({ id, content, message })`.
- UI `/_app/dev/rules` (developer, staff.admin): list grouped by kind with search and filters (kind, owner, character), detail page rendering markdown through the docs engine renderer, metadata sidebar (owners, allowed characters, version, last change), History tab with diffs (`react-diff-viewer-continued` or the docs engine diff component), Usage tab (sessions in the last 30 days, sparkline, link to `collab/prompt-log-ui`), Propose edit (CodeMirror 6 markdown, commit message, opens PR on branch `rules/<id>` with trailers; PR link shown).
- Cross-links: a skill's `allowedCharacters` link to agent objects; agent objects list their skills; rules referenced by a skill (`references/`) link.
- Registered as `rule_skill` search entities for `collab/knowledge-search`.

Out: executing skills, editing `main` directly, approval workflow beyond the normal PR gates, per-tenant rules.

**Spec**

- Content is read from the git ref the app was built from (embedded via `import.meta.glob` for the template) and refreshed from Forgejo for other repos of the org; source repo is part of the object id (`paperos-template:skill:review-pr`).
- Word count and the 1500-word skill limit from `agents/skills-library` are shown with a warning badge when exceeded.
- Propose edit requires `rules.propose` permission (staff.admin, Atlas, Quill); agents' proposals carry attribution.
- Version is frontmatter `version` when present, else short SHA.
- Index rebuild on every deploy; history and usage fetched on demand with 5-minute cache.

**Definition of done**

- Index covers all objects in paperos-template; Vitest for the indexer and frontmatter validation; a missing frontmatter field fails `docs:lint`.
- Playwright: browse to a skill, view history, open a diff, propose an edit (mocked Forgejo) and see the PR link; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
- Usage tab shows real sessions from a seeded prompt log.
- axe clean; `docs/collab/rules-registry.md`; CHANGELOG entry; Linear comment with screenshots.
- Justin reviews one rule in-app and comments (via `collab/comments` on the object, anchor `entity:rule_skill:<id>`).

**Edge cases**

- Skill folder without SKILL.md: listed as invalid with a fix link.
- Same skill name in two repos: distinct ids by repo prefix.
- Forgejo unreachable: content still shown from the build; history tab shows a retry notice.
- Huge CLAUDE.md (20k words): rendered with a TOC; word-limit badge applies only to skills.
- Proposed edit conflicts with a concurrent merge: PR shows conflict; UI links to it, no auto-resolve.
- Prompt log lacks Skill events (older sessions): usage shows "no data before" with the first logged date.

**Dependencies**

`collab/docs-engine` (renderer) and `agents/skills-library` (`skills.json`, frontmatter) (hard). Soft: `agents/roster-v1`, `forge/in-app-git`, `collab/prompt-log-store`, `collab/comments`. Consumed by `agents/character-docs`.

**Agent**

Built by Quill (Prompt Logger) with Nova on UI. Reviewed by Atlas (governance) and Sentinel (Code Reviewer).

**Size**

M: indexer plus a CRUD-like UI with git history and a PR flow.
