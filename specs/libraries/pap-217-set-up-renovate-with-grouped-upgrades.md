---
identifier: "PAP-217"
title: "Set up Renovate with grouped upgrades and agent-reviewed changelog summaries"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Infra"
priority: 3
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-48", "PAP-78", "PAP-493"]
blocks: []
key: "libraries/upgrade-bot"
url: "https://linear.app/paperos/issue/PAP-217/set-up-renovate-with-grouped-upgrades-and-agent-reviewed-changelog"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:42.001Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-217: Set up Renovate with grouped upgrades and agent-reviewed changelog summaries

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Keep dependencies current without burning attention: self-hosted Renovate opens grouped upgrade PRs on a schedule, every PR gets an agent-written summary of what changed and what it means for our code, safe upgrades merge themselves once gates pass, and risky ones become Linear work. Runs on both forges as a workflow, not the Mend app.

**Scope**

In:

* `renovate.json` at the template root plus shared preset `ops/renovate/default.json` other repos extend.
* `.github/workflows/renovate.yml` running the pinned `renovate/renovate` image with the Scout bot token from PAP-48; Forgejo platform setting for Forgejo Actions.
* `.github/workflows/upgrade-summary.yml` on Renovate PR open or update: spawns a Scout (Library Evaluator) session through PAP-96's headless entry to post the summary comment.
* Automerge tied to statuses `gate/1-static`, `gate/3-visual`, `licenses`, executed by Atlas's Merger sub-agent so PAP-46 rules hold.
* Dependency dashboard mirrored to a pinned Linear issue with a weekly burn line.

Out: vulnerability detection (PAP-80; consumed here), major framework migrations (normal issues), registry schema (PAP-216).

**Spec**

* Config: `extends: ["config:recommended", ":semanticCommits", ":pinAllExceptPeerDependencies"]`, `schedule: ["before 6am on monday"]`, `vulnerabilityAlerts` at any time, weekly `lockFileMaintenance`, `rangeStrategy: pin`, `commitBody: "Linear: PAP-<upgrades-epic>\nCharacter: scout"`, labels `upgrade`, `upgrade:{{updateType}}`.
* Groups: `@tanstack/*`; UI primitives; editor and CRDT (`@tiptap/*`, `yjs`, `@hocuspocus/*`); Drizzle; test tooling; Biome; MCP servers from PAP-210; Tauri npm and cargo together; GitHub Actions; Docker tags in `ops/compose/`. Majors never grouped with minors.
* Automerge: devDependency patch and minor, dependency patch, with `automergeType: pr`, required statuses above and summary verdict `merge`. Minor dependencies and all majors need the verdict plus a Sentinel Code Reviewer pass (PAP-81).
* Summary comment (posted once, edited on update): packages and versions, release-note highlights, breaking changes found by grepping our code for removed APIs, bundle delta from PAP-87, license delta from `reports/licenses.json`, risk `low|medium|high`, verdict `merge|needs-work|hold`. `needs-work` on minors pushes a fix commit to the branch (`rebaseWhen: conflicted`); majors open a Backlog issue.
* Cost guard: 40 turns and the PAP-111 per-PR budget (default $3); over budget posts `hold`.
* Post-merge `pnpm lib registry build` updates versions.

**Interface contract**

Provides: preset `ops/renovate/default.json`, both workflows, `UpgradeSummary` schema `{ packages[], breaking[], bundleDelta, licenseDelta, risk, verdict }` posted as a sticky comment via PAP-78's action, labels `upgrade:*`, pinned Linear "Dependency dashboard" issue. Consumes: PAP-78 statuses and sticky-comment action, PAP-82 `gate/3-visual`, PAP-211 `licenses` status and report, PAP-87 perf report (soft), PAP-80 alerts (soft), PAP-48 bot token, PAP-50 runner, PAP-96 headless entry, PAP-111 budget, PAP-216 build, PAP-97 concurrency file-lock hints for `pnpm-lock.yaml`.

**Definition of done**

* Config, preset and both workflows merged; first scheduled run opens grouped PRs (screenshot).
* One patch PR automerges end to end with green statuses and a summary; one seeded major (old pin on a fixture branch) gets `hold` or `needs-work` and a Linear issue.
* Workflow verified on a Forgejo runner with the platform setting; link in the PR.
* `docs/libraries/upgrades.md` (groups, automerge rules, pausing); CHANGELOG; Linear comment.
* Sentinel Security Auditor confirms least-privilege token scopes.

**Test plan**

* Vitest: summary prompt fixture and mocked Claude response asserting the comment schema, verdict routing, branch push path, budget guard producing `hold`.
* Config: `renovate-config-validator` in Gate 1.
* Integration: seeded fixture branch with an old patch and an old major; observe automerge and hold paths on both forges.

**Demo**

Reviewer triggers `renovate.yml` by `workflow_dispatch` on a fixture branch pinning an old `vitest`, watches the grouped PR open, reads the summary comment with a `merge` verdict, and sees it automerge once statuses are green. Under two minutes after CI.

**Edge cases**

* Conflict with an agent PR on the lockfile: `rebaseWhen: conflicted`; lockfile shared in PAP-97.
* Missing or huge release notes: `package.json` diff and changelog headings, 2k tokens per package.
* Only Gate 3 visuals break: `needs-work` with diff links.
* Same package upgraded mid-week: Renovate rebases or closes as superseded.
* Bot token expires: loud failure on the dashboard issue.
* Release train (PAP-88): Monday upgrades, Friday RC.

**Dependencies**

PAP-78 (hard: required statuses), PAP-48 (hard: bot token). Soft: PAP-82, PAP-87, PAP-80, PAP-211, PAP-50, PAP-96, PAP-111, PAP-216, PAP-210 group.

**Agent**

Built by Scout (Library Evaluator) with Forge (Ops Runner) and Atlas (Merger). Reviewed by Sentinel (Security Auditor, Code Reviewer).

**Size**

M: config is quick; the summary workflow and automerge plumbing are the work.
