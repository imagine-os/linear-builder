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
blocks: ["PAP-15", "PAP-16", "PAP-17", "PAP-18", "PAP-19", "PAP-255", "PAP-26", "PAP-27", "PAP-42", "PAP-78"]
key: "app-shell/monorepo-scaffold"
url: "https://linear.app/paperos/issue/PAP-13/scaffold-paperos-template-monorepo-with-pnpm-turborepo-strict"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-13: Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app

**Goal**

Create the `paperos-template` monorepo that every future PaperOS app is cloned from. It must build, typecheck, lint and test from a clean checkout with one command, and every later issue in this plan drops its code into a folder this issue creates.

**Scope**

In:
- Root workspace with pnpm 10 workspaces and Turborepo 2.x pipelines (`build`, `dev`, `lint`, `typecheck`, `test`, `clean`) with remote-cache disabled by default.
- `apps/web` (React 19.1, Vite 7, TypeScript 5.9 strict) rendering a single placeholder route.
- Empty-but-wired packages: `packages/ui`, `packages/core`, `packages/spec`, `packages/views`, `packages/agents`, each with `package.json`, `tsconfig.json`, `src/index.ts`, one passing Vitest test.
- Folders with README stubs: `apps/desktop`, `apps/mobile`, `specs/`, `docs/`, `.claude/` (CLAUDE.md, `agents/`, `skills/`, `rules/`), `ops/` (`compose/`, `ci/`).
- Shared config packages: `packages/config-ts` (base, react, node tsconfigs) and `packages/config-biome` (Biome 2.x formatter + linter, 2-space, single quotes, import sorting).
- `.github/workflows/ci.yml` running `pnpm turbo lint typecheck test build` (Gate 1 hand-off to `quality/ci-gate1`).
- `.nvmrc`/`.node-version` pinned to Node 22 LTS; `packageManager` field pinned.

Out: any real pages, Tauri (`app-shell/tauri-desktop`), router (`app-shell/router-layouts`), PWA, design tokens, database code.

**Spec**

- Root `package.json` scripts: `dev`, `build`, `lint`, `lint:fix`, `typecheck`, `test`, `test:watch`, `clean`, `check` (all gates locally).
- `turbo.json`: `build` depends on `^build`; `test` and `typecheck` depend on `^build`; outputs `dist/**`, `.vite/**`.
- TS options: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `moduleResolution: bundler`, path alias `@paperos/*` -> `packages/*/src`.
- `apps/web/src/main.tsx` mounts `<App />` into `#root`; `App` renders "PaperOS template" and the git SHA from `import.meta.env.VITE_GIT_SHA` (injected by Vite `define`).
- `apps/web/vite.config.ts`: `@vitejs/plugin-react`, `base: process.env.BASE_PATH ?? '/'` (needed by `app-shell/gh-pages-demo`), `build.target: 'es2022'`.
- Vitest 3 workspace file at root so `pnpm test` runs every package; React tests use `jsdom` + Testing Library.
- CLAUDE.md contains: folder map, the commands above, "never edit generated files", link to `docs/template-guide.md` (written in `app-shell/template-docs`).
- `.editorconfig`, `.gitignore`, `.gitattributes` (LF), `LICENSE` placeholder pending `libraries/license-policy`.

**Definition of done**

- Fresh clone: `pnpm i && pnpm check` passes in under 3 minutes on GitHub-hosted runner.
- `pnpm dev` serves `apps/web` on :5173 and hot-reloads a change in `packages/ui`.
- Every package has at least one Vitest test; coverage report generated to `coverage/`.
- CI workflow green on the PR; status badge in README.
- Screenshots of the placeholder page at 320, 768, 1280 and 1920 px attached to the PR.
- `docs/adr/0001-monorepo-stack.md` records pnpm/Turbo/Vite/Biome choices with versions.
- `CHANGELOG.md` created with an Unreleased entry.
- Linear comment with PR link, CI run link and the Pages preview URL once `app-shell/gh-pages-demo` merges.

**Edge cases**

- Windows contributors: no symlink-dependent scripts; paths use `node:path`.
- pnpm store offline: lockfile committed, `--frozen-lockfile` in CI.
- Circular package imports must fail `typecheck` (enable `dpdm` or Biome `noImportCycles`).
- A package with zero tests must not fail Vitest (`passWithNoTests` per package).
- Node version mismatch prints a clear error via `engines` + `engine-strict=true` in `.npmrc`.
- Turbo cache poisoning: `build` inputs include `tsconfig*.json` and `.env.example`.

**Dependencies**

None; this is the root of the graph. Unblocks `app-shell/router-layouts`, `app-shell/env-config`, `app-shell/pwa`, `app-shell/tauri-desktop`, `design-system/tokens`, `data-layer/api-layer`.

**Agent**

Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer sub-agent) with Atlas confirming folder layout matches the repo-template decision.

**Size**

M: many small files and configs, low algorithmic risk, but everything downstream depends on getting conventions right.
