---
identifier: "PAP-754"
title: "Reusable `compose-smoke` workflow: matrix over `ops/compose/**` and `spikes/oss-products/*`, health probes, `docker stats` capture, image cache and 20-minute cap"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: []
key: "r4/libraries/compose-smoke-workflow"
url: "https://linear.app/paperos/issue/PAP-754/reusable-compose-smoke-workflow-matrix-over-opscompose-and-spikesoss"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:52:07.101Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 2
dueDate: "2026-09-24"
cycle: {"number": 1, "name": "C1 Foundation & core systems", "startsAt": "2026-09-18", "endsAt": "2026-09-25"}
---

# PAP-754: Reusable `compose-smoke` workflow: matrix over `ops/compose/**` and `spikes/oss-products/*`, health probes, `docker stats` capture, image cache and 20-minute cap

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Infra S

**Goal**

Seven issues (PAP-214, PAP-215 and their six children) assert that a `compose-smoke` CI job starts every candidate and winner with `docker compose up --wait` and captures `docker stats`. None of them builds the job. Ship the reusable workflow first so the spikes report numbers the same way and the resource budget table (PAP-296) is generated, not typed.

**Scope**

In: `.github/workflows/compose-smoke.yml` (reusable, `workflow_call` and `workflow_dispatch`) discovering compose files under `ops/compose/**` and `spikes/oss-products/*/docker-compose.yml`, running each in its own job with `--wait --wait-timeout 600`, a health probe from a `x-paperos.healthcheck` extension field, `docker stats --no-stream` JSON after a `x-paperos.warmupSeconds` warm-up, optional load script `x-paperos.load`, artefact `compose-smoke/<name>.json`; `scripts/compose-smoke/budget-table.ts` merging artefacts into `docs/adr/backend-resource-budget.md`; Forgejo Actions compatibility (PAP-50). Out: the compose files themselves, production deploys (PAP-26).

**Spec**

* Extension fields documented in `docs/libraries/compose-smoke.md`: `x-paperos: { healthcheck: url, warmupSeconds, load: script, ramBudgetMb, skipCi: reason }`; missing fields default to the first exposed port and 60 s.
* Image cache: `docker/build-push-action` cache and a weekly pull-warm job so a 2 GB image ([Cal.com](<http://Cal.com>), Twenty) does not time out; per-job cap 20 minutes, then `status: timeout` with the log tail.
* Result JSON: `{ name, startedMs, healthy, ramIdleMb, ramLoadedMb, cpuPct, imageSizeMb, status }` validated by a Zod schema shared with PAP-296's budget script.
* Budget table script sums `ramLoadedMb` for files under `ops/compose/` only (winners), prints headroom against the 6 GB budget and fails when over.
* Secrets: compose files read `.env.example` placeholders only; anything needing a real key sets `skipCi` and runs nightly on staging through the credential broker (PAP-300).

**Interface contract**

Provides: reusable workflow, extension field grammar, result schema, budget-table script, `docs/libraries/compose-smoke.md`. Consumes: Gate 1 job slot and setup action (PAP-78), Forgejo runners (PAP-50, soft), VPS profile numbers (PAP-25, soft). Consumed by: PAP-295, PAP-296, PAP-297, PAP-350, PAP-351, PAP-352 (`compose-smoke` in their DoDs), PAP-42 local stack (same extension fields), PAP-253 nightly.

**Definition of done**

* Workflow green on the PAP-42 dev stack compose and on one spike compose; artefacts uploaded; budget table generated from artefacts.
* Timeout path proven with a deliberately broken compose (screenshot); `docs/libraries/compose-smoke.md`; comments on PAP-214 and PAP-215; CHANGELOG entry.

**Test plan**

* Unit: extension field parsing, result schema, budget sum and headroom.
* Integration: workflow run on GitHub and on a Forgejo runner for the same compose file.
* E2E: none.

**Demo**

Dispatch `compose-smoke` on `ops/compose/jobs.yml`, watch the job wait for health, download the JSON and run the budget script to see the table with headroom. Under two minutes after pull.

**Edge cases**

* Compose needs privileged mode or host networking: `skipCi` with reason; measured by hand on staging.
* Two services share a port: jobs run in isolated Docker networks per matrix entry.
* Runner disk full from images: nightly prune step and a 15 GB guard before pulling.

**Dependencies**

None hard (a reusable workflow file; ready on creation). Soft: PAP-78 (job slot and setup action; runs standalone until then), PAP-50, PAP-25, PAP-300, PAP-42. Informs PAP-295, PAP-296, PAP-350, PAP-351, PAP-352 (they run compose by hand if unmerged, then adopt the workflow).

**Agent**

Builder: Forge (Ops Runner) with Scout. Reviewer: Sentinel (Security Auditor for secrets handling).

**Size**

S: half a session.
