---
identifier: "PAP-24"
title: "Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Agent", "Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-19", "PAP-257", "PAP-305"]
blocks: []
key: "app-shell/template-docs"
url: "https://linear.app/paperos/issue/PAP-24/write-the-repo-template-guide-folder-conventions-how-an-agent-adds-a"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:01.144Z"
---

# PAP-24: Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target

**Goal**

Write the guide every new Claude Code session reads before touching the template: where things live, how a page goes from spec to route to test, how each target runs and ships, and which conventions are non-negotiable. Docs are checked in CI so they cannot rot.

**Scope**

In:

* `docs/template-guide.md` (3,000-5,000 words) plus `docs/shell/*` pages cross-linked and indexed.
* Root `CLAUDE.md` rewritten to a 300-word summary with the "never do" list.
* `.claude/rules/*.md`: naming, imports, tests, specs-before-code, no secrets, commit format (PAP-46).
* Worked example `/_app/invoices` end to end with snippets extracted from `docs/examples/` and compiled in CI.
* Target cheat-sheets: web, desktop, mobile, kiosk, Pages, staging.
* Troubleshooting FAQ from real P0 errors.

Out: component guidelines (PAP-77), spec tutorial (PAP-127), character docs (PAP-115).

**Spec**

* Sections: Purpose; Folder map table (path, owner project, what goes here, what never goes here); Commands; Adding a page (10 numbered steps with paths); Data access (PAP-35); Auth and audiences; Targets; Quality gates; Conventions; Glossary.
* `pnpm docs:check` verifies snippet markers match `docs/examples/` sources, every backticked `pnpm <script>` exists in `package.json`, and token budgets (CLAUDE.md under 1,200 tokens, section 4 under 900).
* Front-matter `title`, `owner`, `updated` for PAP-128 rendering; Mermaid diagrams for folder tree, request flow, release flow.
* Unbuilt references marked `(planned: PAP-n)`.

**Interface contract**

Provides:

* `docs/template-guide.md`, `CLAUDE.md`, `.claude/rules/*.md` as the onboarding path PAP-108 (skills library) and PAP-93 (session playbook) link to.
* `docs/examples/invoices/` compiled example (spec, route, component, test) that PAP-120 uses as a codegen fixture.
* Script `pnpm docs:check` that PAP-78 Gate 1 runs.
* Front-matter schema `{ title, owner, updated }` shared with PAP-128.

Consumes: real behaviour of PAP-16, PAP-19, PAP-18, PAP-17; commit format from PAP-46; the docs engine (PAP-128) for in-app rendering, GitHub rendering until then.

**Definition of done**

* Guide, CLAUDE.md, rules and example merged; `pnpm docs:check` green.
* A fresh Claude Code session given only the guide adds the example page and passes Gate 1 without a question (Atlas runs the trial; transcript linked).
* Token counts under budget; Mermaid renders on GitHub.
* Docs screenshots at 375, 1024, 1920; CHANGELOG; Linear comment with the trial transcript.

**Test plan**

* Static: `docs:check` snippet-marker test, script-name test, token-count test with fixtures that fail.
* Compile: `docs/examples/invoices` typechecks and its Vitest test passes in CI.
* Trial: one scripted Claude Code session (PAP-96 harness or manual) adds a page from the guide; success criterion is Gate 1 green with zero clarifying questions.
* Visual: GitHub render and, once PAP-128 exists, in-app render at 375, 1024, 1920.

**Demo**

Reviewer opens `CLAUDE.md`, follows section 4 of the guide to add a `/_app/hello` route with a spec, runs `pnpm check`, and sees the page in `pnpm dev`. Under 2 minutes for an experienced reader; the agent trial transcript shows the same path unassisted.

**Edge cases**

* Renamed command: `docs:check` catches it.
* Section over budget: CI warns above limits.
* Windows separators: POSIX paths with a note.
* No Rust toolchain: desktop section starts with a skip-if check.
* Stale screenshots: stamped with the SHA taken.

**Dependencies**

PAP-16, PAP-19 (hard). Soft: PAP-17, PAP-18, PAP-46, PAP-93, PAP-128. Consumed by every build issue and PAP-108.

**Agent**

Written by Quill (Spec and Documentation Lead) with Forge supplying commands. Reviewed by Atlas (trial) and Sentinel.

**Size**

M: long document plus a checker script.
