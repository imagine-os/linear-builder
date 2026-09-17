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
blockedBy: ["PAP-67", "PAP-238"]
blocks: ["PAP-73", "PAP-76"]
key: "design-system/storybook"
url: "https://linear.app/paperos/issue/PAP-69/set-up-storybook-with-a11y-viewport-and-interaction-test-addons"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:49.395Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-69: Set up Storybook with a11y, viewport and interaction-test addons deployed to GitHub Pages

**Goal**

Stand up Storybook 9 for `packages/ui` as the living documentation, the component accessibility gate and the stable screenshot target Gate 3 points Playwright at, deployed to GitHub Pages on every merge and per PR.

**Scope**

* In: Storybook 9.x with `@storybook/react-vite`, addons a11y, vitest (interaction tests through Vitest browser mode), docs, viewport (seven widths from `ops/ci/breakpoints.json`), theme toolbar (`data-theme`), RTL toggle, container-width decorator; scripts `storybook`, `storybook:build`, `storybook:test`; deploy workflow `ops/ci/storybook.yml`; `index.json` export.
* Out: writing component stories (each component issue), guidelines prose (PAP-76), paid visual services.

**Spec**

* Config `packages/ui/.storybook/{main.ts,preview.tsx,manager.ts,vitest.setup.ts}`; stories glob `../src/**/*.stories.@(ts|tsx|mdx)`.
* `preview.tsx`: `globalTypes.theme` toolbar setting `document.documentElement.dataset.theme`; decorators import tokens CSS, `ThemeProvider`, `ToastProvider`, RTL, container width.
* Viewports `xs 320, sm 375, md 768, lg 1024, xl 1280, 2xl 1536, 3xl 1920` generated from `breakpoints.json` at config load.
* a11y addon scoped to `#storybook-root` plus the portal container, WCAG 2.2 AA tags, `test: 'error'` so violations fail `storybook:test`.
* Vitest addon: `packages/ui/vitest.config.ts` adds the storybook project with the Playwright Chromium provider; CI job `storybook-test` in Gate 1.
* Story naming `Category/Component`; ids stable and used as screenshot keys (`ui-button--all-variants`); tags `autodocs`, `visual` (opt-in for PAP-246), `proposal` (PAP-77).
* Pages: build to `storybook-static`, copy into `storybook/` in the same `gh-pages` push as PAP-15, `/pr/<n>/storybook/` per PR, sticky PR comment gains a Storybook link; `viteFinal` sets `base` from `BASE_PATH`.

**Interface contract**

* Provides: Storybook URLs (`https://imagine-os.github.io/<repo>/storybook/`, `/pr/<n>/storybook/`), `storybook-static/index.json` (story ids, titles, tags) consumed by PAP-246 and PAP-73, the `visual` and `proposal` tag conventions, the `storybook-test` Gate 1 job, viewport names matching PAP-82 project names.
* Requires: PAP-236 (at least Button) for stories, PAP-14 `breakpoints.json`, PAP-15 branch strategy, PAP-78 job slot, Chromium in the runner image (PAP-50).
* Consumers: PAP-246, PAP-73, PAP-76 embeds, PAP-84 (story ids in findings), PAP-92 playbook.

**Definition of done**

* `storybook:build` under 2 minutes in CI; site live from `main` and per PR.
* `storybook:test` runs every `play` and axe check and fails on a seeded violation (reverted commit as proof).
* Theme and viewport toolbars work; Button docs page screenshots at 375 and 1280 in three themes.
* `index.json` consumed by a stub script listing all story ids.
* `docs/design/storybook.md` (stories, tags, deploy); changelog entry; Linear comment with both URLs.

**Test plan**

* Unit: viewport generation from `breakpoints.json`; base path resolution.
* CI: `storybook-test` on a PR touching `packages/ui`; fork PR skips deploy with a comment.
* Visual: docs page at two widths × three themes.
* Flake: `play` tests use `waitFor` and `findBy*`; three consecutive green runs.

**Demo**

Open the PR preview `/pr/<n>/storybook/`, switch viewport to `sm 375` and theme to `hc`, run the a11y panel on Button, then open `index.json` in a tab. Under one minute.

**Edge cases**

* Portal stories: a11y scope includes the portal container.
* Missing Chromium on Forgejo runners: `pnpm exec playwright install --with-deps chromium` in the runner image.
* Large story count: lazy compilation and `build.test` mode in CI.
* Fork PRs: Pages deploy skipped with comment.

**Dependencies**

PAP-236 (hard). Soft: PAP-14, PAP-15, PAP-78, PAP-50.

**Agent**

Iris with Forge (Ops Runner) on the workflow. Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M.
