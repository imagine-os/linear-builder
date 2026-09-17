---
identifier: "PAP-46"
title: "Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Forgejo live and mirrored"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-49", "PAP-52", "PAP-96", "PAP-133", "PAP-281"]
key: "forge/branch-policy"
url: "https://linear.app/paperos/issue/PAP-46/define-branch-protection-conventional-commits-and-worktree-per-issue"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:41.818Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-46: Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents

**Goal**

Define and enforce the conventions that let twenty Claude Code sessions commit in parallel without colliding: branch naming, one worktree per Linear issue, Conventional Commits with Linear trailers, and protection rules on `main` applied identically on Forgejo and GitHub. Output is a document and machine-applied configuration.

**Scope**

In:

* `docs/engineering/branch-policy.md`; rulesets as JSON applied by `scripts/apply-branch-policy.ts` to both forges; `commitlint` and `lefthook` config; `scripts/worktree.sh`; CODEOWNERS per character plus generated `ownership.json`.

Out: the orchestrator (PAP-96) and scheduler (PAP-102); release tagging (PAP-52).

**Spec**

* Branches `<character>/<PAP-n>-<kebab-slug>` (slug max 40); `release/<yyyy-mm-dd>`; `hotfix/<PAP-n>` only by Atlas with a Needs Justin comment; no direct pushes to `main`.
* Worktrees at `../paperos-worktrees/PAP-<n>` via `scripts/worktree.sh new|done PAP-<n>` (creates branch, copies `.env.example`, runs `pnpm install --offline` when possible, runs PAP-42 `stack up`).
* Conventional Commits 1.0 types `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`; scope = package or app; mandatory trailers `Linear: PAP-<n>` and `Character: <Name>`; optional `Sub-Agent:` and `Co-Authored-By`; enforced by `commitlint` via `lefthook` `commit-msg` and again in PAP-78.
* Rulesets: required PRs, required checks `ci / check`, linear history, signed commits preferred, bypass allowlist for the mirror token (PAP-47) and `bot-atlas` merges (PAP-48).
* CODEOWNERS mirrored to `.forgejo/CODEOWNERS`; `ownership.json` generated from it for PAP-102's file-lock hints; cross-owner PRs need both bot reviews or the `cross-owner` label from Atlas.

**Interface contract**

Provides:

* Commit-message grammar and trailer names consumed by PAP-52 (release notes links), PAP-133 (changelog), PAP-97 (PR status back to Linear), PAP-114 (session attribution).
* `ownership.json` schema `{ paths: [{ glob, owner: CharacterName }] }` consumed by PAP-102.
* `scripts/worktree.sh` CLI contract (exit codes 0, 2 refusal on dirty worktree) consumed by PAP-96 and PAP-93.
* Ruleset JSON files `ops/forge/rulesets/{github,forgejo}.json` reapplied by PAP-51 for each new repo.
* Required check name `ci / check` (PAP-13, PAP-78).

Consumes: `FORGEJO_ADMIN_TOKEN` (PAP-45) until bot tokens (PAP-48); roster names from plan.json (PAP-104).

**Definition of done**

* Document merged and linked from the template README.
* `lefthook.yml` and `commitlint.config.ts` present; a commit without `Linear:` is rejected locally and in CI (test in `scripts/__tests__/commitlint.test.ts`).
* `worktree.sh new PAP-999` and `done` covered by a shell test.
* `apply-branch-policy.ts` applied to `paperos-template` on both forges; a direct push to `main` rejected on each (transcripts).
* CODEOWNERS and `ownership.json` round-trip test; Atlas confirms the ownership map; Linear comment with links; changelog entry under Engineering.

**Test plan**

* Unit: commitlint fixtures (valid, missing trailer, wrong type, long subject); `ownership.json` generation from CODEOWNERS and back.
* Shell: `bats` for `worktree.sh` new, done, refusal on uncommitted changes, long slug truncation.
* Integration: `apply-branch-policy.ts --dry-run` diff against live rulesets is empty after apply; direct push attempts to `main` on both forges rejected (transcripts).
* Parity: script prints which GitHub-only ruleset features could not be applied on Forgejo.

**Demo**

Reviewer runs `scripts/worktree.sh new PAP-999`, commits a change without the `Linear:` trailer and watches lefthook reject it, fixes the message, then attempts `git push origin HEAD:main` and gets the protection error from both remotes. Under 2 minutes.

**Edge cases**

* Issue spanning two characters' paths: both reviews or `cross-owner`.
* Hotfix while `main` is red: Atlas-only branch with Needs Justin comment.
* Ruleset parity gaps degrade gracefully with a printed list.
* Human commit without lefthook: CI catches it with a clear message.
* Existing worktree with changes: script refuses and prints the path.

**Dependencies**

None; ready now. Consumers: PAP-49, PAP-52, PAP-96, PAP-102, PAP-133, PAP-78.

**Agent**

Built by Forge (lead). Reviewed by Sentinel (Code Reviewer); Atlas confirms ownership.

**Size**

M: policy plus four scripts with tests.
