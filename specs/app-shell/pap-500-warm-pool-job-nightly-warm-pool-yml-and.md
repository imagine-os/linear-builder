---
identifier: "PAP-500"
title: "Warm pool job: nightly `warm-pool.yml` and `paperos pool fill|drain|reconcile` keeping preview, database and mirror slots ready with `pool.json` state and a lease mutex"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-15", "PAP-22", "PAP-26", "PAP-30", "PAP-47", "PAP-365", "PAP-503", "PAP-505", "PAP-520"]
blocks: ["PAP-429"]
key: "r4/app-shell/warm-pool-job"
url: "https://linear.app/paperos/issue/PAP-500/warm-pool-job-nightly-warm-poolyml-and-paperos-pool-filldrainreconcile"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:46.558Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-500: Warm pool job: nightly `warm-pool.yml` and `paperos pool fill|drain|reconcile` keeping preview, database and mirror slots ready with `pool.json` state and a lease mutex

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra M

**Goal**

The warm pool is what turns provisioning from minutes into a rename (Golden Path §6). PAP-365 owns the DAG runner and claims; this child owns the resources themselves: the nightly job that keeps five preview applications, five template databases and five mirror repos ready, the state file, the mutex and the reconcile that returns leaked slots.

**Scope**

In:

* `ops/pool/warm-pool.ts` in `paperos-infra` with `fill` (create until `size`), `drain` (release all free), `reconcile` (compare `claimed[]` with live repos, release orphans after reset), `status`; `.github/workflows/warm-pool.yml` nightly 03:30 UTC and `workflow_dispatch`.
* Slot kinds: Coolify preview apps `gp-slot-<n>` from `ops/coolify/preview-slot.json` pointed at the staging API (PAP-26); Postgres `app_slot_<n>` created `TEMPLATE app_slot_template` with baseline migrations (PAP-30, PAP-32) and a per-slot role; Forgejo repos `imagine-os/slot-<n>` with push mirroring pre-authorised (PAP-47).
* `ops/pool/pool.json` schema `{ version, size, min, kinds: { preview|db|mirror: { free: [], claimed: [{ slot, app, claimedAt }] } } }`; lease mutex as a Forgejo issue comment with a 30 s lease and one retry (PAP-365 semantics).
* Alert: when `free < min` two nights running, open a Linear issue in app-shell (label Infra) through the `linear-update` skill; template drift (new baseline migration) rebuilds `app_slot_template` and recreates free db slots.
* Runbook `docs/runbooks/warm-pool.md`: fill, drain, reclaim leaked slots, resize.

Out: the DAG runner, `claimSlot`/`releaseSlot` call sites and budgets (PAP-365), production databases (PAP-30), preview app definition itself (PAP-26).

**Spec**

* Every operation is idempotent and prints `[ok]/[changed]/[skip]` per slot like `forge bootstrap`.
* Database slots never hold tenant data before claim; `reconcile` resets a released slot by `DROP DATABASE` and recreate from template.
* Coolify slot reset clears env vars and points the image back to the placeholder.
* Mirror slot reset deletes all branches except `main` and removes the GitHub remote.
* The job runs under the PAP-48 `bot-forge` identity; secrets from sops (PAP-25).

**Interface contract**

Provides: `pool.json` schema and file, `paperos pool fill|drain|reconcile|status`, `warm-pool.yml`, the slot naming convention; consumed by PAP-365 (`claimSlot`, `releaseSlot`), PAP-429 (pool `free >= 3` precondition), PAP-531 (releases slots of swept repos).

Consumes: Coolify preview definitions and API (PAP-26), Postgres host and roles (PAP-30), baseline migrations (PAP-32), mirror functions (PAP-47), bot identity (PAP-48), sops (PAP-25).

**Definition of done**

* `pool.json` shows five free slots of each kind after the first nightly run; `status` output attached.
* Drain then fill in staging recorded with timings; reconcile releases a deliberately orphaned slot.
* Alert path proven once by draining below `min` for two simulated nights; runbook merged; CHANGELOG; Linear comment.

**Test plan**

* Unit: state transitions free→claimed→free with fakes; reconcile detects an orphan; lease expiry retry.
* Unit: template drift detection compares the migration list hash.
* E2E: staging: real fill of one slot per kind, claim through PAP-365 fakes, release, reset verified (empty db, placeholder image, single branch).

**Demo**

Reviewer runs `paperos pool status` (five free per kind), `paperos pool drain --kind preview --count 1`, watches the Coolify app return to placeholder, then `fill` restores it. Under 2 minutes.

**Edge cases**

* Coolify API down: fill fails for `preview` only, other kinds proceed, job exit code 1 with the kind named.
* Slot claimed by a repo deleted by hand: reconcile releases it after 24 h of no matching repo.
* Two fills overlap (dispatch during nightly): the lease makes the second wait, then it finds nothing to do.

**Dependencies**

Hard: PAP-26, PAP-30, PAP-47. Soft: PAP-32, PAP-48, PAP-25. Parent PAP-365 consumes the pool; PAP-429 asserts its size.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/repo-cleanup` = PAP-531.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-365 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-365 blocks this issue (`blocks` relation).
