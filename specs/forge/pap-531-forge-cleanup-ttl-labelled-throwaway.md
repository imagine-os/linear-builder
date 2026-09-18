---
identifier: "PAP-531"
title: "`forge cleanup`: TTL-labelled throwaway repos (`gp-`, `drill-`, `slot-`, `cli-sandbox-`), stale branch and worktree reaper, protected list, nightly sweep on both forges and pool slot release"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-51", "PAP-520", "PAP-526"]
blocks: ["PAP-429"]
key: "r4/forge/repo-cleanup"
url: "https://linear.app/paperos/issue/PAP-531/forge-cleanup-ttl-labelled-throwaway-repos-gp-drill-slot-cli-sandbox"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:03.023Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-531: `forge cleanup`: TTL-labelled throwaway repos (`gp-`, `drill-`, `slot-`, `cli-sandbox-`), stale branch and worktree reaper, protected list, nightly sweep on both forges and pool slot release

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-429 deletes `gp-` repos "through the PAP-273 runbook script", PAP-29 removes `drill-<date>` "by PAP-51", PAP-22 tears down `cli-sandbox`, PAP-365 releases pool slots on cleanup: four issues assume a cleanup command that does not exist. Twenty sessions also leave merged branches and dead worktrees behind. One reaper with a protected list closes all of it.

**Scope**

In:

* `forge cleanup [--dry-run] [--kind repos|branches|worktrees|all]` in `packages/forge-cli`: repos matching `ops/forge/cleanup.yml` prefixes with a `paperos-ttl: <iso>` topic or description marker past their TTL are deleted on both forges and removed from `repos.yml`; failed golden-path runs keep 24 h (PAP-429 rule).
* Branches: merged branches older than 2 days and unmerged `<character>/PAP-n-*` branches whose Linear issue is Done or Canceled for 7 days are deleted (with a Linear comment); `release/*` and `hotfix/*` never.
* Worktrees: `../paperos-worktrees/PAP-<n>` whose issue is Done and branch deleted are removed on the orchestrator host (PAP-96 hook).
* Pool: swept repos that hold a warm-pool slot call `releaseSlot` (PAP-500).
* Protected list in `cleanup.yml` (template, infra, every app repo) checked by name and id; nightly `cleanup.yml` workflow on Forgejo Actions with a GitHub fallback; summary comment on a standing Linear issue.

Out: tenant data purge (PAP-355), Coolify preview teardown (PAP-505), backup pruning (PAP-274).

**Spec**

* Deletion needs both the prefix match and the TTL marker; either alone is not enough.
* `--dry-run` is the default in CI until the protected list has been reviewed by Atlas once (`cleanup.yml` `armed: true`).
* Every deletion is logged with actor `bot-forge`, repo id and reason to the audit channel and the summary.
* A repo deleted on one forge but not the other (API failure) is retried next night and reported as `partial`.

**Interface contract**

Provides: `forge cleanup`, `cleanup.yml` config and workflow, TTL marker convention `paperos-ttl`; consumed by PAP-429, PAP-29, PAP-22 (sandbox), PAP-365 and PAP-500 (slot release), PAP-96 (worktree hook), PAP-51 (registers the marker at bootstrap when `--ttl` is passed).

Consumes: bootstrap and `repos.yml` (PAP-51), mirror pairs (PAP-47), Linear states (PAP-91) for branch decisions, bot identity (PAP-48).

**Definition of done**

* Fixture: three repos with expired TTL and one protected; sweep deletes three on both forges, skips the protected one, releases one slot (transcript).
* Merged branch older than 2 days deleted; `release/*` untouched; `docs/runbooks/cleanup.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: TTL and prefix matching; protected list by id; branch decision matrix over Linear state fixtures.
* E2E: nightly dry run on the fixture set, then armed run; assert both forges and `repos.yml`.

**Demo**

Reviewer runs `forge cleanup --dry-run` and reads the table of what would go and why, then the armed run on the fixture repos and refreshes both forges. Under 2 minutes.

**Edge cases**

* TTL marker edited by hand to the past on a protected repo: protected wins.
* Branch with an open PR: never deleted regardless of age.
* Linear unavailable: branch sweep skipped, repo sweep proceeds.

**Dependencies**

Hard: PAP-51, PAP-47. Soft: PAP-91, PAP-48, PAP-96, PAP-500. Blocks PAP-429.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/app-shell/pr-preview-environments` = PAP-505, `r4/app-shell/warm-pool-job` = PAP-500.
