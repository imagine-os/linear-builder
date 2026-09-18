---
identifier: "PAP-615"
title: "Demo routes /demo/{grid,kanban,calendar,timeline,gantt,gallery,list,form,map,chart,dashboard} with a deterministic 100k-row seed and two demo datasets"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-161", "PAP-337"]
blocks: ["PAP-167", "PAP-168", "PAP-169", "PAP-170", "PAP-173", "PAP-619", "PAP-621"]
key: "r4/tables/demo-pages-and-seed-data"
url: "https://linear.app/paperos/issue/PAP-615/demo-routes"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:16.974Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-615: Demo routes /demo/{grid,kanban,calendar,timeline,gantt,gallery,list,form,map,chart,dashboard} with a deterministic 100k-row seed and two demo datasets

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Every tables spec demos against `/demo/<kind>` and a 100k-row seed, yet no issue owns those routes or the datasets behind them. Ship them once so eleven view issues, Gate 3 screenshots and the golden-path drill all point at the same deterministic data.

**Scope**

In: `apps/web/src/routes/demo/*.tsx` page specs (`specs/pages/demo/*.page.spec.yaml`) rendering `<ViewHost />` per kind; `packages/views/scripts/seed.ts` (`pnpm views:seed --rows 100000 --tenant demo`) using `@faker-js/faker` 9.x with a fixed seed and the per-type `generators.ts` of PAP-507 once it lands (this issue adds the 100k-row views profile); two datasets: custom `projects_tasks` (every field type, self-relation for Gantt, `geo`, status select) and entity `memberships`; `views.json` with one saved view per kind; a `/demo` index page.

Out: view components, marketing demo content, production seeding (PAP-367 onboarding), business template packs (PAP-427).

**Spec**

* Seed is deterministic (`faker.seed(42)`, UUIDv7 from a fixed clock) so screenshots are stable across runs; sizes `--rows 1000` for e2e and `100000` for the bench (PAP-337 `seedViews(n)` becomes a thin wrapper).
* `projects_tasks` fields: title (text), notes (longText), status (select with status groups), priority (select), owner (user), reviewers (multiSelect of users), due (date), start (date), end (date), estimate (number), budget (currency, mixed currencies), done (checkbox), rating, url, email, phone, attachments, parent (relation self, `limitOne`), depends_on (relation self), client (relation to `clients`), client_city (lookup), hours (rollup sum), location (geo), progress (percent), created_at, updated_at.
* Routes are page specs with `access: staff`, `data: { views: [...] }` so PAP-119 and PAP-120 generate them; each page mounts `ViewHost` in full mode with the saved view for that kind and a `DemoBanner` explaining the dataset.
* Reset endpoint `POST /__test/demo/reset` (PAP-240 test mode only) restores the seed in under 20 s for e2e isolation.
* Demo tenant `demo` and users `owner@demo`, `staff@demo`, `viewer@demo` from PAP-58 fixtures; the customer audience sees only `/demo/form` and `/demo/gallery`.

**Interface contract**

Provides: routes `/demo/*`, `pnpm views:seed`, `demoDatasets` fixture module (`projects_tasks`, `clients`), `resetDemo()` test helper, `views.json` saved specs consumed by Gate 3 (PAP-82) and the golden-path drill (PAP-29). Consumes: `ViewHost` (PAP-614, soft: until it lands the route renders `GridView` directly), `records.*` (PAP-613), `registerDataset` and tables (PAP-161), `seedViews` (PAP-337), test mode (PAP-240), tenants and users (PAP-58), page spec codegen (PAP-120, soft).

**Definition of done**

* `pnpm views:seed --rows 100000` completes under 90 s on the compose stack and is idempotent (second run no duplicates).
* All eleven routes render (kinds not yet built show the registry fallback tile) at 375, 1024, 1920 in three themes; screenshots attached; axe clean on the index page.
* Gate 3 config (PAP-82) lists the routes; `docs/views/demo.md`; CHANGELOG; Linear comment on every view issue linking its route.

**Test plan**

* Unit: seed determinism (two runs produce identical row hashes); field coverage assertion (every registered FieldType appears in `projects_tasks`); mixed-currency distribution.
* Integration: `views.query` over the seed returns 100,000 rows in count; `resetDemo()` restores after a deletion; RLS: `viewer@demo` cannot read `clients`.
* E2E: open `/demo`, click each tile, assert the page title and the presence of `ViewHost`; customer session gets `DeniedState` on `/demo/grid`.

**Demo**

Reviewer runs `pnpm views:seed --rows 1000`, opens `/demo`, tours grid and form, then runs the reset endpoint and sees the edited row revert. Under two minutes.

**Edge cases**

* Seed run against a tenant that already has custom data: refuses unless `--force`, never touches non-demo datasets.
* 100k rows on a laptop with 4 GB Postgres: batches of 5,000 with `COPY`, progress bar, resumable.
* A view kind removes an option (schema bump): `views.json` migrated by `migrateViewSpec` on load with a test.

**Dependencies**

PAP-337 (hard, `seedViews` and procedures), PAP-161 (hard). Soft: PAP-614, PAP-613, PAP-507 (shared generators and demo tenant convention), PAP-240, PAP-58, PAP-120. Feeds the demo step of PAP-341 (soft); blocks the demo steps of PAP-167, PAP-168, PAP-169, PAP-170, PAP-173.

**Agent**

Builder: Nova (Views Engineer) with Quill (Page Spec Writer) on the page specs. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/app-shell/starter-kit-demo-seed` = PAP-507, `r4/tables/records-crud-procedures` = PAP-613, `r4/tables/view-renderer-registry-and-host` = PAP-614.
