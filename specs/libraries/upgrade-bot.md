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
blockedBy: ["PAP-48", "PAP-78"]
blocks: []
key: "libraries/upgrade-bot"
url: "https://linear.app/paperos/issue/PAP-217/set-up-renovate-with-grouped-upgrades-and-agent-reviewed-changelog"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-217: Set up Renovate with grouped upgrades and agent-reviewed changelog summaries

**Goal**

Keep dependencies current without burning Justin's or the agents' attention: self-hosted Renovate opens grouped upgrade PRs on a schedule, every PR gets an agent-written summary of what changed and what it means for our code, safe upgrades merge themselves once the gates pass, and risky ones become Linear work. Runs on both forges because it is a workflow, not the Mend app.

**Scope**

In:
- `renovate.json` at the paperos-template root plus a shared preset `ops/renovate/default.json` other imagine-os repos extend.
- Scheduled workflow `.github/workflows/renovate.yml` running `renovate` CLI (Docker image `renovate/renovate` pinned) against the repo with a bot token from `forge/bot-accounts` (Scout bot); runnable on Forgejo Actions via the Forgejo platform setting.
- Summary workflow `.github/workflows/upgrade-summary.yml` triggered when a Renovate PR opens or updates: spawns a Scout (Library Evaluator) Claude Code session through the orchestrator's headless entry point to post the summary comment.
- Automerge rules tied to Gate 1 and Gate 3 statuses from `quality/ci-gate1` and `quality/playwright-matrix`, executed by Atlas's Merger sub-agent so `forge/branch-policy` review rules hold.
- Dependency dashboard issue mirrored to Linear.

Out: security vulnerability alerts (`quality/security-scans` owns detection, this issue only consumes them), major framework migrations (become normal Linear issues), registry schema (`libraries/registry`).

**Spec**

- Renovate config: `extends: ["config:recommended", ":semanticCommits", ":pinAllExceptPeerDependencies"]`; `schedule: ["before 6am on monday"]` for non-security; `vulnerabilityAlerts.enabled: true` with `schedule: at any time`; `lockFileMaintenance` weekly; `rangeStrategy: pin`; `commitBodyTable: true`; `commitBody: "Linear: PAP-<upgrades-epic>\nCharacter: scout"` to satisfy the trailer rule from `forge/branch-policy`; `labels: ["upgrade", "upgrade:{{updateType}}"]`.
- Groups (`packageRules`): `@tanstack/*`; UI primitives (`@base-ui-components/*`, `radix-ui`, `react-aria-components`); editor and CRDT (`@tiptap/*`, `yjs`, `@hocuspocus/*`); `drizzle-orm` + `drizzle-kit`; test tooling (`vitest`, `@playwright/*`, `@axe-core/*`); `@biomejs/biome`; MCP servers from `libraries/mcp-servers`; Tauri (`@tauri-apps/*` npm and `tauri*` cargo in one group); GitHub Actions; Docker image tags in `ops/compose/`. Majors are never grouped with minors.
- Automerge: `devDependencies` patch and minor, and `dependencies` patch, with `automergeType: pr` and required statuses `gate/1-static`, `gate/3-visual`, `licenses`; Merger performs the merge when statuses are green and the summary verdict is `merge`. Minor `dependencies` and all majors require the summary verdict plus a Sentinel Code Reviewer pass (`quality/review-agents`).
- Summary comment format (posted once, edited on updates): packages and versions, release-note highlights with links, breaking changes detected by grepping our code for removed APIs, bundle delta from `quality/perf-budgets` report, license delta from `reports/licenses.json`, risk `low|medium|high`, verdict `merge|needs-work|hold`. For `needs-work` on minor upgrades the session pushes the fix commit to the Renovate branch (with `rebaseWhen: conflicted` so Renovate does not overwrite it); for majors it opens a Linear issue in Backlog with the summary as description and links it.
- Cost guard: summary session capped at 40 turns and the per-PR budget from `agents/cost-controls` (default $3); over budget it posts `hold` with the reason.
- Post-merge: `pnpm lib registry build` in CI updates versions in `registry.json`; no manual registry edits needed.
- Dependency dashboard: Renovate's dashboard issue on the forge; the weekly summary workflow copies its open list to a pinned Linear issue "Dependency dashboard" and posts a burn line (PRs opened, merged, held).

**Definition of done**

- `renovate.json`, preset, both workflows merged; first scheduled run opens grouped PRs (screenshot of the PR list).
- One patch PR automerges end to end with green statuses and a summary comment; one seeded major (pin an old version in a fixture branch) gets a `hold` or `needs-work` summary and a Linear issue.
- Summary workflow tests: prompt fixture and a mocked Claude response asserting the comment schema and the branch push path.
- Workflow verified on a Forgejo runner (`forge/actions-runner`) with the Forgejo platform setting; link in the PR.
- Docs `docs/libraries/upgrades.md` covering groups, automerge rules and how to pause Renovate; CHANGELOG entry; Linear comment with links.
- Sentinel Security Auditor confirms the bot token scopes are least privilege.

**Edge cases**

- Renovate PR conflicts with an agent's open PR touching the lockfile: `rebaseWhen: conflicted`, and `pm-linear/concurrency` file-lock hints treat `pnpm-lock.yaml` as shared.
- Release notes missing or huge: summary falls back to the diff of `package.json` and changelog headings; truncate to 2k tokens per package.
- Upgrade breaks Gate 3 visuals only: verdict `needs-work`, comment includes the screenshot diff links.
- Same package updated by a human agent mid-week: Renovate rebases or closes as superseded.
- Bot token expires: workflow fails loudly and posts to the Linear dashboard issue.
- Renovate schedule collides with the release train (`quality/release-train`): schedule Monday morning, release candidate Friday.

**Dependencies**

`quality/ci-gate1` (hard: required statuses). Soft: `quality/playwright-matrix`, `quality/perf-budgets`, `quality/security-scans`, `libraries/license-policy` (report inputs), `forge/bot-accounts` (token), `forge/actions-runner`, `pm-linear/orchestrator` (headless session entry), `agents/cost-controls`, `libraries/registry`.

**Agent**

Built by Scout (Library Evaluator) with Forge (Ops Runner) for workflows and Atlas (Merger) for automerge. Reviewed by Sentinel (Security Auditor, Code Reviewer).

**Size**

M: Renovate config is quick; the agent summary workflow and automerge plumbing are the real work.
