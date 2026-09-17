---
identifier: "PAP-24"
title: "Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Developer", "Agent"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-19", "PAP-257"]
blocks: []
key: "app-shell/template-docs"
url: "https://linear.app/paperos/issue/PAP-24/write-the-repo-template-guide-folder-conventions-how-an-agent-adds-a"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-24: Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target

**Goal**

Write the guide every new Claude Code session reads before touching the template: where things live, how a page is added from spec to route to test, how each target is run and shipped, and which conventions are non-negotiable. It is the onboarding path for agents and future humans alike.

**Scope**

In:
- `docs/template-guide.md` (main, 3,000-5,000 words) plus focused pages under `docs/shell/` (already stubbed by earlier issues) cross-linked and indexed.
- Root `CLAUDE.md` rewritten to a 300-word summary linking to the guide, with the "never do" list.
- `.claude/rules/*.md`: naming, imports, tests, specs-before-code, no secrets, commit format (from `forge/branch-policy`).
- Worked example: add a `/_app/invoices` page end-to-end (spec, route, component, test, screenshot, PR) with copy-pasteable snippets tested in CI.
- Target cheat-sheets: web dev/build/preview, desktop dev/build/release, mobile dev/build, kiosk, Pages preview.
- Troubleshooting FAQ seeded from real errors hit in P0 issues.

Out: component guidelines (`design-system/guidelines-docs`), spec-writing tutorial (`spec-builder/spec-docs`), agent character docs (`agents/character-docs`).

**Spec**

- Structure of `template-guide.md`: 1 Purpose; 2 Folder map (table: path, owner project, what goes here, what never goes here); 3 Commands; 4 Adding a page (10 numbered steps with file paths); 5 Data access pattern (link `data-layer/api-layer`); 6 Auth and audiences (link identity); 7 Targets; 8 Quality gates and what each expects (link `quality/*`); 9 Conventions; 10 Glossary.
- Every code snippet is extracted from files in `docs/examples/` that are compiled and tested in CI (`pnpm docs:check` uses a small script to verify snippet markers match source), so docs cannot rot silently.
- Docs are Markdown with front-matter (`title`, `owner`, `updated`) compatible with `collab/docs-engine` rendering; until that exists, GitHub renders them.
- Diagrams in Mermaid (folder tree, request flow, release flow).
- Reading-time budget: an agent must be able to read CLAUDE.md + section 4 in under 2,000 tokens; verify with a token count script.
- Links to Linear issue keys for anything not yet built are marked `(planned: <key>)`.

**Definition of done**

- Guide, CLAUDE.md, rules and worked example merged; `pnpm docs:check` green.
- A fresh Claude Code session given only the guide adds the example page and passes Gate 1 without asking a question (Atlas runs this trial; transcript linked).
- Token count of CLAUDE.md under 1,200; guide section 4 under 900.
- Docs rendered screenshot at 375, 1024 and 1920 (GitHub render or docs engine).
- Mermaid diagrams render on GitHub.
- CHANGELOG entry; Linear comment with the trial transcript and doc links.

**Edge cases**

- Guide references a command renamed later: `docs:check` also verifies every backticked `pnpm <script>` exists in `package.json`.
- Sections growing past budget: CI warns above token limits.
- Windows path separators in examples: use POSIX and note.
- Agent with no Rust toolchain: desktop section starts with a "skip if" check.
- Docs engine not yet live: relative links must work on GitHub and in-app.
- Out-of-date screenshots: mark with the SHA they were taken at.

**Dependencies**

`app-shell/router-layouts` and `app-shell/tauri-desktop` (hard, to document real behaviour). Soft: `app-shell/pwa`, `app-shell/env-config`, `forge/branch-policy`, `pm-linear/session-playbook`. Consumed by every build issue thereafter and by `agents/skills-library`.

**Agent**

Written by Quill (Spec and Documentation Lead) with Forge supplying technical review. Reviewed by Atlas (runs the cold-start trial) and Sentinel (Code Reviewer for snippet correctness).

**Size**

M: mostly writing, but the tested-snippets tooling and cold-start trial make it real work.
