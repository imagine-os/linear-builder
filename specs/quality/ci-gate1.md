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
blocks: ["PAP-122", "PAP-217", "PAP-243", "PAP-246", "PAP-80", "PAP-81", "PAP-82", "PAP-87"]
key: "quality/ci-gate1"
url: "https://linear.app/paperos/issue/PAP-78/set-up-ci-gate-1-typecheck-biome-lint-vitest-unit-tests-and-web-build"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-78: Set up CI gate 1: typecheck, Biome lint, Vitest unit tests and web build on every PR

**Goal**

Make Gate 1 the fast, deterministic check every pull request in every imagine-os repo passes before any agent or human looks at it: typecheck, Biome lint and format, Vitest unit tests, commit message lint and a production web build, finishing in under three minutes with clear, machine-readable results that Gate 2 can consume.

**Scope**

In:
- `.github/workflows/ci.yml` (readable natively by Forgejo Actions per `forge/actions-runner`) with jobs `setup` (pnpm cache, Turbo cache), `lint`, `typecheck`, `test`, `build`, `commitlint`, `generated-drift`, and an aggregating `gate-1` job that sets the commit status `gate/1-static`.
- Turborepo remote cache on the VPS (`ducktors/turborepo-remote-cache` in Docker via Coolify) keyed by team token stored as a secret; `--filter=...[origin/main]` so only affected packages run.
- Vitest with coverage (`@vitest/coverage-v8`), JUnit reporter to `reports/junit.xml`, and a coverage floor per package in `vitest.config.ts` (`lines: 70` initially).
- Drift checks: `tokens:build`, `registry:build`, `gen:breakpoints` outputs must be committed (`git diff --exit-code`).
- Required status checks configured through `forge/branch-policy`'s `apply-branch-policy.ts`.
- `pnpm check` local equivalent; `lefthook` pre-push runs the quick subset.
- Results summary as a GitHub job summary (Markdown) and `reports/gate1.json` artifact `{ status, durations, failures: [{ job, file, line, message }] }`.

Out: security scans (`quality/security-scans`), Playwright (`quality/playwright-matrix`), Lighthouse (`quality/perf-budgets`), release automation.

**Spec**

- Runner: `ubuntu-24.04`; Node 22 from `.nvmrc`; pnpm via `corepack`; `actions/cache` for the pnpm store keyed on lockfile; Turbo cache via `TURBO_API`, `TURBO_TOKEN`, `TURBO_TEAM` env.
- Concurrency group `ci-${{ github.ref }}` with cancel-in-progress.
- `commitlint` job validates all commits in the PR range against `@commitlint/config-conventional` plus the `Linear:` and `Character:` trailer rule from `forge/branch-policy`; also validates the PR title.
- `test` runs `pnpm turbo test -- --reporter=default --reporter=junit --outputFile=reports/junit.xml`; failures annotated inline using `dorny/test-reporter`-style annotations or a small script parsing JUnit into `::error file=...` lines.
- `build` runs `pnpm turbo build --filter=web...` and uploads `apps/web/dist` as artifact `web-dist` for Gate 3 and the Pages preview to reuse, so the app is built once per PR.
- `gate-1` job runs `if: always()`, collects job outcomes, writes `gate1.json`, posts commit status via `actions/github-script`, and fails if any required job failed.
- Time budget enforced: a `timeout-minutes: 10` per job and a soft alarm when total exceeds 3 minutes (comment on PR, tracked in `quality/flake-quarantine` later).
- Path filters: docs-only changes (`docs/**`, `*.md`) skip `build` and `test` but still run `lint` and `commitlint`.

**Definition of done**

- Green run on a PR touching `packages/ui` completes in under 3 minutes with warm cache; cold cache under 6 minutes; both timings pasted in the PR.
- Seeded failures for each job (type error, lint error, failing test, bad commit message, drifted generated file) each produce an inline annotation and a red `gate/1-static` status; evidence linked.
- Remote cache hit rate visible in Turbo summary; cache server deployed and documented in `ops/README.md`.
- Same workflow file runs on the Forgejo runner (link to run).
- `gate1.json` artifact schema documented in `docs/quality/gates.md`; CHANGELOG entry.
- Linear comment with links to a green run, a red run and timings.

**Edge cases**

- Lockfile changed without `pnpm install` locally: `--frozen-lockfile` fails with a clear message.
- Merge commits in the PR range confuse commitlint: lint only non-merge commits, and also the squash title.
- Turbo remote cache unreachable: fall back to local cache, never fail the build; emit a warning.
- Tests that pass locally but fail in CI due to timezone: CI sets `TZ=UTC` and `LANG=en_US.UTF-8`; tests must set their own TZ when relevant.
- Flaky unit tests: allow `retry: 1` in Vitest CI config and report retried tests to the flake DB.
- PR with 200 commits: commitlint runs on the last 50 plus the title; documented.

**Dependencies**

`app-shell/monorepo-scaffold` (hard: this issue extends the `ci.yml` it creates; starting in parallel would conflict on the same file). `data-layer/local-dev-stack` (soft: reusable service-container workflow for database-backed tests). `forge/branch-policy` (required checks, trailer rule). Consumed by `quality/security-scans`, `quality/review-agents`, `quality/playwright-matrix`, `quality/perf-budgets`, `spec-builder/conformance-tests`, `libraries/upgrade-bot`.

**Agent**

Built by Sentinel with Forge (Ops Runner) deploying the Turbo cache server. Reviewed by Forge and Atlas (Merger) since the gate defines mergeability.

**Size**

M: standard workflow work, but caching, artifact reuse and the 3-minute budget need tuning.
