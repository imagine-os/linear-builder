---
identifier: "PAP-365"
title: "Build golden path provisioning: parallel idempotent steps, warm pools for preview slots, databases and mirror repos, `--resume` and per-step time budgets in `paperos create`"
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
blockedBy: ["PAP-15", "PAP-22", "PAP-26", "PAP-503", "PAP-505"]
blocks: ["PAP-429", "PAP-500"]
key: "gp/app-shell/provisioning"
url: "https://linear.app/paperos/issue/PAP-365/build-golden-path-provisioning-parallel-idempotent-steps-warm-pools"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:47.643Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-365: Build golden path provisioning: parallel idempotent steps, warm pools for preview slots, databases and mirror repos, `--resume` and per-step time budgets in `paperos create`

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Provisioning is where the ten minutes go: GitHub, Forgejo, Linear, Pages and Coolify calls run serially in PAP-22 and each can take a minute. This issue turns the step list into a DAG run in parallel with per-step budgets, adds a nightly warm pool so preview slots, databases and mirror repos are claimed rather than created, and makes every step resumable. Target: checkpoint C4 within 60 seconds of C2 and C6 within 60 seconds of C5.

**Scope**

In:

* `packages/cli/src/provision/` with `steps.ts` (each PAP-22 step declared as `{ id, dependsOn, budgetMs, run, verify }`), `runner.ts` (parallel execution, retries with backoff, `create.state.json` persistence per step, `--resume`, `--dry-run` printing the DAG), `pool.ts` (claim and release).
* Warm pool job `ops/pool/warm-pool.ts` run nightly by `.github/workflows/warm-pool.yml` and by `paperos pool fill`: keeps N (default 5) of each resource ready: Coolify preview applications `gp-slot-<n>` pointed at the staging API (PAP-26), Postgres databases `app_slot_<n>` on the VPS with roles and RLS baseline migrations applied (PAP-30, PAP-32), Forgejo mirror repos `imagine-os/slot-<n>` (PAP-47). Pool state in `ops/pool/pool.json` in `paperos-infra`, locked with a Forgejo issue comment as the mutex.
* Claim at C4: rename the slot to the app name, write secrets, point the mirror at the new GitHub repo; release on `gp-` repo cleanup returns the slot to the pool after a reset.
* Step verification: every step has a `verify()` that checks the external state (repo exists, mirror configured, Pages enabled, Linear project exists) so `--resume` skips by truth, not by the state file alone.
* Budgets: per-step `budgetMs` with the provisioning total capped at 60 s; a step over budget is `warn`; a failed step after three retries is `failed` and stops dependents only.
* Reporting: step timings into `.paperos/golden-path.json` as sub-steps of C4 and C6 when the driver is present; otherwise printed.

Out: new external systems, production databases (PAP-30 owns production), Coolify blue/green, the driver's stage graph (driver issue).

**Spec**

* DAG: `github.repoCheck` and `forgejo.mirror` and `linear.project` and `pages.enable` and `coolify.claim` and `db.claim` are independent after `git.push`; `ci.secrets` depends on `forgejo.mirror` and `db.claim`; `linear.starterIssues` depends on `linear.project`.
* Concurrency limit 6; per-provider limits (Linear 2 concurrent, GitHub 4) to respect rate limits; 429 and `RATELIMITED` handled with the header-driven wait.
* Pool sizing: `pool.json` records `size`, `min`, `claimed[]`, `free[]`; `warm-pool.yml` refills to `size` and alerts (Linear issue in app-shell, label Infra) when `free < min` two nights running.
* Database slots: created with `CREATE DATABASE ... TEMPLATE app_slot_template` where the template has the PAP-32 baseline migrations applied, so a claim is a rename plus role grant under 2 s; app migrations run at first deploy (PAP-26 pre-deploy command).
* Coolify slots: preview applications pre-created from `ops/coolify/preview-slot.json`; claim sets the image repository and env vars and triggers the first deploy; the preview URL follows `pr-<n>.preview.<domain>` (PAP-26) with the slot's stable hostname aliased.
* Mirror slots: empty Forgejo repos with push mirroring pre-authorised; claim renames and sets the GitHub remote (PAP-47 mirror semantics).
* `--dry-run` prints the DAG as a table with budgets and pool availability without external calls beyond reads.

**Interface contract**

Provides: `provision(plan, opts): ProvisionReport`, `claimSlot(kind: 'preview'|'db'|'mirror', appName)`, `releaseSlot(kind, appName)`, the `pool.json` schema and the `warm-pool` workflow; the PAP-22 step list is re-expressed as `steps.ts` without changing its external behaviour. Consumes: PAP-22 clients (`GitHubClient`, `ForgejoClient`, `LinearClient`), Coolify preview definitions and deploy webhook (PAP-26), Pages repo settings checklist (PAP-15), Postgres provisioning (PAP-30) and baseline migrations (PAP-32), mirror configuration (PAP-47), bot accounts (PAP-48) for the pool job. Consumed by: golden path driver, golden path acceptance test, PAP-29, forge cleanup runbook (PAP-273).

**Test plan**

* Unit: DAG scheduler with fake steps (parallelism, dependents stop on failure, budgets); `verify()`-driven resume skips completed real state even when the state file is deleted.
* Pool: claim and release round trip against the fakes; `free < min` alert path; mutex contention test with two concurrent claimers (second waits, both succeed with distinct slots).
* Integration: one real claim of each slot kind in the staging environment recorded in CI logs with timings; total C2 to C4 under 60 s warm.
* Rate limit: fake provider returning 429 once; runner waits and succeeds within budget.

**Definition of done**

* `paperos create` provisioning runs through the DAG runner with identical external results to PAP-22 (its tests still pass) and C2 to C4 under 60 s on the CI runner with a warm pool.
* Warm pool workflow live in `paperos-infra`, `pool.json` shows five free slots of each kind, alert path proven once by draining the pool in staging.
* `--dry-run` and `--resume` documented in `docs/cli/create.md`; runbook `docs/runbooks/warm-pool.md` (fill, drain, reclaim leaked slots).
* CHANGELOG; Linear comment with the timing table and pool status.

**Edge cases**

* Pool empty: provisioning falls back to creating the resource live (slower), stamps `warn` with reason `pool-empty`, and the nightly job refills.
* Slot leaked (claimed by a deleted repo): weekly reconcile compares `claimed[]` with existing repos and releases orphans after a reset.
* Two `paperos create` runs claim simultaneously: mutex via Forgejo issue comment with a 30 s lease; on lease expiry the claim is retried once.
* Coolify API down: `coolify.claim` fails after retries, C6 cannot complete; everything else finishes and the report says exactly what to resume.
* Database template drift (new baseline migration merged): the nightly job rebuilds the template and recreates free slots; claimed slots migrate at deploy.
* GitHub repo not pre-provisioned (PAP-22 convention): `github.repoCheck` fails fast at C2 with the exact `gh repo create` command.

**Dependencies**

Hard: PAP-22, PAP-26, PAP-15. Soft: PAP-30, PAP-32, PAP-47, PAP-48, PAP-273. Blocks the golden path acceptance test.

**Agent**

Built by Forge (Platform Engineer, Infra sub-agent); reviewed by Sentinel (security reviewer for the pool secrets) and Atlas for budgets.

**Size**

M: a DAG runner, three slot kinds, one nightly job and a runbook.

**Demo**

`paperos create --dry-run` DAG table, then a real run's C2 to C4 timing table under 60 s and `pool.json` before and after the claim.

*Round 4 critique fix (2026-09-18):* PAP-500 was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it blocks PAP-500.
