---
identifier: "PAP-570"
title: "Ephemeral preview databases: template-cloned per-PR and per-preview-slot databases with a seed profile, migration smoke, TTL teardown, `pnpm db:branch` and the `DATABASE_URL` handoff to the deploy pipeline"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-30", "PAP-32"]
blocks: []
key: "r4/data-layer/preview-databases"
url: "https://linear.app/paperos/issue/PAP-570/ephemeral-preview-databases-template-cloned-per-pr-and-per-preview"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:46.579Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-570: Ephemeral preview databases: template-cloned per-PR and per-preview-slot databases with a seed profile, migration smoke, TTL teardown, `pnpm db:branch` and the `DATABASE_URL` handoff to the deploy pipeline

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra M

**Goal**

Per-PR previews (PAP-26) and the golden-path warm pools (PAP-365) need a database each, and nothing provides one: PAP-42 gives per-worktree databases on a laptop, PAP-30 gives prod and staging. Neon and PlanetScale call this branching; on our own Postgres it is `CREATE DATABASE ... TEMPLATE` from a seeded template, a migration smoke run, and a reaper. It also gives every Claude session a disposable database on staging when Docker is not available.

**Scope**

In: `ops/db/branch/{create,drop,reap}.sh` and `pnpm db:branch create|drop|list|reap`, template databases `tpl_minimal` and `tpl_demo` refreshed nightly from migrations plus seeds, naming `pr_<number>` and `slot_<n>`, registry table `db_branch (name, kind, ref, created_at, expires_at, size_bytes)` in the ops schema, GitHub and Forgejo workflow steps that create on PR open and drop on close, TTL 7 days with a reaper cron, `docs/dev/preview-databases.md`.

Out: The preview app deploy itself (PAP-26), warm-pool orchestration and provisioning steps (PAP-365), local per-worktree databases (PAP-42), data masking of production copies (never used as a template).

**Spec**

* `db:branch create --from tpl_demo --name pr_123` runs `CREATE DATABASE pr_123 TEMPLATE tpl_demo` (under 5 s for a 200 MB template), grants `paperos_app`, `paperos_readonly` and `electric`, creates the Electric publication, runs pending migrations and returns `DATABASE_URL*` values in the PAP-17 names for the preview environment.
* Templates rebuilt nightly by `db:branch refresh-templates` from a clean migrate plus `db:seed --profile minimal|demo`; a template is never a copy of production or staging tenant data.
* Quota: at most 30 branches, 2 GB each; `create` fails with the reaper hint when exceeded; `reap` drops expired branches and any `pr_*` whose PR is closed (checked through the forge API, PAP-276 soft).
* Every branch gets its own PgBouncer pool entry generated from the registry; connections capped at 10 per branch.
* Workflow: PR opened creates, PR synchronised re-runs migrations only, PR closed drops; the preview URL comment (PAP-26) includes the branch name.
* Observability: branch count and total size exported for PAP-40; alert at 25 branches.

**Interface contract**

Provides: Scripts `pnpm db:branch *`, registry table `db_branch`, template databases, workflow steps `db-branch-create|drop`, env handoff contract, docs.

Consumes: Postgres roles and PgBouncer (PAP-30), migrations and seeds (PAP-32), env names (PAP-17), deploy pipeline (PAP-26, soft), forge API for PR state (PAP-276, soft), Grafana (PAP-40, soft). Consumed by PAP-26, PAP-365, PAP-253 nightly staging, Claude sessions without Docker (PAP-42 `remote` mode).

**Definition of done**

* Branch created from `tpl_demo` in under 10 s including migrations; preview app boots against it and the RLS harness passes on the branch (CI transcript).
* PR close drops the branch; reaper drops an expired branch and one with a closed PR; quota refusal tested.
* Templates refreshed nightly for two nights; size and count metrics in Grafana.
* Docs; CHANGELOG; Linear comment with the timing.

**Test plan**

* Unit: name validation and collision, TTL arithmetic, quota check, PgBouncer config rendering, env output shape.
* E2E: workflow run on a test PR: create, deploy preview against it, run `pnpm test:e2e --grep smoke`, close PR, assert drop.

**Demo**

Reviewer opens a draft PR, watches the workflow post the preview URL with `pr_<n>`, connects with `psql` to the branch, closes the PR and runs `pnpm db:branch list` to see it gone. Under two minutes.

**Edge cases**

* Template in use during refresh: build `tpl_demo_next` then rename inside a lock; creates retry for up to 30 s.
* Branch with logical replication slot left by Electric: `drop` terminates connections and drops the slot first.
* PR reopened: branch recreated from the template; data from the previous branch is gone, documented.
* Disk pressure on the 8 GB host: quota plus the PAP-30 disk alert; templates kept small by the `minimal` default.

**Dependencies**

Blocked by PAP-30 and PAP-32 (hard). Soft: PAP-17, PAP-26, PAP-276, PAP-40. Consumed by PAP-26, PAP-365, PAP-253.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
