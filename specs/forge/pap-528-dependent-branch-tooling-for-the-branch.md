---
identifier: "PAP-528"
title: "Dependent-branch tooling for the branch-start rule: `worktree.sh new --base`, PR base tracking in `.paperos/branch.json`, auto-retarget and rebase when the base PR merges"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-46"]
blocks: []
key: "r4/forge/dependent-branches"
url: "https://linear.app/paperos/issue/PAP-528/dependent-branch-tooling-for-the-branch-start-rule-worktreesh-new-base"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:02.745Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-528: Dependent-branch tooling for the branch-start rule: `worktree.sh new --base`, PR base tracking in `.paperos/branch.json`, auto-retarget and rebase when the base PR merges

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

The Execution Schedule only fits before 10-01 because of the branch-start rule: a dependent issue starts when its blockers are In Review and works against their PR branches. PAP-96 passes `BASE_BRANCHES` into the session prompt, but nothing creates the worktree on those branches, tracks the relationship, retargets the PR when the base merges, or rebases the dependent. Graphite and GitLab stacked MRs are the reference; this issue builds the minimum for agents.

**Scope**

In:

* `scripts/worktree.sh new PAP-<n> --base <branch>[,<branch>]`: creates the branch from `main`, merges each base branch (octopus for two or more, fail on conflict with the file list), writes `.paperos/branch.json` `{ issue, bases: [{ branch, pr, mergedSha? }] }`.
* PR opening (`pr-body.ts`, PAP-49): base set to the first base branch on both forges when a single base, otherwise `main` with a `Stacked on:` section listing the base PRs; label `stacked`.
* `scripts/forge/retarget.ts` run by a cron and by the PAP-97 webhook on `pull_request.closed(merged)`: for every open PR whose base merged, retarget to `main`, rebase the branch onto `main` (dropping the base commits), push with the bot identity, comment the result; on conflict label `needs-rebase` and wake the owning session (PAP-96).
* Status: `forge stack <PAP-n>` prints the stack with merge states; the PAP-89 digest shows stacked PRs as one row.

Out: merge ordering and the queue (PAP-527), the promotion logic that decides who may start (PAP-96, PAP-93).

**Spec**

* A dependent PR is never eligible to merge before its bases (`merge-automation` reads `branch.json`).
* Rebase drops base commits by `git rebase --onto main <baseTip>`; if the base was squash-merged, `git rebase` uses the recorded base tip so no duplicate commits remain.
* Retarget runs within 5 minutes of the base merge on either forge.
* All pushes carry the session character identity and the `Linear:` trailer is preserved (PAP-46).

**Interface contract**

Provides: `worktree.sh --base`, `.paperos/branch.json` schema, `retarget.ts`, `forge stack`, label `stacked`; consumed by PAP-96 (`BASE_BRANCHES` → `--base`), PAP-92 (playbook step), PAP-93 (`BLOCKED_BY_OPEN` definition of "open"), PAP-89, PAP-527.

Consumes: branch conventions and `worktree.sh` (PAP-46), PR body tool (PAP-49, soft), webhook events (PAP-97, soft), bot identities (PAP-48, soft).

**Definition of done**

* Fixture: PR A open, worktree B created `--base A`, PR B opened on base A; merge A (squash) and within one cron cycle B is retargeted to `main`, rebased with only its own commits, and its checks rerun (transcripts on both forges).
* Conflict fixture labels `needs-rebase`; `bats` for `worktree.sh --base`; `docs/engineering/branch-policy.md` stacked section; PAP-96 comment; CHANGELOG; Linear comment.

**Test plan**

* Unit: `branch.json` read and write; retarget decision over fixture PR states; rebase-onto computation for squash and merge-commit bases.
* E2E: two-PR stack on the fixture repo, both forges; three-base octopus creation.

**Demo**

Reviewer runs `scripts/worktree.sh new PAP-999 --base forge/PAP-998-api`, commits, opens the PR (base shows PAP-998's branch), merges PAP-998 and watches PAP-999 retarget to `main` with a bot comment. Under 3 minutes.

**Edge cases**

* Base PR closed without merging: dependent labelled `base-abandoned`, Linear comment, no automatic action.
* Base force-pushed after the dependent branched: recorded base tip is stale; rebase uses the merge-base fallback and reports it.
* Three-level stack: retarget cascades one level per event.

**Dependencies**

Hard: PAP-46. Soft: PAP-49, PAP-97, PAP-48, PAP-96. Feeds PAP-527, PAP-92, PAP-93.

**Agent**

Builder: Forge (Platform Engineer); Atlas reviews the playbook step. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/merge-automation` = PAP-527.
