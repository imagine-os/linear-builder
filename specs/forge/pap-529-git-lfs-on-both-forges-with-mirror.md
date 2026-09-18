---
identifier: "PAP-529"
title: "Git LFS on both forges with mirror support, large-file and repository-size lint, and the retention policy for screenshot, video and fixture artefacts"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-273", "PAP-520"]
blocks: []
key: "r4/forge/lfs-and-artifacts"
url: "https://linear.app/paperos/issue/PAP-529/git-lfs-on-both-forges-with-mirror-support-large-file-and-repository"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:52.587Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-529: Git LFS on both forges with mirror support, large-file and repository-size lint, and the retention policy for screenshot, video and fixture artefacts

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Gate 3 baselines (PAP-246), video replays (PAP-83), 20 MB Yjs fixtures (PAP-441) and template screenshots all need a home; the round-2 critique noted "LFS still assumed". Without a decision, agents commit binaries into history, mirrors slow down (PAP-47 edge case) and the DR restore grows. This issue turns LFS on properly and sets retention for artefacts that should not live in git at all.

**Scope**

In:

* Forgejo `[lfs]` storage on the PAP-25 object storage bucket (`paperos-lfs`) instead of local disk; GitHub LFS on the mirror; `mirror-all.ts` (PAP-47) sets `lfs: true` per repo and the mirror workflow pushes LFS objects (`git lfs push --all`).
* `.gitattributes` in the template: `*.png`, `*.mp4`, `*.webm`, `fixtures/large/**` tracked by LFS; `scripts/check-large-files.ts` in Gate 1 fails a commit adding a non-LFS file over 1 MB or growing the repo pack by over 20 MB.
* Artefact policy `docs/engineering/artifacts.md`: Gate 3 screenshots and videos are CI artefacts (14-day retention) and the baselines only are LFS; contact sheets link to the artefact store (PAP-248); fixtures over 5 MB go to `fixtures/large/` in LFS.
* Restore path: `restore.sh` (PAP-274) includes the LFS bucket; PAP-53 verifies `git lfs fsck` on a restored repo.

Out: the baselines and reporters (quality), object storage provisioning (PAP-25), MinIO for app files (PAP-37).

**Spec**

* LFS objects mirror both ways within the PAP-47 60 s target for objects under 50 MB; larger objects documented as slower.
* Lint exempts `pnpm-lock.yaml` and generated JSON under 5 MB.
* LFS bandwidth on GitHub is capped; the mirror uses Forgejo as the LFS origin for agents (`lfs.url` in `.lfsconfig`).

**Interface contract**

Provides: LFS configuration on both forges, `.gitattributes` and `.lfsconfig` in the template, `check-large-files.ts`, the artefact retention policy; consumed by PAP-246 (baselines), PAP-83, PAP-248, PAP-441 (`fixtures/large/`), PAP-47, PAP-53, PAP-274.

Consumes: Forgejo stack and storage (PAP-273), mirror functions (PAP-47), bucket (PAP-25), backups (PAP-274, soft).

**Definition of done**

* A 30 MB fixture committed via LFS appears on both forges with matching OIDs within a minute; `git lfs fsck` clean on a scratch restore.
* Lint fails a fixture PR adding a 2 MB PNG outside LFS; policy doc merged; CHANGELOG; Linear comment.

**Test plan**

* Unit: large-file detector over fixture diffs; pack-growth estimate; `.gitattributes` pattern coverage test.
* E2E: push LFS object to Forgejo, assert on GitHub; restore into scratch and fsck.

**Demo**

Reviewer adds a 10 MB MP4 under `fixtures/large/`, pushes, and sees the LFS pointer on Forgejo and the object on GitHub; adds a 2 MB PNG elsewhere and Gate 1 fails with the LFS hint. Under 2 minutes.

**Edge cases**

* Agent without `git lfs` installed: `worktree.sh` (PAP-46) checks and prints the install command.
* LFS bucket credentials rotated: Forgejo fails loudly; backup alert path (PAP-274).
* History already containing a binary: `git filter-repo` runbook, never rewriting `main` without a Needs Justin note.

**Dependencies**

Hard: PAP-273, PAP-47. Soft: PAP-25, PAP-274, PAP-246, PAP-441.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
