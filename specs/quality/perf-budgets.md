---
identifier: "PAP-87"
title: "Enforce performance budgets (LCP, INP, bundle size) with Lighthouse CI"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-240", "PAP-78"]
blocks: ["PAP-242"]
key: "quality/perf-budgets"
url: "https://linear.app/paperos/issue/PAP-87/enforce-performance-budgets-lcp-inp-bundle-size-with-lighthouse-ci"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-87: Enforce performance budgets (LCP, INP, bundle size) with Lighthouse CI

**Goal**

Make speed a gate: Lighthouse CI measures LCP, INP proxies, CLS, TBT and PWA installability on key pages of every PR preview, `size-limit` guards JavaScript bundle weight per route, and any regression beyond the budget fails the PR with a diff against `main`.

**Scope**

In:
- `ops/ci/lighthouserc.json` and workflow job `perf` in `.github/workflows/perf.yml` triggered after Gate 1 build, serving `web-dist` with `vite preview` and running `@lhci/cli` 0.15.x on the page list from `quality/playwright-matrix` (`perf: true` in page specs; defaults: `/`, `/_app/dashboard`, `/_app/settings`, `/auth/sign-in`), 3 runs each, mobile and desktop presets.
- Budgets: mobile LCP under 2.5s, TBT under 200ms, CLS under 0.1, performance score at or above 90, accessibility at or above 95, PWA installable (from `app-shell/pwa`); desktop LCP under 1.5s.
- Bundle budgets with `size-limit` 11.x and `@size-limit/file` on `apps/web/dist`: initial JS under 180 KB gzipped, per-route chunk under 120 KB, CSS under 60 KB, `packages/ui` Button import under 6 KB (shared with `design-system/primitives`).
- LHCI server: self-hosted `lhci server` in Docker via Coolify on the VPS with SQLite storage, so trends and comparisons against `main` are stored; token as secret.
- PR sticky comment section "Performance" with a table (metric, main, PR, delta, budget) and links to the LHCI report; status `gate/1-perf` (S1 on budget breach, S0 if performance score drops more than 10 points).
- Runtime web-vitals reporting hook `packages/core/src/perf/vitals.ts` sending `web-vitals` 4.x metrics to the observability endpoint (`data-layer/observability`) so field data exists later.

Out: server response time budgets (observability), load testing, image CDN.

**Spec**

- `lighthouserc.json`: `ci.collect.url` templated from `BASE_URL`, `numberOfRuns: 3`, `settings.preset: 'desktop'` for the desktop run and default mobile with `throttlingMethod: 'simulate'`; `ci.assert.assertions` per budget with `aggregationMethod: 'median-run'`; `ci.upload.target: 'lhci'`.
- Budgets also as `ops/ci/budget.json` (Lighthouse budgets format) for resource counts and sizes per type.
- `size-limit` config in `apps/web/.size-limit.json`; runs `pnpm build` output only (no rebuild); comment produced by `size-limit`'s JSON output merged into our sticky comment rather than a second comment.
- Comparison: script `ops/ci/perf-compare.ts` fetches the latest `main` LHCI run for each URL and computes deltas; if `main` has no baseline yet, comment says so and only absolute budgets apply.
- Tauri and PWA offline shell excluded; PWA category asserted only on `/`.
- Documentation of how to fix common regressions (code splitting with `React.lazy`, image sizing, font preload) in `docs/quality/performance.md`.

**Definition of done**

- Perf job runs on a PR and posts the table with deltas against `main` (link); LHCI server dashboard shows both runs.
- Seeded regression (importing a 300 KB library on the dashboard) fails `size-limit` and drops LCP; gate red (link). Removing it restores green.
- All default pages meet budgets on `main` at the time of merge; numbers in the PR.
- `web-vitals` hook sends metrics in dev to the console and to the observability endpoint when configured.
- `docs/quality/performance.md`; CHANGELOG entry; Linear comment with dashboard link and table screenshot.

**Edge cases**

- Runner CPU variance producing noisy LCP: 3 runs with median, and budgets applied with a 10 percent tolerance band for warnings before failing.
- Pages requiring auth: use Lighthouse `puppeteerScript` (or `extraHeaders` cookie) with the seeded test user storage state.
- Preview served from a subpath (`/pr/<n>/`): use local `vite preview` in CI rather than Pages to avoid CDN variance; Pages measured only informationally on nightly.
- Third-party scripts (analytics) inflating budgets: none allowed without an ADR; flagged by `budget.json` third-party count 0.
- Bundle chunk names change per build: `size-limit` matches by glob and reports per-route via a manifest, not file names.
- LHCI server down: job posts absolute results and marks comparison unavailable; still enforces budgets.

**Dependencies**

`quality/ci-gate1` (hard: artifact and status pattern). Soft: `app-shell/pwa` (installability), `quality/playwright-matrix` (page list and auth state), `data-layer/observability` (vitals sink), `design-system/primitives` (Button budget). Consumed by `quality/release-train`, `quality/review-report`, `libraries/upgrade-bot` (bundle impact of upgrades).

**Agent**

Built by Sentinel with Forge (Ops Runner) deploying the LHCI server. Reviewed by Forge and Iris (which pages matter).

**Size**

S: LHCI and size-limit are mature; the compare script and server deployment are the only custom parts.
