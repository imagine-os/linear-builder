---
identifier: "PAP-78"
title: "Set up CI gate 1: typecheck, Biome lint, Vitest unit tests and web build on every PR"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-80", "PAP-81", "PAP-82", "PAP-87", "PAP-122", "PAP-217", "PAP-243", "PAP-246"]
key: "quality/ci-gate1"
url: "https://linear.app/paperos/issue/PAP-78/set-up-ci-gate-1-typecheck-biome-lint-vitest-unit-tests-and-web-build"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:10.625Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-78: Set up CI gate 1: typecheck, Biome lint, Vitest unit tests and web build on every PR

**Goal**

Make Gate 1 the fast, deterministic check every PR in every imagine-os repo passes before any agent looks at it: typecheck, Biome lint and format, Vitest, commitlint, generated-file drift and a production web build, under three minutes warm, with a machine-readable `gate1.json` Gate 2 consumes and a `web-dist` artifact Gate 3 reuses.

**Scope**

* In: `.github/workflows/ci.yml` (Forgejo-compatible) with jobs `setup`, `lint`, `typecheck`, `test`, `build`, `commitlint`, `generated-drift`, aggregating `gate-1`; Turborepo remote cache on the VPS; Vitest coverage and JUnit; drift checks; required checks via PAP-46; `pnpm check` and `lefthook` pre-push; job summary and `reports/gate1.json`; the shared sticky-comment action other gates reuse.
* Out: security scans (PAP-80), Playwright (PAP-82), Lighthouse (PAP-87), release automation (PAP-88).

**Spec**

* Runner `ubuntu-24.04`, Node 22 from `.nvmrc`, pnpm via corepack, store cached on lockfile hash; Turbo cache via `TURBO_API/TOKEN/TEAM` against `ducktors/turborepo-remote-cache` deployed by Coolify; `--filter=...[origin/main]` for affected packages; concurrency group `ci-${{ github.ref }}` with cancel-in-progress.
* `commitlint` validates non-merge commits (last 50) and the PR title against `@commitlint/config-conventional` plus the `Linear:` and `Character:` trailer rule from PAP-46.
* `test`: `pnpm turbo test -- --reporter=default --reporter=junit --outputFile=reports/junit.xml`, coverage floor `lines: 70` per package, `retry: 1` in CI with retried tests written to `reports/flakes-delta.json` (PAP-90 format), failures annotated as `::error file=… line=…`.
* `build`: `pnpm turbo build --filter=web...`, uploads `apps/web/dist` as `web-dist`.
* `generated-drift`: `tokens:build`, `registry:build`, `gen:breakpoints`, `contracts:build`, `versions.json` check, then `git diff --exit-code`.
* `gate-1` runs `if: always()`, writes `reports/gate1.json` as `GateReport<'gate1'>` from `packages/contracts` (PAP-239) with `data: { jobs: [{ name, status, durationMs }], failures: [{ job, file, line, message }] }`, sets status `gate/1-static`, fails if any required job failed.
* Path filters: docs-only changes skip `build` and `test`. Env `TZ=UTC`, `LANG=en_US.UTF-8`. `timeout-minutes: 10` per job; soft alarm comment above 3 minutes total.

**Interface contract**

* Provides: artifact `web-dist`; `reports/gate1.json`; status `gate/1-static`; composite action `ops/ci/actions/sticky-comment` (one PR comment with named sections, used by PAP-80, PAP-82, PAP-83, PAP-84, PAP-85, PAP-87); composite `ops/ci/actions/setup` (pnpm, Turbo, Playwright cache); `workflow_run` completion event that PAP-81 and PAP-82 trigger on; `pnpm check`.
* Requires: PAP-13 `ci.yml` skeleton (hard, same file), PAP-46 required checks and trailer rule, PAP-239 artifact schema (soft: write the shape now, import the schema when it lands), PAP-42 service-container workflow (soft), PAP-25 Coolify for the cache server.
* Consumers: PAP-80, PAP-81, PAP-82, PAP-87, PAP-122, PAP-217, PAP-64, PAP-73.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. Also §5 and §6 row "Package boundary map and import lint": Gate 1 runs the cross-package import lint once pending contracts issue D lands (soft; Biome `noImportCycles` is the interim).

**Definition of done**

* Green run on a PR touching `packages/ui` under 3 minutes warm and 6 minutes cold; timings in the PR.
* Seeded failures (type error, lint error, failing test, bad commit message, drifted generated file) each produce an inline annotation and a red status; links.
* Turbo cache hit rate visible; cache server deployed and documented in `ops/README.md`.
* Same workflow runs green on the Forgejo runner (link).
* `gate1.json` validates against `packages/contracts`; `docs/quality/gates.md` documents it; changelog entry; Linear comment with green, red and timing links.

**Test plan**

* Workflow: the five seeded failures as separate commits on a sandbox branch; docs-only PR skips build and test; fork PR runs without secrets.
* Unit: `gate1.json` writer against fixtures; JUnit-to-annotation parser.
* Cache: two consecutive runs, second reports hits; cache server unreachable falls back with a warning, not a failure.
* Determinism: `TZ` and `LANG` asserted inside a test.

**Demo**

Open a green PR run: the job summary shows five jobs with durations under 3 minutes and the `web-dist` artifact; then open the seeded red run and click an inline lint annotation. Under one minute.

**Edge cases**

* Lockfile drift: `--frozen-lockfile` fails with a clear message.
* Merge commits in range: skipped by commitlint.
* 200-commit PR: last 50 plus title.
* Cache server down: local cache, warning only.

**Dependencies**

PAP-13 (hard). Soft: PAP-46, PAP-42, PAP-25, PAP-239.

**Agent**

Sentinel with Forge (Ops Runner) deploying the cache server. Reviewed by Forge and Atlas (Merger).

**Size**

M.
