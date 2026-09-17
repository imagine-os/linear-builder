---
identifier: "PAP-47"
title: "Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-45", "PAP-273"]
blocks: ["PAP-22", "PAP-51", "PAP-53", "PAP-455"]
key: "forge/mirror"
url: "https://linear.app/paperos/issue/PAP-47/configure-bidirectional-push-mirroring-between-forgejo-and-the-github"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:02.243Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-47: Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Every imagine-os repository exists on Forgejo too, with commits pushed to either side arriving on the other within a minute, so either forge can be primary and agents never care which is up. Drift is detected automatically and never resolved by force-push.

**Scope**

In:

* Forgejo to GitHub push mirrors; GitHub to Forgejo via a reusable workflow plus a Forgejo Actions cron fallback (PAP-50); `mirror-all.ts` configuring all repos; `mirror-check.ts` drift monitor; a documented conflict rule.

Out: creating repos for new apps (PAP-51), issue and PR metadata (Linear owns issues), wikis, Discussions, Projects.

**Spec**

* `ops/forge/mirror-all.ts` (infra repo, `pnpm tsx`): lists `GET /orgs/imagine-os/repos`; per repo creates the Forgejo twin if missing (visibility copied), sets a push mirror to GitHub with a fine-grained PAT (contents read and write, org-scoped), `interval=10m`, `sync_on_commit=true`; records pairs in `ops/forge/repos.yml`. Idempotent; `--dry-run`; `--only <repo>`.
* `.github/workflows/mirror-to-forgejo.yml` on `push` to any branch or tag: `git push --mirror` excluding `refs/pull/*` using the PAP-48 mirror token (interim `paperos-admin`).
* Fallback: Forgejo Actions cron (PAP-50) fetches from GitHub every 10 minutes when the workflow has not run.
* Loop safety: mirror pushes carry a `paperos-mirror` marker commit message check; Forgejo push mirror ignores pushes whose only change came from GitHub within the last interval.
* `mirror-check.ts` hourly compares heads and tags; divergence opens a Linear issue via PAP-97 (interim: comment on this issue) and never force-pushes.

**Interface contract**

Provides:

* `ops/forge/repos.yml` schema `{ repos: [{ name, githubId, forgejoId, visibility, archived, lfs, mirror: { pushToGithub: boolean, lastSyncAt } }] }` consumed by PAP-51 (registration), PAP-53 (restore manifest), the template-upgrade issue.
* Exported functions `ensureForgejoRepo(name)`, `configurePushMirror(name)`, `checkDrift(name)` moved into `packages/forge-cli/src/mirror.ts` by PAP-51.
* Reusable workflow `imagine-os/paperos-infra/.github/workflows/mirror-to-forgejo.yml@main`.
* Secret names `FORGEJO_MIRROR_TOKEN`, `GITHUB_MIRROR_PAT` in `ops/forge/secrets-manifest.yml`.
* Bypass actor requirement registered in PAP-46 rulesets.

Consumes: Forgejo instance and admin token (PAP-45), bot token (PAP-48, soft), runner cron (PAP-50, soft), alert path (PAP-97, soft).

**Definition of done**

* Every imagine-os repo on Forgejo with identical heads and tags (`mirror-check.ts` zero drift).
* Forgejo to GitHub and GitHub to Forgejo each within 60 s on a test repo (timings in PR).
* Divergence test produces a Linear issue, not a force-push.
* Second `mirror-all.ts` run makes zero writes (asserted on recorded HTTP calls).
* Secrets only in sops; Sentinel confirms minimal scopes; runbook merged; Linear comment with drift output and timings; changelog under Infra.

**Test plan**

* Unit: `mirror-all.ts` against `msw`-recorded GitHub and Forgejo responses: create, skip, rename by id, archived handling; `--dry-run` zero writes.
* Integration: push to Forgejo `main` on `mirror-fixture`, poll GitHub head until equal, record ms; reverse direction likewise.
* Divergence: force different commits on both sides; assert issue created and both heads unchanged.
* Monitor: expired PAT simulated with 401; distinct "credential expired" message.
* Portability: workflow runs unchanged on Forgejo Actions (PAP-50 check).

**Demo**

Reviewer pushes an empty commit to `mirror-fixture` on Forgejo and refreshes the GitHub commits page within a minute, then runs `pnpm tsx ops/forge/mirror-check.ts` and reads the zero-drift table. Under 2 minutes.

**Edge cases**

* Repos over 1 GB or with LFS: LFS flag on; initial sync may exceed a minute.
* Repo renamed on GitHub: detected by id, renamed on Forgejo.
* Archived repo: read-only mirror, push mirror disabled.
* Protected branch rejects mirror push: bypass allowlist in rulesets.
* Forgejo down during GitHub pushes: workflow retries; cron catches up.

**Dependencies**

PAP-45 (hard). Soft: PAP-48, PAP-50, PAP-46, PAP-97. Unblocks PAP-22, PAP-51, PAP-53.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor on tokens; Edge Case Hunter runs divergence).

**Size**

M: two propagation paths and a monitor with timing evidence.
