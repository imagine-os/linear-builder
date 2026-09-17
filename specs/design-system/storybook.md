---
identifier: "PAP-69"
title: "Set up Storybook with a11y, viewport and interaction-test addons deployed to GitHub Pages"
project: "design-system"
projectName: "Design System"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-238", "PAP-67"]
blocks: ["PAP-73", "PAP-76"]
key: "design-system/storybook"
url: "https://linear.app/paperos/issue/PAP-69/set-up-storybook-with-a11y-viewport-and-interaction-test-addons"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-69: Set up Storybook with a11y, viewport and interaction-test addons deployed to GitHub Pages

**Goal**

Stand up Storybook 9 for `packages/ui` as the living documentation, the accessibility gate for components, and the stable screenshot target the quality pipeline points Playwright at, deployed to GitHub Pages on every merge and per PR.

**Scope**

In:
- Storybook 9.x with `@storybook/react-vite`, addons: `@storybook/addon-a11y`, `@storybook/addon-vitest` (interaction tests in CI through the Vitest browser mode), `@storybook/addon-docs`, viewport addon configured with the seven widths from `ops/ci/breakpoints.json`, theme toolbar switching `data-theme` (light, dark, hc).
- Global decorators: token CSS import, `ThemeProvider`, `ToastProvider`, RTL toggle, container-width decorator.
- `pnpm --filter ui storybook` (dev), `storybook:build` (static to `packages/ui/storybook-static`), `storybook:test` (runs all `play` functions and axe).
- Deploy workflow `ops/ci/storybook.yml` publishing to `https://imagine-os.github.io/<repo>/storybook/` from `main` and `/pr/<n>/storybook/` per PR, reusing the `gh-pages` branch strategy from `app-shell/gh-pages-demo`.
- Story index JSON exported for the screenshot suite (`storybook-static/index.json`).

Out: writing component stories themselves (each component issue), guidelines prose (`design-system/guidelines-docs`), Chromatic or other paid services.

**Spec**

- Config in `packages/ui/.storybook/{main.ts,preview.tsx,manager.ts,vitest.setup.ts}`; stories glob `../src/**/*.stories.@(ts|tsx|mdx)`.
- `preview.tsx` `globalTypes.theme` with toolbar; decorator sets `document.documentElement.dataset.theme`.
- Viewports: `xs 320, sm 375, md 768, lg 1024, xl 1280, 2xl 1536, 3xl 1920` generated at config load from `breakpoints.json`.
- a11y addon set to `element: '#storybook-root'`, rules WCAG 2.2 AA tags, `test: 'error'` so violations fail `storybook:test`.
- Vitest addon: `packages/ui/vitest.config.ts` adds the storybook project using Playwright Chromium provider; CI job `storybook-test` in Gate 1 (`quality/ci-gate1`).
- Story naming convention `Category/Component`, story ids stable (used as screenshot keys by `quality/playwright-matrix`): `ui-button--all-variants`.
- Docs autodocs enabled with `tags: ['autodocs']`; MDX pages for Tokens, Getting started, Contributing.
- Pages deploy: build with `--output-dir storybook-static`, copy into `storybook/` subfolder in the same `gh-pages` push as the web demo; sticky PR comment extended with a Storybook link.

**Definition of done**

- `storybook:build` succeeds under 2 minutes in CI; static site live on Pages from `main` and per PR.
- `storybook:test` runs every story's `play` and axe checks in CI and fails on a seeded violation (prove with a reverted commit).
- Theme and viewport toolbars work; screenshots of the Button docs page at 375 and 1280 in three themes attached.
- `index.json` consumed by a stub script listing all story ids.
- `docs/design/storybook.md` covers writing stories, tags and the deploy; CHANGELOG entry.
- Linear comment with the Storybook URL and the PR preview URL.

**Edge cases**

- Storybook `base` path under `/storybook/` subfolder: set `viteFinal` `base` from `BASE_PATH` env, same rule as the web app.
- Stories that open portals (Dialog, Toast) need `#storybook-root` plus portal container in the a11y scope.
- Vitest browser mode missing Chromium on Forgejo runners: install via `pnpm exec playwright install --with-deps chromium` in the runner image (`forge/actions-runner`).
- Flaky `play` timing: use `waitFor` and `findBy*`, never fixed sleeps; flakes go through `quality/flake-quarantine`.
- Large story count slows build: enable `storyStoreV7` lazy compilation and `build.test` mode for CI.
- PR from a fork: skip Pages deploy with comment, same as the demo workflow.

**Dependencies**

`design-system/primitives` (at least Button merged to have stories). Soft: `app-shell/gh-pages-demo` (branch strategy), `quality/ci-gate1` (job slot), `ops/ci/breakpoints.json` from `app-shell/device-matrix-research`. Consumed by `quality/playwright-matrix`, `design-system/a11y-audit`, `design-system/guidelines-docs`.

**Agent**

Built by Iris with Forge (Ops Runner) on the deploy workflow. Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: configuration heavy, and the Pages subfolder plus Vitest browser mode need care on self-hosted runners.
