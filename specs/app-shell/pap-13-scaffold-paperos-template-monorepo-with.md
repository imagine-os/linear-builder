---
identifier: "PAP-13"
title: "Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-15", "PAP-16", "PAP-17", "PAP-18", "PAP-19", "PAP-26", "PAP-27", "PAP-42", "PAP-78", "PAP-255", "PAP-305"]
key: "app-shell/monorepo-scaffold"
url: "https://linear.app/paperos/issue/PAP-13/scaffold-paperos-template-monorepo-with-pnpm-turborepo-strict"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:03.283Z"
---

# PAP-13: Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app

**Goal**

Create the `paperos-template` monorepo that every PaperOS app is cloned from. From a clean checkout, one command builds, typechecks, lints and tests; every later issue drops code into a folder this issue creates. `packages/core` is owned by app-shell: this issue creates its `src/index.ts` barrel and the rule that other projects add sub-folders (`shell/`, `config/`, `pwa/`, `windows/`, `devices/`, `events/`) but never edit the barrel without an app-shell review. The PM Drizzle schema (PAP-100) lives in `packages/pm`, not here.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Contracts §5 (Monorepo package boundaries) fixes the package list, owners and registration points this scaffold creates, and §1 fixes UUIDv7 ids and Zod 4 as the schema language; the sub-folder ownership table in `packages/core/README.md` must match §5.

**Scope**

In:

* pnpm 10 workspaces, Turborepo 2.x pipelines `build`, `dev`, `lint`, `typecheck`, `test`, `clean`; remote cache off.
* `apps/web` (React 19.1, Vite 7, TypeScript 5.9 strict) rendering one placeholder route.
* Wired-but-empty packages `packages/ui`, `packages/core`, `packages/spec`, `packages/views`, `packages/agents`, `packages/config-ts`, `packages/config-biome`, each with `package.json`, `tsconfig.json`, `src/index.ts` and one passing Vitest test.
* README-stub folders `apps/desktop`, `apps/mobile`, `apps/api`, `specs/`, `docs/`, `.claude/` (CLAUDE.md, `agents/`, `skills/`, `rules/`), `ops/compose`, `ops/ci`.
* `.github/workflows/ci.yml` running `pnpm turbo lint typecheck test build` (Gate 1 hand-off to PAP-78).
* Node 22 LTS pinned (`.nvmrc`, `packageManager`, `engine-strict`).

Out: pages, Tauri (PAP-19), router (PAP-16), PWA (PAP-18), tokens, database code.

**Spec**

* Root scripts: `dev`, `build`, `lint`, `lint:fix`, `typecheck`, `test`, `test:watch`, `clean`, `check` (all gates locally).
* `turbo.json`: `build` depends on `^build`; `test` and `typecheck` depend on `^build`; outputs `dist/**`, `.vite/**`; inputs include `tsconfig*.json` and `.env.example`.
* TS: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `moduleResolution: bundler`, alias `@paperos/*` -> `packages/*/src`.
* `apps/web/src/main.tsx` mounts `<App/>`; `App` renders "PaperOS template" and `import.meta.env.VITE_GIT_SHA` (Vite `define`).
* `vite.config.ts`: `@vitejs/plugin-react`, `base: process.env.BASE_PATH ?? '/'`, `build.target: 'es2022'`.
* Vitest 3 workspace at root; React tests use jsdom + Testing Library; `passWithNoTests` per package.
* Biome 2.x: 2-space, single quotes, import sorting, `noImportCycles` on.
* CLAUDE.md: folder map, commands, "never edit generated files", link to `docs/template-guide.md` (PAP-24).
* `.editorconfig`, `.gitignore`, `.gitattributes` (LF), `LICENSE` placeholder, `CHANGELOG.md` with Unreleased.

**Interface contract**

Provides:

* Package names `@paperos/ui`, `@paperos/core`, `@paperos/spec`, `@paperos/views`, `@paperos/agents`; tsconfig presets `@paperos/config-ts/{base,react,node}.json`; Biome preset `@paperos/config-biome`.
* `packages/core/src/index.ts` barrel exporting a `PAPEROS_VERSION` constant; sub-folder ownership table in `packages/core/README.md` (app-shell owns the barrel; data-layer adds `events/`, identity adds `principal.ts`).
* Env vars read at build: `BASE_PATH`, `VITE_GIT_SHA`.
* CI job name `ci / check` that PAP-78 extends; artifact `coverage/`.

Consumes: nothing. Everything downstream imports these names, so renaming any of them is a breaking change requiring an ADR.

**Definition of done**

* Fresh clone: `pnpm i && pnpm check` green in under 3 minutes on a GitHub-hosted runner.
* `pnpm dev` serves `apps/web` on :5173 and hot-reloads an edit in `packages/ui`.
* Every package has one Vitest test; coverage written to `coverage/`.
* CI green on the PR; badge in README.
* `docs/adr/0001-monorepo-stack.md` records versions and rejected alternatives.
* Linear comment with PR, CI run and the Pages URL once PAP-15 merges.

**Test plan**

* Unit: Vitest smoke test per package; a test importing `@paperos/core` from `apps/web` proves the alias.
* Static: `pnpm typecheck` with a deliberate circular import in a fixture branch must fail; `engine-strict` error on Node 20 captured.
* Integration: CI runs `pnpm check` on ubuntu-latest and macos-latest; frozen lockfile enforced.
* Visual: placeholder page screenshots at 320, 768, 1280 and 1920 attached to the PR.
* Timing: CI job duration recorded in the PR; fails the DoD if over 3 minutes.

**Demo**

Reviewer clones the repo, runs `pnpm i && pnpm check && pnpm dev`, opens `http://localhost:5173`, sees "PaperOS template" with the git SHA, edits a string in `packages/ui/src/index.ts` and watches it hot-reload. Under 2 minutes with a warm pnpm store.

**Edge cases**

* Windows contributors: no symlink-dependent scripts; paths via `node:path`.
* Offline pnpm store: lockfile committed, `--frozen-lockfile` in CI.
* Node mismatch prints a clear error through `engines` and `.npmrc`.
* Turbo cache poisoning: config files are declared inputs.
* Package with zero tests must not fail Vitest.

**Dependencies**

None; root of the graph. Unblocks PAP-15, PAP-16, PAP-17, PAP-18, PAP-19, PAP-26, PAP-27, PAP-42, PAP-78.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).

**Size**

M: many files, no unknowns; must be exact because everything else builds on it.
