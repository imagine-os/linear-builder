---
identifier: "PAP-15"
title: "Set up GitHub Pages demo deploy for every app with per-PR preview URLs"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-18"]
key: "app-shell/gh-pages-demo"
url: "https://linear.app/paperos/issue/PAP-15/set-up-github-pages-demo-deploy-for-every-app-with-per-pr-preview-urls"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-15: Set up GitHub Pages demo deploy for every app with per-PR preview URLs

**Goal**

Every merge to `main` and every pull request publishes a static build of `apps/web` to GitHub Pages so reviewers, the vision agent and Justin can open a URL instead of running code. This is the public demo convention of the imagine-os org made automatic.

**Scope**

In:
- Workflow `ops/ci/pages.yml` (symlinked from `.github/workflows/`) that builds `apps/web` and deploys with `actions/deploy-pages`.
- Production URL `https://imagine-os.github.io/<repo>/` from `main`.
- Per-PR preview at `https://imagine-os.github.io/<repo>/pr/<number>/` using a `gh-pages` branch subfolder strategy, cleaned up on PR close.
- Sticky PR comment containing the preview URL, build SHA and Lighthouse summary placeholder.
- Correct `base` path handling and SPA fallback (`404.html` copying `index.html`).

Out: Storybook deploy (`design-system/storybook`), Vercel, custom domains, server-side rendering.

**Spec**

- Two workflows: `pages-main.yml` (trigger `push: main`) uses the official Pages artifact flow; `pages-preview.yml` (trigger `pull_request: [opened, synchronize, reopened, closed]`) pushes to the `gh-pages` branch under `pr/<n>/` using `peaceiris/actions-gh-pages@v4` with `destination_dir` and `keep_files: true`; on `closed` it deletes the folder.
- Because the two flows conflict, `main` also deploys through the `gh-pages` branch root rather than the artifact flow; Pages source set to `gh-pages` branch, `/` folder. Document this in `ops/ci/README.md`.
- Build with `BASE_PATH=/<repo>/pr/<n>/ pnpm --filter web build` (env var read in `vite.config.ts` from `app-shell/monorepo-scaffold`).
- Inject `VITE_GIT_SHA`, `VITE_BUILD_TIME`, `VITE_PR_NUMBER` and render them in a footer badge component `<BuildInfo />` in `packages/ui`.
- Sticky comment via `marocchino/sticky-pull-request-comment@v2`, body template in `ops/ci/templates/preview-comment.md`.
- Concurrency group per PR so stale builds cancel.
- Add `pnpm demo:url` script printing the URL for the current branch (used by agents to post Linear comments).
- Repo setting checklist (Pages enabled, `gh-pages` branch, Actions permission `pages: write`, `id-token: write`) written for `forge/repo-bootstrap` to automate.

**Definition of done**

- Opening a PR yields a working preview URL within 4 minutes; closing removes the folder.
- Deep link `/<repo>/pr/<n>/some/route` loads the SPA (404 fallback proven).
- `main` demo live and linked from README.
- Playwright smoke test in CI hits the preview URL and asserts `<BuildInfo />` SHA equals the commit SHA.
- Screenshots of the deployed page at 375, 1024 and 1920 px in the PR.
- `ops/ci/README.md` documents flows, permissions and the base-path rule; CHANGELOG entry.
- Linear comment on this issue with both URLs.

**Edge cases**

- Repo name changes break `base`; derive from `github.event.repository.name`, never hard-code.
- Forked PRs lack write token: skip preview with an explanatory comment instead of failing.
- Two PRs merging within a minute race on `gh-pages`: use `force_orphan: false` and retry push once.
- Assets over 100 MB or total site over 1 GB (Pages limit): fail with a clear message; add `size-limit` check.
- Private repo: Pages needs GitHub Pro/Team; document fallback of publishing to a public `-demo` repo.
- Trailing slash missing in URL: Pages redirects; ensure router tolerates both.

**Dependencies**

`app-shell/monorepo-scaffold` (hard: the Vite `base` option and the web build this deploys come from it; it lands within hours, so wait rather than conflict on `vite.config.ts`). Feeds `quality/playwright-matrix`, `quality/review-report`, `forge/repo-bootstrap`, `app-shell/create-cli`.

**Agent**

Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel (Security Auditor for token scopes, Code Reviewer for workflow logic).

**Size**

S: two workflows and a badge component, but the base-path and branch-collision details must be right.
