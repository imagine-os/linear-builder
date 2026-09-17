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
blockedBy: ["PAP-78", "PAP-240"]
blocks: ["PAP-242"]
key: "quality/perf-budgets"
url: "https://linear.app/paperos/issue/PAP-87/enforce-performance-budgets-lcp-inp-bundle-size-with-lighthouse-ci"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:16.568Z"
---

# PAP-87: Enforce performance budgets (LCP, INP, bundle size) with Lighthouse CI

**Goal**

Make web speed a gate: Lighthouse CI measures LCP, TBT, CLS, performance and accessibility scores and PWA installability on key pages of every PR, `size-limit` guards JavaScript and CSS weight per route, and any regression beyond budget fails the PR with a delta against `main`. Server-side budgets live in PAP-242.

**Scope**

* In: `ops/ci/lighthouserc.json`, `ops/ci/budget.json`, workflow `perf.yml` after Gate 1 serving `web-dist` with `vite preview`, `@lhci/cli` 0.15.x with 3 runs mobile and desktop, self-hosted LHCI server via Coolify, `apps/web/.size-limit.json`, `ops/ci/perf-compare.ts`, "Performance" sticky-comment section, status `gate/1-perf`, `packages/core/src/perf/vitals.ts` runtime hook, docs.
* Out: API and database budgets (PAP-242), load testing, image CDN.

**Spec**

* Pages: `perf: true` in page specs plus defaults `/`, `/_app/dashboard`, `/_app/settings`, `/auth/sign-in`; authenticated pages use PAP-240 storage state through `puppeteerScript`.
* Budgets: mobile LCP under 2.5 s, TBT under 200 ms, CLS under 0.1, performance at or above 90, accessibility at or above 95, PWA installable on `/` (PAP-18); desktop LCP under 1.5 s; 10 percent tolerance band warns before failing; `aggregationMethod: 'median-run'`.
* Bundles: initial JS under 180 KB gzipped, per-route chunk under 120 KB, CSS under 60 KB, `@paperos/ui` Button import under 6 KB (shared with PAP-236); matched by glob and reported per route via the Vite manifest.
* Compare: `perf-compare.ts` fetches the latest `main` run per URL from the LHCI server and computes deltas; no baseline means absolute budgets only with a note; server down means absolute results and "comparison unavailable".
* Output: `reports/perf.json` as `GateReport<'perf'>` (PAP-239) with `data.web: [{ url, preset, lcp, tbt, cls, scores, budget, status }]` and `data.bundles`; PAP-242 adds `data.api` later. Severity S1 on breach, S0 if performance drops more than 10 points.
* Runtime: `web-vitals` 4.x metrics to the PAP-40 endpoint when configured, console in dev.

**Interface contract**

* Provides: `reports/perf.json` web section, status `gate/1-perf`, "Performance" comment section, LHCI server URL, `perf: true` spec key, `.size-limit.json` conventions, `reportVitals()` hook.
* Requires: PAP-78 `web-dist` and comment action (hard), PAP-239 schema, PAP-240 auth state (soft), PAP-18 installability (soft), PAP-40 sink (soft), PAP-25 Coolify for the server.
* Consumers: PAP-242 (extends the artifact and status), PAP-88 certification, PAP-89 section 3, PAP-217 (bundle impact of upgrades), PAP-62 and PAP-63 Lighthouse DoDs.

**Definition of done**

* Perf job posts the table with deltas against `main` (link); LHCI dashboard shows both runs.
* Seeded regression (300 KB library imported on the dashboard) fails `size-limit` and drops LCP; gate red; removal restores green (links).
* All default pages meet budgets on `main` at merge; numbers in the PR.
* `web-vitals` hook logs in dev and posts when configured.
* `docs/quality/performance.md`; changelog entry; Linear comment with dashboard link and table screenshot.

**Test plan**

* Unit: `perf-compare.ts` delta math and missing-baseline path; `perf.json` writer against fixtures; budget tolerance band.
* Workflow: seeded regression PR; LHCI server stopped yields absolute results only.
* Perf: job under 5 minutes; 3-run median variance under 5 percent on `main`.
* Runtime: vitals hook unit test with mocked `web-vitals`.

**Demo**

Open a PR's "Performance" section: four pages with mobile and desktop LCP, deltas and budgets, bundle table per route; click through to the LHCI report and the trend chart. Under one minute.

**Edge cases**

* Runner CPU noise: median of 3, tolerance band.
* Subpath previews: measured on local `vite preview`, Pages only informationally nightly.
* Third-party scripts: none without an ADR; `budget.json` third-party count 0.
* Chunk names change per build: glob plus manifest.

**Dependencies**

PAP-78 (hard). Soft: PAP-239, PAP-240, PAP-18, PAP-40, PAP-25.

**Agent**

Sentinel with Forge (Ops Runner) deploying the LHCI server. Reviewed by Forge and Iris (which pages matter).

**Size**

S.
