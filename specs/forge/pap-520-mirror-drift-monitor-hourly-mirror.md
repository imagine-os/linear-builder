---
identifier: "PAP-520"
title: "Mirror drift monitor: hourly `mirror-check.ts` comparing heads and tags on both forges, divergence issue through PAP-97, credential-expiry detection and the loop-safety marker test"
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
blockedBy: ["PAP-45", "PAP-47", "PAP-273"]
blocks: ["PAP-22", "PAP-51", "PAP-53", "PAP-455", "PAP-500", "PAP-503", "PAP-525", "PAP-526", "PAP-529", "PAP-531", "PAP-702"]
key: "r4/forge/mirror-drift-monitor"
url: "https://linear.app/paperos/issue/PAP-520/mirror-drift-monitor-hourly-mirror-checkts-comparing-heads-and-tags-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:41.434Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-520: Mirror drift monitor: hourly `mirror-check.ts` comparing heads and tags on both forges, divergence issue through PAP-97, credential-expiry detection and the loop-safety marker test

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-47 configures two propagation paths; the monitor that proves they stay in sync is separable and is what the DR drill (PAP-53) and the weekly re-audit (PAP-306) read. Splitting it means mirroring can go live on day one while the monitor hardens over the week.

**Scope**

In:

* `ops/forge/mirror-check.ts`: for every pair in `repos.yml`, compare `refs/heads/*` and `refs/tags/*` SHAs from both APIs; classify `in-sync`, `lagging` (one side behind by commits on the same line), `diverged` (different commits, no fast-forward), `missing`.
* Actions: `lagging` over 10 minutes triggers the fallback fetch (PAP-50 cron); `diverged` opens a Linear issue through PAP-97 (interim: comment on PAP-47) with both SHAs and the last common ancestor; never force-pushes.
* Credential health: 401 from either API produces a distinct `credential expired` alert naming the secret (`FORGEJO_MIRROR_TOKEN`, `GITHUB_MIRROR_PAT`).
* Loop-safety test: a push carrying the `paperos-mirror` marker must not re-trigger the opposite mirror within the interval; asserted with a fixture repo.
* Output `mirror-status.json` published to the infra repo hourly and read by `forge.mirrorStatus` (PAP-449 port) and PAP-53.

Out: mirror configuration and the workflow path (PAP-47), repo registration (PAP-51).

**Spec**

* Runs as a Forgejo Actions cron hourly (PAP-50) with a GitHub Actions fallback so the monitor itself survives either forge being down.
* Divergence issues are deduplicated by repo and branch marker; resolved automatically when heads match again.
* Runtime under 60 s for 50 repos using the list endpoints, not per-branch calls.

**Interface contract**

Provides: `mirror-check.ts`, `mirror-status.json` schema `{ checkedAt, repos: [{ name, state, lagSeconds, branches: [...] }] }`, alert conventions; consumed by PAP-53, PAP-306, PAP-449 (`MirrorState`), PAP-534 (lag metric).

Consumes: Forgejo API (PAP-273), `repos.yml` and mirror functions (PAP-47), alert path (PAP-97, soft), runner cron (PAP-50, soft).

**Definition of done**

* Zero drift on all repos in the first report; a forced divergence on `mirror-fixture` opens exactly one issue and no force-push happens (transcript).
* Expired PAT simulated: distinct message; `docs/runbooks/mirroring.md` monitor section; CHANGELOG; Linear comment with the report.

**Test plan**

* Unit: classification over fixture ref maps (in-sync, lagging, diverged, missing); dedupe marker; 401 handling.
* E2E: fixture repo: push both sides, assert `diverged` and the issue; reconcile and assert auto-resolution.

**Demo**

Reviewer runs `pnpm tsx ops/forge/mirror-check.ts` and reads the zero-drift table, then force-pushes a fixture branch on one side and sees the divergence row and the Linear comment. Under 2 minutes.

**Edge cases**

* Branch deleted on one side only: `missing` with the side named; mirror deletion propagates by design, so the monitor waits one interval before alerting.
* Tag moved (release re-tag): flagged `diverged` for tags with a dedicated message, since tags must be immutable (PAP-52).
* Repo archived: read-only compare, no fallback fetch.

**Dependencies**

Hard: PAP-273. Soft: PAP-97, PAP-50. Sibling: the mirror configuration half of PAP-47.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/forge-observability` = PAP-534.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-47 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-47 blocks this issue (`blocks` relation).
