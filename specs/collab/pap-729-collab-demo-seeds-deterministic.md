---
identifier: "PAP-729"
title: "Collab demo seeds: deterministic fixtures for comments, notifications, prompt sessions, docs and changelog registered with `/__test/seed`"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Comments and canvas"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-129", "PAP-240", "PAP-317"]
blocks: ["PAP-135", "PAP-138"]
key: "r4/collab/collab-demo-seeds"
url: "https://linear.app/paperos/issue/PAP-729/collab-demo-seeds-deterministic-fixtures-for-comments-notifications"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:32.673Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-729: Collab demo seeds: deterministic fixtures for comments, notifications, prompt sessions, docs and changelog registered with `/__test/seed`

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Infra S

**Goal**

Six collab specs assume seeded data nobody owns: 50 prompt sessions and a 10k-event session (PAP-135), a 500-doc and 2k-comment corpus (PAP-138), 50 pins on one page (PAP-318), a mention flow between two users (PAP-323), a release with rewritten entries (PAP-133). Ship one deterministic fixture set through PAP-240 so every Gate 3 run, Playwright test and demo starts from the same world.

**Scope**

In: `packages/collab/fixtures/` generators with a fixed seed (`seedrandom`), fixture sets `collab-basic`, `collab-large`, `prompt-log-20-turns`, `prompt-log-10k`, `search-corpus`; registration with `/__test/seed?set=` (PAP-240); JSON snapshots committed for the small sets; `docs/collab/fixtures.md`. Out: production seeds, business data (PAP-240 owns audiences and tenants).

**Spec**

* `collab-basic`: two staff users and one customer from PAP-240's audience users, one commentable sample record, 12 threads (8 open, 4 resolved, 3 `internal`), one thread with a Linear issue id, 15 notifications across five kinds, 3 changelog versions with customer and staff entries, 20 docs frontmatter-valid under `docs/fixtures/` (excluded from production sidebar).
* `collab-large`: 60 threads with 50 pins on the sample page for clustering tests, 300 notifications for the 99+ badge, 2k comments and 500 docs for PAP-138's benchmark (generated, not committed).
* `prompt-log-20-turns`: the NDJSON fixture PAP-107 and PAP-129 name, with two redacted events and one `seq` gap; `prompt-log-10k`: 50 sessions, one with 10k events, deterministic costs from a fixed price epoch.
* Every generator is idempotent per set and tenant; reset removes only fixture rows (tagged `fixture_set` column or metadata key).
* Total seed time under 10 s for the small sets, under 90 s for `collab-large` on the CI runner.

**Interface contract**

Provides: fixture set names above, `seedCollab(set, tenantId)`, committed JSON snapshots, `fixture_set` tagging convention. Consumes: `/__test/seed` registry and audience users (PAP-240), tables from PAP-317, PAP-129, PAP-725, PAP-133 (soft; skipped when absent), docs loader (PAP-128). Consumed by: PAP-135, PAP-138, PAP-318, PAP-323, PAP-133, PAP-137, PAP-477 real-adapter run, Gate 3 (PAP-247).

**Definition of done**

* Sets register and seed on the compose stack; snapshots committed; reset leaves non-fixture rows untouched (test).
* PAP-135 and PAP-138 test plans run against these sets without private seeds; timing table in the Linear comment.
* `docs/collab/fixtures.md`; CHANGELOG entry.

**Test plan**

* Unit: determinism (two runs, equal snapshots), idempotency, reset scope.
* Integration: seed each set on Postgres and assert counts; RLS: fixtures land in the requested tenant only.
* E2E: none; consumed by other suites.

**Demo**

Call `/__test/seed?set=collab-basic`, open the sample record and see 12 threads and 50 pins after `collab-large`; call reset and see them gone. Under one minute.

**Edge cases**

* A dependent table missing (module disabled): the set skips that generator with a listed warning, never fails.
* Seeding twice: no duplicate rows (idempotency keys).
* Fixture docs must never appear in `/_public/docs`: `status: draft` and folder excluded by `_meta.yaml`.

**Dependencies**

Hard: PAP-240, PAP-317, PAP-129. Soft: PAP-725, PAP-133, PAP-128. Blocks PAP-135 and PAP-138 test plans (they may start against the PR branch under the branch-start rule).

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725.
