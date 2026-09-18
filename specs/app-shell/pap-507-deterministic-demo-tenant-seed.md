---
identifier: "PAP-507"
title: "Deterministic demo tenant seed: `seedDemoTenant(db, appSpec)`, `paperos seed demo --reset`, faker-by-field-type with constraints and the production guard shared by `/__test/seed`"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-55", "PAP-117", "PAP-240", "PAP-361", "PAP-363"]
blocks: ["PAP-364", "PAP-517"]
key: "r4/app-shell/starter-kit-demo-seed"
url: "https://linear.app/paperos/issue/PAP-507/deterministic-demo-tenant-seed-seeddemotenantdb-appspec-paperos-seed"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:46.276Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-507: Deterministic demo tenant seed: `seedDemoTenant(db, appSpec)`, `paperos seed demo --reset`, faker-by-field-type with constraints and the production guard shared by `/__test/seed`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Every gate, drill and preview signs in as `customer@demo.<app>.test` and expects 25 realistic rows per entity. PAP-363 bundles the seed with six starter page specs and the README renderer; the seed is the part Gate 3 and Gate 4 depend on first, so it gets its own half-session and lands before the specs.

**Scope**

In:

* `packages/db/seed/demo-tenant.ts`: `seedDemoTenant(db, app: AppSpec, opts: { reset?: boolean; seed?: string })` creating tenant `demo`, one user per audience with `attributes.demo: true`, 25 records per entity, three comment threads, five audit events, following the PAP-240 fixture shapes.
* Value generators per PAP-164 field type in `packages/db/seed/generators.ts` (`faker` seeded with the app id): unique fields distinct, relations resolved two-pass, dates within 90 days, currency as `Money` minor units, select values from the field options, two-sentence comment bodies without lorem ipsum.
* `paperos seed demo [--reset] [--tenant demo]` CLI and the `/__test/seed` hook (PAP-240) calling the same function; `--reset` truncates only the demo tenant under RLS (PAP-34).
* Production guard: refuses when `PUBLIC_ENV=production` or the tenant is not flagged demo; exit 2 without touching the database.

Out: starter page specs and README renderer (PAP-363), test-mode endpoints themselves (PAP-240), business template packs (PAP-427).

**Spec**

* Writes go through the API when Electric shapes may be subscribed (PAP-36) so sync clients see them; direct SQL only for `--reset`.
* Idempotent: rerun without `--reset` upserts by deterministic ids (UUIDv7 derived from the seed and row index).
* Runtime under 10 s for the three canned apps; measured in the test.
* Demo users sign in by magic link in preview and dev (PAP-57 test mode), never by password.

**Interface contract**

Provides: `seedDemoTenant`, `generators`, `paperos seed demo`, the account convention `<audience>@demo.<app>.test`; consumed by PAP-363 (starter kit), PAP-364 (C6), PAP-505, PAP-82, PAP-85, PAP-240 (hook body), PAP-29.

Consumes: `AppSpec` entities and audiences (PAP-117, PAP-55), fixture shapes and hook (PAP-240), field types (PAP-164, soft; primitives only until it lands), RLS (PAP-34), magic link test mode (PAP-57, soft).

**Definition of done**

* Seed of the clinic fixture yields 25 rows per entity, three threads, five audit events in under 10 s (CI timing); `--reset` leaves other tenants untouched (row counts asserted).
* `PUBLIC_ENV=production` run exits 2 with no writes; CHANGELOG; Linear comment with timings.

**Test plan**

* Unit: generator per field type honours uniqueness, options and date window; deterministic ids across two runs.
* E2E: compose stack: seed, sign in as each demo user by magic link, grid shows 25 rows; `--reset` then counts.

**Demo**

Reviewer runs `paperos seed demo --reset` on the dev stack, opens the app as `staff@demo.clinic.test` and sees 25 appointments with realistic names and dates. Under a minute.

**Edge cases**

* Entity with no fields beyond name: rows still valid; status defaults to the first option.
* App with no customer audience: only staff and owner users are created.
* Relation cycle (A references B references A): second pass fills both; a self-relation gets nulls on 20 percent of rows.

**Dependencies**

Hard: PAP-240, PAP-117. Soft: PAP-164, PAP-34, PAP-57, PAP-36. Parent PAP-363 copies and calls it; PAP-364 runs it at C6.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/pr-preview-environments` = PAP-505.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-363 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-363 blocks this issue (`blocks` relation).
