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
blocks: ["PAP-18", "PAP-365", "PAP-500", "PAP-517", "PAP-794"]
key: "app-shell/gh-pages-demo"
url: "https://linear.app/paperos/issue/PAP-15/set-up-github-pages-demo-deploy-for-every-app-with-per-pr-preview-urls"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:45.770Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-15: Set up GitHub Pages demo deploy for every app with per-PR preview URLs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Every merge to `main` and every pull request publishes a static build of `apps/web` to GitHub Pages so reviewers, the vision agent (PAP-83) and Justin open a URL instead of running code. This is the imagine-os public demo convention made automatic.

**Scope**

In:

* `pages-main.yml` and `pages-preview.yml` in `ops/ci/` (symlinked into `.github/workflows/`).
* Production URL `https://imagine-os.github.io/<repo>/` from `main`; previews at `/pr/<n>/`, removed on close.
* Sticky PR comment with preview URL, SHA and a Lighthouse placeholder.
* SPA fallback (`404.html`), correct `base`.
* `<BuildInfo/>` footer badge in `packages/ui`.

Out: Storybook deploy (PAP-75), custom domains, SSR, the Coolify preview environments (PAP-26).

**Spec**

* Both flows publish to the `gh-pages` branch (root for `main`, `pr/<n>/` for previews) via `peaceiris/actions-gh-pages@v4` with `keep_files: true`; the `closed` event deletes the folder. Pages source is the `gh-pages` branch.
* Build with `BASE_PATH=/<repo>/pr/<n>/ pnpm --filter web build`; inject `VITE_GIT_SHA`, `VITE_BUILD_TIME`, `VITE_PR_NUMBER`.
* Sticky comment via `marocchino/sticky-pull-request-comment@v2`, template `ops/ci/templates/preview-comment.md`.
* Concurrency group per PR cancels stale builds.
* `pnpm demo:url` prints the URL for the current branch (agents paste it into Linear comments).
* `ops/ci/README.md` documents the repo settings checklist and the base-path rule.

**Interface contract**

Provides:

* URL convention `https://imagine-os.github.io/<repo>/` and `/pr/<n>/`, consumed by PAP-82 (screenshot target), PAP-83 (vision review), PAP-89 (review report) and PAP-22 (prints it after create).
* `<BuildInfo/>` component and `import.meta.env.VITE_GIT_SHA|VITE_BUILD_TIME|VITE_PR_NUMBER` typed in `packages/core/src/config/public.ts` (PAP-17 extends the schema).
* Script `pnpm demo:url`.

Consumes: `BASE_PATH` from PAP-13's `vite.config.ts`. PAP-18 must propagate `BASE_PATH` into the PWA manifest scope.

**Definition of done**

* A PR yields a working preview within 4 minutes; closing removes the folder.
* Deep link `/<repo>/pr/<n>/some/route` loads the SPA.
* `main` demo linked from README.
* CI smoke test hits the preview and asserts the `<BuildInfo/>` SHA equals the commit.
* Screenshots at 375, 1024 and 1920; README and CHANGELOG updated; Linear comment with both URLs.

**Test plan**

* Unit: Vitest for `demo:url` URL derivation from `GITHUB_REPOSITORY` and branch or PR number.
* Integration: Playwright job after deploy loads the preview root and a deep link, asserts SHA text and no console errors.
* E2E: open, push twice and close a test PR; verify folder appears, updates, disappears (workflow logs in PR).
* Visual: screenshots at 375, 1024, 1920 of the deployed page.

**Demo**

Reviewer opens the PR, clicks the preview URL in the sticky comment, confirms the SHA in the footer matches the PR head, then navigates to `/pr/<n>/does-not-exist` and sees the SPA not-found page rather than the GitHub 404. Under a minute.

**Edge cases**

* Repo renamed: derive `base` from `github.event.repository.name`.
* Fork PRs lack a write token: skip with an explanatory comment.
* Two PRs deploying within a minute race on `gh-pages`: `force_orphan: false` plus one retry.
* Site over 1 GB or asset over 100 MB: `size-limit` check fails clearly.
* Private repo needs GitHub Pro: document publishing to a public `-demo` repo.

**Dependencies**

PAP-13 (hard: `vite.config.ts` base option). Feeds PAP-18, PAP-22, PAP-51, PAP-82, PAP-83, PAP-89.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer).

**Size**

S: two workflows and a badge component.
