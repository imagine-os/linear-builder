---
identifier: "PAP-242"
title: "Enforce API and database performance budgets: k6 smoke per release candidate, p95 per procedure, slow-query gate, `apps/api` image size"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Infra"
priority: 3
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-35", "PAP-87", "PAP-269"]
blocks: ["PAP-88", "PAP-253"]
key: "quality/api-perf-budgets"
url: "https://linear.app/paperos/issue/PAP-242/enforce-api-and-database-performance-budgets-k6-smoke-per-release"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:18.859Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-242: Enforce API and database performance budgets: k6 smoke per release candidate, p95 per procedure, slow-query gate, `apps/api` image size

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Give the server the same discipline PAP-87 gives the web bundle: a k6 smoke run against every release candidate with p95 budgets per oRPC procedure, a slow-query gate from Postgres statistics, and an `apps/api` image-size budget, all wired into the release certification so an API regression cannot ship.

**Scope**

* In: `ops/perf/k6/` scenarios generated from the oRPC procedure registry (read-heavy list, detail, mutation, search) with seeded data via test mode, `ops/perf/budgets.yaml` (p95 and error-rate per procedure class), `perf.json` artifact in the contracts shape, slow-query extraction from `pg_stat_statements` on staging after the run, `apps/api` image size check with `dive`-style layer report, nightly trend in the LHCI-style SQLite store or Postgres `qa_perf`, release certification hook.
* Out: full load testing (PAP-147), web budgets (PAP-87), APM dashboards (PAP-40 provides the data).

**Spec**

* k6 1.x scripts read `procedures.json` exported by PAP-35 (`pnpm api:procedures`) and run 3-minute smoke at 20 virtual users against the RC on staging after PAP-88 deploys it; auth via test-mode `login-as`.
* Budgets: `list.*` p95 150 ms, `get.*` 80 ms, `mutate.*` 250 ms, `search.*` 300 ms, error rate under 0.5 percent; overrides per procedure with a reason and expiry.
* Slow queries: after the run, `SELECT ... FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20` compared to `main`'s last run; any query over 200 ms mean or a 50 percent regression is an S1 finding with the normalised SQL.
* Image: `apps/api` image under 250 MB compressed; report of top 10 layers.
* Output: `reports/perf.json` `{ procedures: [{ name, p50, p95, errorRate, budget, status }], slowQueries, image }` plus a Markdown summary posted on the RC PR; status `gate/1-perf` (server section).

**Interface contract**

* Provides: `perf.json` kind in `packages/contracts`, `ops/perf/budgets.yaml` schema, `perfHealth` summary for PAP-89 section 3, certification input `perf` for PAP-88 `certify.ts`.
* Requires: PAP-35 procedure registry, PAP-87 status and comment pattern, test-mode seed and `login-as`, PAP-40 `pg_stat_statements`, PAP-88 RC deploy hook.

**Definition of done**

* Smoke runs against a rehearsal RC and posts the table with budgets (link); `certify.ts` reads the artifact.
* Seeded regression (N+1 in a list procedure) breaches p95 and appears in slow queries; gate red; fix restores green (links).
* Image budget check fails on a seeded 300 MB layer.
* Nightly trend for 3 nights stored; `docs/quality/performance.md` gains a server section; changelog under "Quality".

**Test plan**

* Unit: budget matching, regression math, artifact schema.
* Integration: k6 run against the ephemeral compose stack in CI with reduced VUs (informational on PRs).
* Release: full smoke on staging, blocking.

**Demo**

Run `pnpm perf:smoke --target staging --duration 60s` and open the generated Markdown: procedures with p95 against budget, two slow queries with SQL, image size. Under two minutes.

**Edge cases**

* Staging cold cache: 30-second warm-up excluded from percentiles.
* Procedure added without a budget class: defaults to `mutate.*` budget and warns.
* `pg_stat_statements` disabled: gate posts `unknown` for slow queries, still enforces p95.
* k6 runner network jitter: compare against `main` p95 of the same night, not absolute only.

**Dependencies**

PAP-87, PAP-35 (hard). Soft: PAP-40, PAP-88, test-mode seed issue.

**Agent**

Built by Sentinel with Forge (Ops Runner). Reviewed by Forge and Nova (query realism).

**Size**

S: k6 and `pg_stat_statements` are mature; the budget file and certification hook are small.
