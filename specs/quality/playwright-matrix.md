---
identifier: "PAP-82"
title: "Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: ["PAP-246", "PAP-248", "PAP-247"]
blockedBy: ["PAP-14", "PAP-239", "PAP-240", "PAP-78"]
blocks: ["PAP-253", "PAP-83", "PAP-84", "PAP-88"]
key: "quality/playwright-matrix"
url: "https://linear.app/paperos/issue/PAP-82/build-gate-3-playwright-screenshot-suite-across-the-7-width-breakpoint"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-82: Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs

**Goal**

Build Gate 3's screenshot suite: Playwright renders every key page and every Storybook story across the seven-width breakpoint matrix and the three themes, compares against committed baselines, and fails the PR on unexpected visual change while making intended changes a one-command baseline update. These images are also the input for the vision agent.

**Scope**

In:
- `apps/web/e2e/visual/` Playwright 1.5x project set generated from `ops/ci/breakpoints.json`: projects `xs-320, sm-375, md-768, lg-1024, xl-1280, 2xl-1536, 3xl-1920` each with viewport, `deviceScaleFactor`, `hasTouch`, `isMobile` from the device matrix mapping; theme handled via `data-theme` set in a fixture, giving 21 combinations.
- Page list `apps/web/e2e/visual/pages.ts` derived from route files with `staticData.spec` plus `specs/pages/*.spec.yaml` `screenshot: true` flag; Storybook stories from `storybook-static/index.json` filtered by tag `visual`.
- Deterministic rendering: fixed clock (`page.clock.setFixedTime`), seeded data via a `/__test/seed` endpoint or MSW, `animations: 'disabled'`, fonts preloaded, `caret: 'hide'`, `reducedMotion: 'reduce'`, masked dynamic regions via `data-testid="volatile"`.
- Baselines committed under `apps/web/e2e/visual/__screenshots__/<project>/<theme>/<id>.png` with Git LFS; `toHaveScreenshot` thresholds `maxDiffPixelRatio: 0.002`, `threshold: 0.2`.
- Diff report (Playwright HTML report plus a generated contact sheet) uploaded as artifact and to the PR Pages preview under `/pr/<n>/visual/`; sticky PR comment with counts and thumbnails of the top 6 diffs.
- Baseline update flow: label `update-baselines` on the PR triggers a workflow that regenerates and commits baselines with the bot account; direct pushes of baseline changes without the label are flagged.
- Commit status `gate/3-visual`.

Out: video (`quality/video-replays`), vision inspection (`quality/screenshot-annotation`), functional e2e (`quality/e2e-flows`).

**Spec**

- Runs against the `web-dist` artifact from Gate 1 served by `vite preview` and `storybook-static`; no rebuild.
- Playwright config `apps/web/playwright.visual.config.ts`: `fullyParallel`, `workers: 4` in CI, `retries: 1`, reporter `html` + `json` + custom `contact-sheet` reporter (`sharp` composing a grid PNG per page across widths).
- Screenshot ID grammar: `page:<routeId>` or `story:<storyId>`; file names sanitised; total budget under 600 images initially, enforced by a count check so the suite stays under 8 minutes with sharding (`--shard=i/4` across 4 runners).
- Full-page screenshots for pages (`fullPage: true`, capped at 4000px height) and element screenshots for stories (`#storybook-root`).
- Volatile masking: elements with `data-volatile` masked in `--pos-color-accent-500` so masks are visible in diffs.
- `pnpm shots` (local run), `pnpm shots:update` (regenerate), `pnpm shots:report` (open report); Docker image `mcr.microsoft.com/playwright:v1.5x-noble` pinned so local and CI fonts match; local runs outside Docker are informational only.
- Diff artifact JSON `reports/visual.json`: `[{ id, project, theme, status: 'pass'|'diff'|'new'|'missing', diffRatio, paths }]` consumed by the vision agent.
- Stories opt in with `tags: ['visual']`; pages opt out with `screenshot: false` in the spec and a reason.

**Definition of done**

- Suite runs on a PR across 4 shards in under 8 minutes and posts the sticky comment with contact sheets (link).
- Seeded 2px padding change fails the gate with a visible diff; `update-baselines` label workflow commits new baselines and turns the gate green (links to both runs).
- Flake check: 10 consecutive runs on `main` with zero diffs.
- Baselines exist for all example routes and all `visual` stories at 21 combinations; LFS configured and documented.
- `docs/quality/visual-testing.md` explains adding pages, masking, updating; CHANGELOG entry.
- Linear comment with report link and contact sheet images.

**Edge cases**

- Font rendering differences between local and CI: enforce the Docker image; report shows an "environment mismatch" warning if run outside it.
- Lazy-loaded images and skeletons: wait for `networkidle` plus `document.fonts.ready` and a `data-ready` attribute set by the app when initial data is loaded.
- Pages requiring auth: fixture logs in with a seeded test user per audience (`identity/*`), storage state cached per shard.
- Extremely tall pages: capped height with a note; full content covered by scrolling screenshots only for pages flagged `screenshot: fullScroll`.
- Baseline update PR conflicts with another baseline PR: LFS binary conflict resolved by re-running the update workflow after rebase (documented).
- Storybook story ids renamed: old baseline marked `missing`, requires explicit deletion so orphaned images do not accumulate.

**Dependencies**

`quality/ci-gate1` (artifact reuse) and `app-shell/device-matrix-research` (`breakpoints.json`) hard. Soft: `design-system/storybook` (story source), `app-shell/gh-pages-demo` (report hosting), `forge/bot-accounts` (baseline commits), `design-system/theming` (theme attribute). Consumed by `quality/video-replays`, `quality/screenshot-annotation`, `quality/release-train`.

**Agent**

Built by Sentinel (Visual Inspector sub-agent) with Iris consulting on story tagging. Reviewed by Forge (CI and LFS) and Iris.

**Size**

L: 21 render combinations, determinism, sharding, LFS baselines and the update workflow.
