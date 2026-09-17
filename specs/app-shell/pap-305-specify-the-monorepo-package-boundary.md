---
identifier: "PAP-305"
title: "Specify the monorepo package boundary map: package ownership table, allowed dependency graph, `packages/core` sub-folder owners, dependency-cruiser lint in Gate 1 and the `packages/pm` move"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Template scaffolds and runs on web"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-24", "PAP-28", "PAP-100", "PAP-264", "PAP-439"]
key: "contracts/package-boundaries"
url: "https://linear.app/paperos/issue/PAP-305/specify-the-monorepo-package-boundary-map-package-ownership-table"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:22.684Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-305: Specify the monorepo package boundary map: package ownership table, allowed dependency graph, `packages/core` sub-folder owners, dependency-cruiser lint in Gate 1 and the `packages/pm` move

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec P0

**Goal**

Write down who owns which package in `paperos-template` and which imports are allowed, then enforce it with a lint so that twelve issues across six projects can write into `packages/core` without colliding, optional modules cannot reach into each other, and the PM schema that PAP-100 puts in `packages/core/src/pm` lands in `packages/pm` instead. Section 5 of the Interface & Data Contracts document is the prose; this issue makes it machine-checked.

**Scope**

In:

* `ownership.json` at the repo root (the same file PAP-46 uses for CODEOWNERS-style review routing gains a `packages` section): for every `apps/*` and `packages/*` directory and every `packages/core/src/<folder>`: `{ owner: <project key>, issues: [PAP-..], kind: core|runtime|module|tooling, optional: boolean }`.
* `.dependency-cruiser.cjs` rules: (1) `packages/core/**` imports nothing from `packages/*` except `packages/core`; (2) `packages/db` imports only `core`; (3) optional modules (`finance`, `crm`, `pm`, `import`, `views` extensions, `collab` features flagged optional) import only `core`, `db`, `ui`, `spec`, `views`, `sync`, `api-contract`, `permissions`, `jobs`, `files`, `search`, `email` and never another optional module; (4) `apps/*` import packages, never other apps; (5) no imports of `drizzle/*.sql` or generated files; (6) React only in `ui`, `collab`, `views`, `spec` editor, `apps/*`.
* `pnpm lint:deps` script and Gate 1 step (PAP-78) that fails on violations; Biome rule `noRestrictedImports` mirroring rule 3 for fast editor feedback.
* Scaffold `packages/pm/` (package.json, tsconfig, empty schema barrel) and a note in PAP-100 that its schema lands there; `packages/core/src/index.ts` becomes a curated barrel that re-exports sub-folder indexes only.
* `docs/template-guide.md` section "Where code goes" (feeds PAP-24) with a decision table: new entity, new page, new component, new job, new event, new module.

Out: moving existing code (none exists yet beyond PAP-13), the module manifest itself (PAP-264), CI wiring beyond one Gate 1 step, publishing packages (`gp/app-shell/upgrade`, which absorbed the forge template-upgrade gap).

**Spec**

* Owner keys are the seventeen project keys from plan.json; `issues` must reference existing PAP keys (checked against `linear-workspace.json` from PAP-91 when present, else format-only).
* `packages/core` sub-folder owners: `audience` identity (PAP-55), `filter` data-layer (PAP-279), `events` and `types` data-layer (contract issues), `modules` app-shell (PAP-264), `pwa` (PAP-18), `windows` (PAP-21), `native` (PAP-259), `flags` (runtime-flags gap), `i18n` app-shell (PAP-27), `nav` app-shell (PAP-16); anything else in `core` fails the lint until added to `ownership.json`.
* A package may be created only by an issue whose project owns it; the lint checks that every `packages/*` directory has an owner entry.
* Allowed graph is expressed as `allowedDeps: Record<pkg, pkg[]>` in `ownership.json` and the dependency-cruiser config is generated from it (`pnpm gen:deps-rules`) so there is one source of truth.
* Violations print the rule id, the offending import and the owner to ask, for example `R3 packages/finance -> packages/crm: optional modules must couple via @paperos/core/events (owner: growth)`.

**Interface contract**

Provides: `ownership.json` `packages` section schema (Zod in `packages/core/src/modules/ownership.ts`), `pnpm lint:deps`, `pnpm gen:deps-rules`, Gate 1 step `deps`, `packages/pm` scaffold, the "Where code goes" decision table. Consumes: PAP-13 layout (hard), PAP-46 `ownership.json` (shared file; this issue adds a section), PAP-78 Gate 1 (soft; `pnpm check` until it merges), PAP-264 module manifest (soft; `optional` flag mirrors the manifest). Consumed by PAP-24, PAP-28, PAP-100, PAP-264, PAP-22 (`paperos create --without` reads `optional`), every issue that adds a package.

**Test plan**

* Unit: `ownership.json` schema fixtures (unknown owner key, missing package, cyclic `allowedDeps`); rule generation snapshot.
* Integration: a fixture violation (`packages/finance` importing `packages/crm`) fails `pnpm lint:deps` with rule R3 and the owner name; removing it passes; a new `packages/foo` without an entry fails.
* Repo check: every current directory under `packages/` and `packages/core/src/` has an entry (runs in CI).

**Definition of done**

* `ownership.json` covers every existing directory; `pnpm lint:deps` green on `main` and wired into `pnpm check` (Gate 1 when PAP-78 merges).
* Fixture violation test committed; `packages/pm` scaffold merged and PAP-100 carries a comment pointing at it.
* `docs/template-guide.md` section merged; ADR `docs/adr/00xx-package-boundaries.md`; CHANGELOG under "Template"; Linear comment with the lint output screenshot (terminal, 1280).

**Edge cases**

* Type-only imports across optional modules: allowed with `import type` (rule 3 ignores type-only edges) so shared DTOs do not force a package split.
* Test files importing fixtures from another module: allowed under `**/test/**` and `**/*.test.ts`.
* Generated code (`packages/spec` codegen output into `apps/web`): exempt by path glob, listed in the config with the generating issue.
* A package that starts core and becomes optional (or vice versa): change `optional` in `ownership.json`, regenerate, fix violations in the same PR; the lint blocks half-done migrations.
* Storybook and Playwright configs importing across packages: `tooling` kind is exempt from rule 3.

**Dependencies**

PAP-13 (hard: the layout must exist). Soft: PAP-46 for the shared `ownership.json`, PAP-78 for the Gate 1 step, PAP-264 for the `optional` semantics. Blocks PAP-24, PAP-28, PAP-100, PAP-264.

**Agent**

Specified and built by Atlas (Chief Architect) with Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

S

**Demo**

Reviewer adds `import { deals } from '@paperos/crm'` to `packages/finance/src/index.ts`, runs `pnpm lint:deps` and reads the R3 message naming growth as the owner to talk to, reverts, and sees it pass; then opens `docs/template-guide.md` and finds where a new job goes in the decision table. Under a minute.
