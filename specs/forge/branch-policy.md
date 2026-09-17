---
identifier: "PAP-46"
title: "Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Forgejo live and mirrored"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-133", "PAP-49", "PAP-52", "PAP-96"]
key: "forge/branch-policy"
url: "https://linear.app/paperos/issue/PAP-46/define-branch-protection-conventional-commits-and-worktree-per-issue"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-46: Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents

**Goal**

Define and enforce the conventions that let up to twenty Claude Code sessions commit in parallel without colliding: branch naming, one git worktree per Linear issue, Conventional Commits with Linear trailers, and protection rules on `main` applied identically on Forgejo and GitHub. The output is both a document and machine-applied configuration.

**Scope**

- In: policy document, branch-protection rulesets as JSON applied by script to both forges, commitlint and lefthook configuration in the template repo, a worktree helper script, CODEOWNERS ownership map per character.
- Out: the orchestrator that spawns sessions (pm-linear/orchestrator) and the concurrency scheduler (pm-linear/concurrency); this issue only gives them rules and hints to consume.
- Out: release tagging (forge/release-tags).

**Spec**

Document `docs/engineering/branch-policy.md` in `imagine-os/paperos-template` covering:

- Branch names: `<character>/<PAP-n>-<kebab-slug>` (e.g. `forge/PAP-42-mirror-setup`); release branches `release/<yyyy-mm-dd>`; no direct pushes to `main`.
- Worktrees: every session works in `../paperos-worktrees/PAP-<n>` created by `scripts/worktree.sh new PAP-<n>` (which also creates the branch, copies `.env.example`, runs `pnpm install --offline` when possible); `scripts/worktree.sh done PAP-<n>` removes it after merge.
- Commits: Conventional Commits 1.0 (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`), scope = package or app name; body wraps at 100; mandatory trailers `Linear: PAP-<n>` and `Character: <Name>`, optional `Co-Authored-By`. Enforced by `commitlint` (`@commitlint/config-conventional` plus a custom rule for the trailers) run via `lefthook` `commit-msg` hook and again in quality/ci-gate1.
- File ownership: `.github/CODEOWNERS` (mirrored to `.forgejo/CODEOWNERS`) maps paths to character bot accounts (packages/ui -> Iris, specs/ docs/ -> Quill, ops/ -> Forge, and so on) matching the access lists in plan.json; it doubles as the file-lock hint source for pm-linear/concurrency, exported as `ops/forge/ownership.json` by `scripts/export-ownership.ts`.
- Merge policy: squash-merge only, linear history, PR title becomes the commit subject, rebase onto `main` before Gate 3 runs; the Merger sub-agent (Atlas) is the only merger.
- Protection rulesets: `ops/forge/policies/main-ruleset.github.json` (GitHub repository ruleset API) and `ops/forge/policies/main-branch.forgejo.json` (Forgejo branch protection API) requiring: PR before merge, status checks `gate1`, `gate2-review`, `gate3-visual` to pass, no force-push, no deletion, dismiss stale approvals; human approvals required = 0 but a required check from the Sentinel bot. Applied by `scripts/apply-branch-policy.ts <repo>` using tokens from forge/bot-accounts, idempotent.

**Definition of done**

- Policy document merged and linked from the template README.
- `lefthook.yml`, `commitlint.config.ts` present; a commit lacking `Linear:` trailer is rejected locally and in CI (test committed under `scripts/__tests__/commitlint.test.ts`).
- `scripts/worktree.sh new PAP-999` creates a worktree and branch; `done` removes both; covered by a bats or Vitest shell test.
- `apply-branch-policy.ts` applied to `paperos-template` on both forges; a direct push to `main` is rejected on each (evidence: terminal output in PR).
- CODEOWNERS and `ownership.json` generated and consistent (test asserts round-trip).
- Sentinel Code Reviewer approves; Atlas confirms the ownership map matches the roster.
- Linear comment with links to the document and the two rejected-push transcripts.
- Changelog entry under "Engineering".

**Edge cases**

- An issue spans two characters' paths: the PR requires both owners' bot review or an Atlas override label `cross-owner`; document the override.
- Hotfix needed while `main` checks are red: `hotfix/<PAP-n>` branches allowed only by Atlas with a Needs Justin comment.
- Forgejo and GitHub ruleset feature parity differs (GitHub rulesets support required workflows; Forgejo does not): the script degrades gracefully and prints what could not be applied.
- Commit made by a human without lefthook installed: CI check catches it; error message explains the trailer format.
- Worktree directory already exists with uncommitted changes: script refuses and prints the path rather than deleting.
- Branch name exceeds 100 characters because of a long slug: slug truncated to 40 characters.

**Dependencies**

- None blocking. Consumers: pm-linear/orchestrator, pm-linear/concurrency, quality/ci-gate1, forge/pr-templates, forge/release-tags. Tokens from forge/bot-accounts are needed to run `apply-branch-policy.ts` against Forgejo; use `paperos-admin` until then.

**Agent**

- Builds: Forge (lead).
- Reviews: Sentinel (Code Reviewer) and Atlas (Dispatcher sub-agent, for worktree ergonomics).

**Size**

M: mostly configuration and scripts, but it must be exercised on two forges with real rejection evidence.
