---
identifier: "PAP-753"
title: "Spike harness kit: `spikes/_kit` with route-per-candidate Vite template, Playwright trace-to-FPS script, bundle analyzer output and the `pnpm spike` runner"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Evaluation process"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: []
key: "r4/libraries/spike-harness-kit"
url: "https://linear.app/paperos/issue/PAP-753/spike-harness-kit-spikes-kit-with-route-per-candidate-vite-template"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:17.578Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-753: Spike harness kit: `spikes/_kit` with route-per-candidate Vite template, Playwright trace-to-FPS script, bundle analyzer output and the `pnpm spike` runner

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Infra S

**Goal**

Five research issues (PAP-212, PAP-292, PAP-293, PAP-294, PAP-127) each describe the same harness: a Vite app with a route per candidate, Playwright traces turned into FPS numbers, `vite build --mode analyze` JSON per route, screenshots at three widths and two themes, and a `pnpm spike <dir> --lib <id>` command. Build it once so every spike measures the same way and Scout compares like with like.

**Scope**

In: `spikes/_kit/` with `createSpikeApp({ candidates })` (Vite 6, React 19, TanStack Router, PAP-66 tokens when present), `playwright.spike.config.ts`, `scripts/trace-fps.ts` (CDP trace to mean and p5 FPS), `scripts/bundle.ts` (rollup-plugin-visualizer JSON to `results/<lib>.bundle.json`), `scripts/shots.ts` (375, 1024, 1920, light and dark, axe), `results.schema.json` (Zod), root script `pnpm spike <dir> [--lib <id>] [--bench|--shots|--dev]`; `spikes/**` excluded from `turbo build`, `knip` and Gate 3; `docs/libraries/spikes.md`. Out: the spikes themselves, scoring (PAP-209 `pnpm lib score` reads `results/`).

**Spec**

* Candidate contract: `spikes/<dir>/candidates/<lib>/{index.tsx,package.json}`; the kit mounts each at `/c/<lib>` and injects the shared fixture data (`fixtures/rows.ts`: 100k rows generator with a fixed seed, 10k-point series, 5k markers).
* `trace-fps.ts` throttles CPU 4x (PAP-292 reference profile), scrolls or pans for 5 s, reads `DrawFrame` events, writes `{ meanFps, p5Fps, longFrames }`; numbers reproducible within 5 percent across three runs or the script reports `unstable`.
* Bundle: per-candidate gzip of the route chunk minus the shared React and router chunk, so libraries are compared on their own weight.
* Results folder shape `results/<lib>.{fps,bundle,axe}.json` plus `results/summary.json` validated by `results.schema.json`; `pnpm lib score --facts-from results/` (PAP-209) consumes it.
* Tauri check helper `scripts/tauri-window.ts` opens a candidate route in a secondary PAP-19 window when the shell exists (PAP-212 portal test).

**Interface contract**

Provides: `@paperos/spike-kit` (private), `pnpm spike`, `results.schema.json`, fixture generators, `docs/libraries/spikes.md`. Consumes: monorepo layout (PAP-13), tokens (PAP-66, soft), Tauri shell (PAP-19, soft), rubric CLI input shape (PAP-209). Consumed by: PAP-212, PAP-292, PAP-293, PAP-294, PAP-127 spikes, PAP-215 children for screenshots, PAP-218 candidates later.

**Definition of done**

* Kit merged with one sample candidate (`spikes/_kit/example`), `pnpm spike _kit/example --bench --shots` produces FPS, bundle and axe JSON plus six screenshots on the CI runner.
* Three consecutive bench runs within 5 percent; `docs/libraries/spikes.md` with the candidate contract; comments on PAP-212, PAP-292, PAP-293 naming the kit; CHANGELOG entry.

**Test plan**

* Unit: results schema, FPS extraction from a recorded trace fixture, bundle subtraction math.
* Integration: full run on the example candidate in CI; `turbo build` ignores `spikes/`.
* E2E: none beyond the kit's own Playwright run.

**Demo**

Run `pnpm spike _kit/example --bench`, read the FPS table, open `results/summary.json`, then `--shots` and view the 1920 dark screenshot. Under two minutes.

**Edge cases**

* Candidate needs a global CSS import: kit allows `styles.css` per candidate and records it as a composability note.
* Library incompatible with React 19: candidate marked `failed: peer` in summary, not a kit error.
* CI runner slower than the reference: FPS normalised by the example candidate's baseline run in the same job.

**Dependencies**

Hard: PAP-13. Soft: PAP-66, PAP-19, PAP-209. Informs PAP-212, PAP-292, PAP-293, PAP-294 (they build inline if the kit is unmerged, then migrate).

**Agent**

Builder: Scout (Library Evaluator) with Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
