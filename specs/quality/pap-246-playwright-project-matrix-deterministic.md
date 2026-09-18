---
identifier: "PAP-246"
title: "Playwright project matrix, deterministic fixtures and Storybook story capture"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-82"
children: []
blockedBy: ["PAP-14", "PAP-78", "PAP-678"]
blocks: ["PAP-83", "PAP-247", "PAP-248", "PAP-685", "PAP-890"]
key: "quality/playwright-matrix/projects-fixtures-stories"
url: "https://linear.app/paperos/issue/PAP-246/playwright-project-matrix-deterministic-fixtures-and-storybook-story"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:16.618Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-246: Playwright project matrix, deterministic fixtures and Storybook story capture

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Create the 21-combination visual project matrix from `breakpoints.json`, the determinism fixtures, and the first baselines for every `visual`-tagged Storybook story, which needs no authentication and can therefore ship in P0 ahead of test-mode seeding.

**Scope**

* In: `apps/web/playwright.visual.config.ts` generating projects `xs-320 … 3xl-1920` with viewport, `deviceScaleFactor`, `hasTouch`, `isMobile` from the device matrix; theme fixture setting `data-theme`; determinism fixtures (fixed clock, `animations: 'disabled'`, `reducedMotion`, `caret: 'hide'`, fonts ready, `data-ready` wait, volatile masking); story capture from `storybook-static/index.json`; screenshot ID grammar; Docker image pin; `pnpm shots*` scripts.
* Out: authenticated page capture and baseline workflow (sibling), reporter and sharding (sibling).

**Spec**

* Projects from `ops/ci/breakpoints.json` (PAP-14); 7 widths × 3 themes = 21 project-theme combinations; `toHaveScreenshot` thresholds `maxDiffPixelRatio: 0.002`, `threshold: 0.2`.
* Stories opt in with `tags: ['visual']`; element screenshots of `#storybook-root`; ID `story:<storyId>`.
* Masks: elements with `data-volatile` painted `--pos-color-accent-500`.
* Image `mcr.microsoft.com/playwright:v1.5x-noble` pinned; outside Docker runs print an environment-mismatch warning and are informational.
* Baselines under `apps/web/e2e/visual/__screenshots__/<project>/<theme>/<id>.png` with Git LFS (`.gitattributes` and LFS enabled on both forges).

**Interface contract**

* Provides: `visualTest` fixture (`{ theme, width, seedReady }`), project names as the canonical width keys used by PAP-83, PAP-84, PAP-87; screenshot ID grammar; `pnpm shots`.
* Requires: PAP-14 `breakpoints.json`, PAP-69 `storybook-static`, PAP-78 artifacts; LFS on Forgejo (PAP-45 config).

**Definition of done**

* Storybook stories for PAP-66 tokens and PAP-67 components captured at 21 combinations with baselines committed via LFS.
* 10 consecutive runs on `main` with zero diffs (flake check).
* Seeded 2 px padding change on Button fails with a visible diff image (link).
* `docs/quality/visual-testing.md` sections "Matrix", "Determinism", "Stories".

**Test plan**

* Unit: project generation from JSON snapshot; ID sanitising.
* Integration: determinism run repeated 10 times; mask rendering check.
* Visual: the suite itself.

**Demo**

`pnpm shots --project sm-375 --grep story:ui-button` inside the Docker image, then `pnpm shots:report` to open the HTML report with the 3 theme captures. Under two minutes.

**Edge cases**

* Story renders a portal: capture `body` for stories tagged `visual-portal`.
* Fonts not ready: `document.fonts.ready` awaited with a 5 s cap.
* LFS quota: baselines capped at 600 images with a count check.

**Dependencies**

PAP-78, PAP-14 (hard). Soft: PAP-69. Blocks the two sibling children.

**Agent**

Built by Sentinel (Visual Inspector sub-agent). Reviewed by Forge (LFS, image) and Iris (story tags).

**Size**

M.
