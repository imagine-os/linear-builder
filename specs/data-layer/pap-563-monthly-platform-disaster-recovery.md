---
identifier: "PAP-563"
title: "Monthly platform disaster-recovery drill `ops/dr/platform-drill.sh`: fresh Hetzner host, escrow decrypt, restore Postgres, MinIO, Yjs and orchestrator state, smoke suite, RPO and RTO report"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: "PAP-354"
children: []
blockedBy: ["PAP-30", "PAP-140", "PAP-562"]
blocks: ["PAP-88", "PAP-896", "PAP-903", "PAP-905"]
key: "r4/data-layer/platform-dr-drill"
url: "https://linear.app/paperos/issue/PAP-563/monthly-platform-disaster-recovery-drill-opsdrplatform-drillsh-fresh"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:08.713Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-563: Monthly platform disaster-recovery drill `ops/dr/platform-drill.sh`: fresh Hetzner host, escrow decrypt, restore Postgres, MinIO, Yjs and orchestrator state, smoke suite, RPO and RTO report

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Second half of PAP-354: prove the objectives instead of asserting them. One script rebuilds the whole platform on a throwaway host from backups and escrow only, runs a smoke suite that opens a Yjs document and downloads a file, computes RPO and RTO from what was actually restored, writes the report the release policy requires, and destroys the host. First run before the 2026-09-30 release candidate; then monthly.

**Scope**

In: `ops/dr/platform-drill.sh` with phases 1-10 from PAP-354, `ops/dr/smoke.ts` (reuses PAP-86 flows), report template `docs/runbooks/dr-reports/platform-<date>.md`, RPO/RTO calculators, Forgejo Actions cron `.forgejo/workflows/platform-drill.yml` (first Sunday monthly), Linear report comment through PAP-97, `docs/runbooks/platform-dr.md` RPO/RTO table.

Out: Backup jobs and escrow (sibling), forge DR (PAP-53), Postgres PITR mechanics (PAP-30).

**Spec**

* Phases: create cpx31 from cloud-init; `ops/bootstrap.sh` (PAP-25) at `dr.<domain>`; decrypt escrow (Justin's step the first time, then a drill-only age key held by the orchestrator); restore Postgres to the newest point (PAP-30) and the orchestrator schema; restore MinIO buckets; deploy `apps/api`, `apps/web`, Hocuspocus and Electric from Coolify exports with pinned image digests (PAP-26); smoke; measure; report; destroy unless `--keep`; abort after 6 h.
* Smoke suite: sign in as a seeded user, open a table, open a Yjs doc and see the last edit, download a file, orchestrator `/status`; each step timed.
* RPO = `now - max(latest restored row timestamps)` across `audit_event`, `yjs_updates`, MinIO object mtimes and orchestrator events; RTO = wall clock from phase 1 to smoke green; targets RPO 1 h, RTO 4 h (Postgres alone 30 min).
* Restore uses only images from our own registry (PAP-50) with GitHub blocked, as in PAP-53; field decryption proven with keys restored from escrow (PAP-353).
* Report lists phase timings, targets met or missed, and opens a Linear issue per gap; `dr.drill.completed` event for PAP-88 (a release candidate requires a green drill within 30 days).
* Cost guard: one cpx31 for at most 6 h monthly; the script refuses to create a second host while one is tagged `dr`.

**Interface contract**

Provides: `ops/dr/platform-drill.sh`, `ops/dr/smoke.ts`, report template and directory, event `dr.drill.completed`, runbook RPO/RTO table.

Consumes: Backups and escrow (sibling), bootstrap (PAP-25), PITR (PAP-30), Coolify exports and image digests (PAP-26), Yjs tables (PAP-140), orchestrator schema (PAP-96), smoke flows (PAP-86, soft), Linear comment helper (PAP-97, soft), runner (PAP-50, soft). Consumed by PAP-88/PAP-252 release policy, PAP-219 incident playbook.

**Definition of done**

* One full drill completed with RPO under 1 h and RTO under 4 h; report committed with phase table and screenshots of the restored app at 1280 and the Yjs doc with its last edit.
* Escrow decrypt performed once by Justin (recorded) and once by the drill key; both documented.
* Cron registered; second run scheduled; `dr.drill.completed` consumed by the PAP-88 certification input.
* Runbook; CHANGELOG; Linear comment with the report link.

**Test plan**

* Unit: RPO/RTO calculators on fixture timestamps, report renderer snapshot, phase state machine with `--resume <phase>`.
* E2E: the drill itself against staging backups on a scratch host; a reduced `--phases 4-7` run in CI on a self-hosted runner restoring into containers.

**Demo**

Reviewer opens the latest `platform-<date>.md`, reads RPO and RTO, then runs `ops/dr/platform-drill.sh --phases 7 --target dr.<domain>` to re-run the smoke suite against the kept host. One minute.

**Edge cases**

* Yjs documents with uncompacted updates: restore includes `yjs_updates`; compaction runs on first load and the smoke step waits for it.
* Orchestrator claims in flight at backup time: PAP-96 re-queues `interrupted` sessions; the drill asserts no duplicate PRs were opened.
* Hetzner API quota or region unavailable: fall back to a second location listed in the script; report notes it.
* Drill exceeds 6 h: aborted, host destroyed, report marks RTO missed with the phase reached.

**Dependencies**

Blocked by PAP-562 and PAP-140 (hard). Soft: PAP-25, PAP-26, PAP-30, PAP-50, PAP-53, PAP-86, PAP-97, PAP-301. Blocks PAP-88.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor; Justin performs the escrow decrypt once).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/platform-backups` = PAP-562.
