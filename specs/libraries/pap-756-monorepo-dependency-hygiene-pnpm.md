---
identifier: "PAP-756"
title: "Monorepo dependency hygiene: pnpm `catalog:` for shared versions, `syncpack` alignment, `pnpm dedupe --check`, `knip` unused dependencies in Gate 1"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-78"]
blocks: []
key: "r4/libraries/dependency-hygiene"
url: "https://linear.app/paperos/issue/PAP-756/monorepo-dependency-hygiene-pnpm-catalog-for-shared-versions-syncpack"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:17.101Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-756: Monorepo dependency hygiene: pnpm `catalog:` for shared versions, `syncpack` alignment, `pnpm dedupe --check`, `knip` unused dependencies in Gate 1

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra M

**Goal**

Twenty parallel sessions running `pnpm add` in twenty packages will produce three versions of `zod`, two of `@tanstack/react-query` and a dozen unused dependencies within a week. PAP-264 mentions a `knip` baseline and PAP-217 keeps versions fresh; nothing keeps them aligned. Adopt pnpm catalogs for shared versions and add the three checks that fail a PR before drift lands.

**Scope**

In: `pnpm-workspace.yaml` `catalog:` (and named catalogs `react19`, `tooling`) for every dependency used by two or more packages, with a codemod moving existing `package.json` entries to `catalog:`; `.syncpackrc` (`versionGroups` mirroring the catalog, `semverGroups: pin`) and `pnpm syncpack lint` in Gate 1; `pnpm dedupe --check`; `knip.json` with the workspace plugins and the PAP-264 baseline, `pnpm knip --production` in Gate 1 with a baseline file and expiry like PAP-115's; Renovate (PAP-217) `pnpm.catalog` support enabled; `docs/libraries/dependency-hygiene.md`. Out: license tiers (PAP-211), vulnerability scanning (PAP-80), the registry (PAP-216).

**Spec**

* Rule: a dependency in two or more workspace packages must come from a catalog (`syncpack` `versionGroups` with `policy: sameRange`); a single-package dependency may pin locally; peer dependency ranges follow the catalog.
* `knip` covers unused dependencies, unused exports of contract packages (reported, not failed, since contracts are APIs) and unresolved imports; `spikes/**` and `generated/**` ignored.
* Baselines: `.knip-baseline.json` and `.syncpack-baseline.json` with `expires` 14 days ahead; growth needs the `dep-baseline` label, matching the PAP-115 pattern.
* Gate 1 step `deps` runs the three checks in under 30 s warm and posts one sticky-comment section with the offending packages and the fix command (`pnpm syncpack fix-mismatches`, `pnpm dedupe`).
* Registry link: `pnpm lib registry build` (PAP-216) reads the catalog as the source of `version` when present, so the registry shows one version per library.

**Interface contract**

Provides: catalogs, `.syncpackrc`, `knip.json`, Gate 1 step `deps`, baselines, codemod `scripts/deps/to-catalog.ts`, docs. Consumes: workspace layout (PAP-13), Gate 1 slot and sticky comment (PAP-78), `knip` baseline (PAP-264), Renovate preset (PAP-217). Consumed by: PAP-216 registry build, PAP-217 grouped upgrades (catalog bumps are one PR), PAP-439 dependency map (fewer duplicate nodes), every session that runs `pnpm add`.

**Definition of done**

* Template migrated to catalogs with zero `syncpack` mismatches; `pnpm dedupe --check` and `knip` clean with a committed baseline; Gate 1 step green on `main` and red on a seeded PR adding a second `zod` range (screenshot).
* `docs/libraries/dependency-hygiene.md` (how to add a dependency); CLAUDE.md gains one line; CHANGELOG entry; comment on PAP-217 about catalog support.

**Test plan**

* Unit: codemod on a fixture workspace; baseline expiry logic.
* Integration: the three checks in CI on both forges; timing under 30 s.
* E2E: none.

**Demo**

Add `zod@^3` to one package while the catalog says `^4`, push, watch the `deps` step fail with the fix command; run `pnpm syncpack fix-mismatches` and see green. Under two minutes.

**Edge cases**

* Library needing two majors during a migration (React 19 and a legacy tool): named catalog per major with an expiry note in the registry.
* Tauri Rust crates: out of scope for syncpack; `cargo deny` bans duplicate crate versions in PAP-211's `deny.toml`.
* Generated `package.json` in `spikes/`: ignored by all three checks.

**Dependencies**

Hard: PAP-13, PAP-78. Soft: PAP-264, PAP-217, PAP-216, PAP-439.

**Agent**

Builder: Scout (Library Evaluator) with Forge (Ops Runner). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
