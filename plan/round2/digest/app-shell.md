# app-shell — Universal App Shell & Repo Template
PHASE P0 prio 1 dependsOn ['design-system', 'data-layer']
SUMMARY: The paperos-template monorepo that runs the same app on web, PWA, Linux/macOS/Windows desktop and iOS/Android with multi-window support.
DESC: Goal: a single template repository that any new PaperOS app is generated from and that ships to every device class from day one. It is a pnpm + Turborepo monorepo with a React 19 + Vite web app, Tauri 2 desktop and mobile targets, an installable PWA, and a file-based router whose layouts are driven by page specs. It owns the responsive breakpoint matrix and a window manager that lets panels detach into separate OS windows across monitors, plus a Linux kiosk mode that launches synced windows on several displays. The `paperos create` CLI clones the template into a pre-provisioned imagine-os repo and wires the Forgejo mirror, CI, GitHub Pages demo and a Linear project. Non-goals: native Swift/Kotlin UI, Electron, or a custom bundler. It consumes the design system, data layer and identity packages and is the host for every other project's UI.
MILESTONES: ['Template scaffolds and runs on web 2026-09-19: Monorepo builds, routes render, Pages demo live', 'Desktop and mobile shells build 2026-09-23: Tauri desktop + mobile targets build from the same bundle', 'Multi-monitor and PWA polish 2026-09-29: Window manager, kiosk mode, offline shell, template guide']


## PAP-13 [P0 Build M prio1 Ready for Claude] Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app
key=app-shell/monorepo-scaffold milestone=Template scaffolds and runs on web agent=Built by Forge (Platform Engineer). Reviewed by Sentinel (Co
blockedBy=[] blocks=['PAP-78', 'PAP-42', 'PAP-27', 'PAP-26', 'PAP-19', 'PAP-18', 'PAP-17', 'PAP-16', 'PAP-15']
GOAL: Create the `paperos-template` monorepo that every future PaperOS app is cloned from. It must build, typecheck, lint and test from a clean checkout with one command, and every later issue in this plan drops its code into a folder this issue creates.
SCOPE: In:

* Root workspace with pnpm 10 workspaces and Turborepo 2.x pipelines (`build`, `dev`, `lint`, `typecheck`, `test`, `clean`) with remote-cache disabled by default.
* `apps/web` (React 19.1, Vite 7, TypeScript 5.9 strict) rendering a single placeholder route.
* Empty-but-wired packages: `packages/ui`, `packages/core`, `packages/spec`, `packages/views`, `packages/agents`, each with `package.json`, `tsconfig.json`, `src/index.ts`, one passing Vitest test.
* Folders with README stubs: `apps/desktop`, `apps/mobile`, `specs/`, `docs/`, `.claude/` (CLAUDE.md, `agents/`, `skills/`, `rules/`), `ops/` (`compose/`, `ci/`).
* Shared config packages: `packages/config-ts` (base, react, node tsconfigs) and `packages/config-biome` (Biome 2.x formatter + linter, 2-space, single quotes, import sorting).
* `.github/workflows/ci.yml` running `pnpm turbo lint typecheck test build` (Gate 1 hand-off to `qu
SPEC(first 1200): * Root `package.json` scripts: `dev`, `build`, `lint`, `lint:fix`, `typecheck`, `test`, `test:watch`, `clean`, `check` (all gates locally).
* `turbo.json`: `build` depends on `^build`; `test` and `typecheck` depend on `^build`; outputs `dist/**`, `.vite/**`.
* TS options: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `moduleResolution: bundler`, path alias `@paperos/*` -> `packages/*/src`.
* `apps/web/src/main.tsx` mounts `<App />` into `#root`; `App` renders "PaperOS template" and the git SHA from `import.meta.env.VITE_GIT_SHA` (injected by Vite `define`).
* `apps/web/vite.config.ts`: `@vitejs/plugin-react`, `base: process.env.BASE_PATH ?? '/'` (needed by `app-shell/gh-pages-demo`), `build.target: 'es2022'`.
* Vitest 3 workspace file at root so `pnpm test` runs every package; React tests use `jsdom` + Testing Library.
* CLAUDE.md contains: folder map, the commands above, "never edit generated files", link to `docs/template-guide.md` (written in `app-shell/template-docs`).
* `.editorconfig`, `.gitignore`, `.gitattributes` (LF), `LICENSE` placeholder pending `libraries/license-policy`.
DOD:
* Fresh clone: `pnpm i && pnpm check` passes in under 3 minutes on GitHub-hosted runner.
* `pnpm dev` serves `apps/web` on :5173 and hot-reloads a change in `packages/ui`.
* Every package has at least one Vitest test; coverage report generated to `coverage/`.
* CI workflow green on the PR; status badge in README.
* Screenshots of the placeholder page at 320, 768, 1280 and 1920 px attached to the PR.
* `docs/adr/0001-monorepo-stack.md` records pnpm/Turbo/Vite/Biome choices with versions.
* `CHANGELOG.md` created with an Unreleased entry.
* Linear comment with PR link, CI run link and the Pages preview URL once `app-shell/gh-pages-demo` merges.
EDGE:
* Windows contributors: no symlink-dependent scripts; paths use `node:path`.
* pnpm store offline: lockfile committed, `--frozen-lockfile` in CI.
* Circular package imports must fail `typecheck` (enable `dpdm` or Biome `noImportCycles`).
* A package with zero tests must not fail Vitest (`passWithNoTests` per package).
* Node version mismatch prints a clear error via `engines` + `engine-strict=true` in `.npmrc`.
* Turbo cache poisoning: `build` inputs include `tsconfig*.json` and `.env.example`.
DEPS: None; this is the root of the graph. Unblocks `app-shell/router-layouts`, `app-shell/env-config`, `app-shell/pwa`, `app-shell/tauri-desktop`, `design-system/tokens`, `data-layer/api-layer`.


## PAP-14 [P0 Research S prio2 Ready for Claude] Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices
key=app-shell/device-matrix-research milestone=Template scaffolds and runs on web agent=Researched by Scout (Library Evaluator sub-agent) with Forge
blockedBy=[] blocks=['PAP-82', 'PAP-21']
GOAL: Decide and document the exact set of device classes, viewport widths, DPRs and input modes PaperOS commits to supporting, and publish the 7-width breakpoint matrix that the quality pipeline (`quality/playwright-matrix`, `quality/video-replays`) screenshots against and that `app-shell/breakpoints-windows` implements.
SCOPE: In:

* Research current market share and viewport data for phone, tablet, laptop, desktop, ultra-wide, TV/kiosk and foldable classes (StatCounter, Steam hardware survey, Apple/Android device lists).
* A machine-readable matrix file consumed by CI and the app.
* A test-device recommendation list (real and emulated) with cost.
* Guidance on container queries vs viewport breakpoints, DPR handling, safe areas and hover/pointer capability queries.

Out: implementing the breakpoints in CSS (that is `app-shell/breakpoints-windows`); designing components.
SPEC(first 1200): * Deliver `packages/core/src/devices/matrix.ts` exporting `BREAKPOINTS` (7 named widths) and `DEVICE_CLASSES`. Recommended starting point to validate or overturn with data: `xs 320`, `sm 375`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536`, `3xl 1920`, with `tv 3840` documented as an optional eighth for kiosk work.
* Each entry: `{ name, minWidth, exampleDevices[], dpr[], pointer: 'coarse'|'fine'|'both', hover: boolean, orientation: 'portrait'|'landscape'|'both', safeArea: boolean }`.
* `ops/ci/breakpoints.json` generated from the TS file (single source of truth, generation script `pnpm gen:breakpoints`) so Playwright projects can read it without importing TS.
* Foldables: document posture (`device-posture` API) and the dual-screen span; recommend treating unfolded as `md`.
* TV/kiosk: 10-foot UI notes, focus ring minimums, 4K at DPR 1 and 2.
* Write `docs/research/device-matrix.md` (1,500-2,500 words) with data sources, the decision, rejected alternatives and a review date (2027-01).
* Provide a Playwright `devices` mapping table: for each width, the `playwright.devices` preset or custom viewport + `deviceScaleFactor` + `hasTouch` + `isMobile`.
* Propose the 3 physical devices worth b
DOD:
* `matrix.ts`, generated `breakpoints.json` and the research doc merged; generation script covered by a Vitest snapshot test.
* ADR `docs/adr/0002-device-matrix.md` records the 7 widths and why.
* Screenshots of the placeholder web app rendered at all 7 widths via a throwaway Playwright script, attached to the PR as proof the matrix is executable.
* `quality/playwright-matrix` owner (Sentinel) has commented approval on the PR.
* CHANGELOG Unreleased entry.
* Linear comment linking the doc on the Pages demo (`/docs/research/device-matrix`) once the docs engine exists, or the raw file URL until then.
EDGE:
* Browser zoom at 125-200 percent changes effective CSS width; document that layouts must be tested at zoom, not only at viewport.
* Split-screen tablets produce widths between named breakpoints; matrix must define behaviour for any width, not just the seven.
* Virtual keyboard shrinking `100vh` on mobile; recommend `100dvh` and `interactive-widget=resizes-content`.
* Notch/safe-area insets on iOS and Android gesture bars.
* Windows display scaling producing fractional DPR (1.25, 1.5).
* Very old kiosks locked to Chromium 90-ish; state minimum browser versions.
DEPS: None. Consumed by `app-shell/breakpoints-windows`, `quality/playwright-matrix`, `quality/video-replays`, `design-system/layout-components`, `input/touch-gestures`, `input/gamepad`.


## PAP-15 [P0 Infra S prio2 Backlog] Set up GitHub Pages demo deploy for every app with per-PR preview URLs
key=app-shell/gh-pages-demo milestone=Template scaffolds and runs on web agent=Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel 
blockedBy=['PAP-13'] blocks=[]
GOAL: Every merge to `main` and every pull request publishes a static build of `apps/web` to GitHub Pages so reviewers, the vision agent and Justin can open a URL instead of running code. This is the public demo convention of the imagine-os org made automatic.
SCOPE: In:

* Workflow `ops/ci/pages.yml` (symlinked from `.github/workflows/`) that builds `apps/web` and deploys with `actions/deploy-pages`.
* Production URL `https://imagine-os.github.io/<repo>/` from `main`.
* Per-PR preview at `https://imagine-os.github.io/<repo>/pr/<number>/` using a `gh-pages` branch subfolder strategy, cleaned up on PR close.
* Sticky PR comment containing the preview URL, build SHA and Lighthouse summary placeholder.
* Correct `base` path handling and SPA fallback (`404.html` copying `index.html`).

Out: Storybook deploy (`design-system/storybook`), Vercel, custom domains, server-side rendering.
SPEC(first 1200): * Two workflows: `pages-main.yml` (trigger `push: main`) uses the official Pages artifact flow; `pages-preview.yml` (trigger `pull_request: [opened, synchronize, reopened, closed]`) pushes to the `gh-pages` branch under `pr/<n>/` using `peaceiris/actions-gh-pages@v4` with `destination_dir` and `keep_files: true`; on `closed` it deletes the folder.
* Because the two flows conflict, `main` also deploys through the `gh-pages` branch root rather than the artifact flow; Pages source set to `gh-pages` branch, `/` folder. Document this in `ops/ci/README.md`.
* Build with `BASE_PATH=/<repo>/pr/<n>/ pnpm --filter web build` (env var read in `vite.config.ts` from `app-shell/monorepo-scaffold`).
* Inject `VITE_GIT_SHA`, `VITE_BUILD_TIME`, `VITE_PR_NUMBER` and render them in a footer badge component `<BuildInfo />` in `packages/ui`.
* Sticky comment via `marocchino/sticky-pull-request-comment@v2`, body template in `ops/ci/templates/preview-comment.md`.
* Concurrency group per PR so stale builds cancel.
* Add `pnpm demo:url` script printing the URL for the current branch (used by agents to post Linear comments).
* Repo setting checklist (Pages enabled, `gh-pages` branch, Actions permission `pag
DOD:
* Opening a PR yields a working preview URL within 4 minutes; closing removes the folder.
* Deep link `/<repo>/pr/<n>/some/route` loads the SPA (404 fallback proven).
* `main` demo live and linked from README.
* Playwright smoke test in CI hits the preview URL and asserts `<BuildInfo />` SHA equals the commit SHA.
* Screenshots of the deployed page at 375, 1024 and 1920 px in the PR.
* `ops/ci/README.md` documents flows, permissions and the base-path rule; CHANGELOG entry.
* Linear comment on this issue with both URLs.
EDGE:
* Repo name changes break `base`; derive from `github.event.repository.name`, never hard-code.
* Forked PRs lack write token: skip preview with an explanatory comment instead of failing.
* Two PRs merging within a minute race on `gh-pages`: use `force_orphan: false` and retry push once.
* Assets over 100 MB or total site over 1 GB (Pages limit): fail with a clear message; add `size-limit` check.
* Private repo: Pages needs GitHub Pro/Team; document fallback of publishing to a public `-demo` repo.
* Trailing slash missing in URL: Pages redirects; ensure router tolerates both.
DEPS: `app-shell/monorepo-scaffold` (hard: the Vite `base` option and the web build this deploys come from it; it lands within hours, so wait rather than conflict on `vite.config.ts`). Feeds `quality/playwright-matrix`, `quality/review-report`, `forge/repo-bootstrap`, `app-shell/create-cli`.


## PAP-16 [P0 Build M prio1 Backlog] Implement file-based router with layout slots (nav, sidebar, inspector, command bar) driven by page specs
key=app-shell/router-layouts milestone=Template scaffolds and runs on web agent=Built by Forge. Reviewed by Sentinel (Code Reviewer) and Qui
blockedBy=['PAP-13'] blocks=['PAP-128', 'PAP-70', 'PAP-63', 'PAP-62', 'PAP-54', 'PAP-24', 'PAP-22']
GOAL: Give every PaperOS app one file-based, fully typed router whose pages are wrapped in a layout with named slots (nav, sidebar, main, inspector, command bar, status bar) and whose slot contents are chosen by the page's `page.spec.yaml`. Agents add a page by adding a spec and a route file; the shell does the rest.
SCOPE: In:

* TanStack Router 1.x with the Vite plugin for file-based route generation in `apps/web/src/routes/`.
* `packages/core/src/shell/` layout engine: `<AppShell>` root layout, `Slot` registry, `useLayout()` hook.
* Spec-to-layout adapter reading the `layout` section of a page spec (schema owned by `spec-builder/schema`; until it lands, use the interim type in `packages/spec/src/interim.ts` and mark TODO).
* Route metadata: title, breadcrumb, required audience (string, enforced later by `identity/rbac-abac`), default slot visibility.
* Not-found, error boundary and pending (suspense) routes.
* Deep-linkable panel state via search params (`?inspector=open&sidebar=collapsed`) validated with Zod 4.

Out: real navigation content, auth guards (identity), multi-window detach (`app-shell/breakpoints-windows`), codegen of route files (`spec-builder/layout-codegen`).
SPEC(first 1200): * Routes: `__root.tsx` renders `<AppShell>`; `_app.tsx` layout route for authenticated area; `_public.tsx` for marketing/auth pages; example pages `index.tsx`, `_app/dashboard.tsx`, `_app/settings/index.tsx`.
* `AppShell` grid: CSS grid areas `nav | sidebar | main | inspector` with `commandbar` overlay and `statusbar` bottom; container-query aware (widths from `app-shell/device-matrix-research`), collapses sidebar under `md` and inspector under `lg` into drawers.
* Slot API: `registerSlot(name, Component, { priority, when })`; pages call `useLayout({ sidebar: <Filters/>, inspector: <Details/> })` or declare in spec `layout.slots.sidebar: FiltersPanel` resolved through a component registry (`design-system/component-spec-mapping`).
* Route file exports `Route = createFileRoute('/_app/dashboard')({ component, loader, validateSearch, staticData: { spec: 'dashboard' } })`; `staticData.spec` points at `specs/pages/dashboard.spec.yaml`.
* `useSpec(routeId)` loads the parsed spec (bundled at build time via a Vite plugin `vite-plugin-paperos-specs` that imports `specs/**/*.yaml` as JSON).
* Command bar slot reserved for `input/command-registry`; expose `<Slot name="commandbar" />` only.
* P
DOD:
* Three example routes render inside the shell; typed `Link` to a missing route fails typecheck.
* Vitest: slot registry, search-param validation, spec adapter mapping (fixtures for 3 specs).
* Playwright: navigate all example routes; sidebar collapses to drawer at 375 and 768; inspector drawer at 1024; full grid at 1280, 1536, 1920. Screenshots at all 7 widths attached.
* Not-found and thrown-error routes screenshot-tested.
* `docs/shell/routing.md` explains adding a route + spec in under 10 steps; CHANGELOG entry.
* Linear comment with Pages preview links to each example route.
EDGE:
* Spec references a component not in the registry: render a visible `<MissingComponent name/>` placeholder in dev, log error and hide in prod.
* Two pages register the same slot with equal priority: last-write wins with a dev warning.
* Search params with invalid values: fall back to defaults, never crash.
* Route file exists without a spec: allowed in dev, blocked in CI by `spec-builder/validator`.
* Window narrower than 320: shell still scrolls horizontally rather than overlapping.
* Nested layouts under `_app/settings/*` must not double-render nav.
DEPS: `app-shell/monorepo-scaffold` (hard). Soft: `spec-builder/schema` (interim type until then), `design-system/layout-components` (uses plain divs until then). Unblocks `app-shell/create-cli`, `app-shell/template-docs`, `spec-builder/layout-codegen`, `identity/customer-portal-shell`, `identity/staff-console-shell`.


## PAP-17 [P0 Build M prio2 Backlog] Define typed environment and config layer with per-target secret storage (web, desktop keychain, mobile secure storage)
key=app-shell/env-config milestone=Template scaffolds and runs on web agent=Built by Forge (Tauri Smith for native stores). Reviewed by 
blockedBy=['PAP-13'] blocks=[]
GOAL: Provide one typed, validated configuration layer shared by web, desktop and mobile, with secrets stored in the right place on each target (browser: never; desktop: OS keychain; mobile: secure enclave/Keystore) so agent-written code cannot accidentally leak a key into a bundle.
SCOPE: In:

* `packages/core/src/config/`: Zod 4 schemas for public config (`VITE_*`, safe to ship) and server config (API, DB, S3, auth), typed accessors `publicEnv`, `serverEnv`.
* `.env.example`, `.env.test`, per-app `.env.local` gitignored; `pnpm env:check` fails on missing/invalid keys.
* Secret storage abstraction `SecretStore` with three backends: `WebSecretStore` (in-memory, session only, warns), `TauriKeychainStore` (via `tauri-plugin-stronghold` or `keyring` crate through a Tauri command), `MobileSecureStore` (Tauri 2 plugin `tauri-plugin-secure-storage`, iOS Keychain and Android EncryptedSharedPreferences).
* Runtime feature flags read from config with a `Flags` type and `useFlag('name')` hook.
* Build-time guard: Vite plugin fails the build if any non-`VITE_` env var appears in output.

Out: remote flag service, per-tenant settings (data layer), auth tokens lifecycle (`identity/bett
SPEC(first 1200): * `publicEnvSchema`: `VITE_API_URL` (url), `VITE_APP_NAME`, `VITE_GIT_SHA`, `VITE_ELECTRIC_URL`, `VITE_YJS_URL`, `VITE_SENTRY_DSN` (optional), `VITE_FLAGS` (comma list).
* `serverEnvSchema`: `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `STRIPE_SECRET_KEY` (optional), `OTEL_EXPORTER_OTLP_ENDPOINT` (optional), `NODE_ENV`.
* Parsing happens once at module load; failure throws with a table of missing keys, never partially loads.
* `SecretStore` interface: `get(key): Promise<string|null>`, `set(key, value)`, `delete(key)`, `list()`; keys namespaced `paperos.<app>.<key>`.
* Target detection: `getTarget(): 'web'|'desktop'|'ios'|'android'` using `window.__TAURI_INTERNALS__` and `navigator.userAgent` fallback.
* Tauri side: Rust command `secret_get/set/delete` in `apps/desktop/src-tauri/src/secrets.rs` using `keyring` 3.x; capability file limits to the main window.
* Documentation `docs/shell/config.md`: which vars go where, how CI supplies them (GitHub/Forgejo secrets, Coolify env), rotation procedure.
DOD:
* `pnpm env:check` passes with `.env.example` and fails with a clear table when a key is removed.
* Vitest: schema parsing, target detection, `WebSecretStore` behaviour; Rust unit test for keychain round-trip (skipped when no keychain available in CI, with a note).
* Build guard proven: a test build with a stray `SECRET=` in a `VITE_`-less import fails.
* Desktop manual check on Linux (`secret-service`) and macOS Keychain recorded as a short screen recording; screenshots of the settings debug page at 375, 1024, 1920.
* Docs and CHANGELOG updated; `.env.example` complete.
* Linear comment with PR and recording links.
EDGE:
* Linux without a running secret service (headless kiosk): fall back to an encrypted file with a loud warning; documented.
* Env var present but empty string: treated as missing.
* Same key set from two windows: last write wins; `list()` reflects it immediately.
* Bundle size: schemas must tree-shake so the server schema never reaches the browser.
* Test environment must not read `.env.local`; Vitest uses `.env.test` only.
* Value length above 4 KB on Android Keystore-backed storage: chunk or reject with error.
DEPS: `app-shell/monorepo-scaffold` (hard). `app-shell/tauri-desktop` for native backends (the web backend ships first; native backends land behind the target check). Consumed by `identity/better-auth`, `data-layer/api-layer`, `data-layer/file-storage`.


## PAP-18 [P0 Build S prio2 Backlog] Ship installable PWA manifest, service worker and offline app shell
key=app-shell/pwa milestone=Template scaffolds and runs on web agent=Built by Forge. Reviewed by Sentinel (Visual Inspector for i
blockedBy=['PAP-13'] blocks=[]
GOAL: Make the web build installable on any browser and load its shell instantly offline, so customers on flaky connections and staff on shared tablets get an app-like experience without a store download. This is the zero-install baseline every target inherits.
SCOPE: In:

* `vite-plugin-pwa` 1.x with Workbox 7 `generateSW` strategy in `apps/web`.
* Web app manifest: name, short name, theme colours from tokens, icons 192/512 plus maskable, screenshots for install UI, `display: standalone`, `display_override: ['window-controls-overlay','standalone']`, shortcuts for the top 3 routes, `id`.
* Offline app shell: precache HTML, JS, CSS, fonts, icons; runtime caching rules for API (`NetworkFirst`, 10s timeout), images (`CacheFirst`, 30 days, 200 entries), fonts (`StaleWhileRevalidate`).
* Update flow: `registerType: 'prompt'`; `<UpdateToast/>` in `packages/ui` offering "Reload".
* Offline page/state: `<OfflineBanner/>` reacting to `navigator.onLine` and a heartbeat fetch.
* Install prompt: capture `beforeinstallprompt`, expose `useInstallPrompt()`; iOS instructions sheet.

Out: offline data sync (`data-layer/local-first-sync`, `realtime/offline-queue`), pus
SPEC(first 1200): * Config in `apps/web/vite.config.ts` `VitePWA({ registerType:'prompt', includeAssets, manifest, workbox:{ navigateFallback:'/index.html', navigateFallbackDenylist:[/^\/api/], globPatterns:['**/*.{js,css,html,ico,png,svg,woff2}'], maximumFileSizeToCacheInBytes: 3_000_000, runtimeCaching:[...] }, devOptions:{ enabled:false } })`.
* `base` from `BASE_PATH` must propagate to manifest `start_url`, `scope` and `id` (Pages previews live under `/pr/<n>/`).
* Icons generated by `pnpm gen:icons` from `packages/ui/assets/logo.svg` using `@vite-pwa/assets-generator`.
* `packages/core/src/pwa/`: `useServiceWorker()` (needRefresh, offlineReady, update()), `useOnline()`, `useInstallPrompt()`.
* Cache versioning: Workbox handles; on activation `clients.claim()` and `skipWaiting` only after user accepts.
* Add `<meta name="theme-color">` bound to dark/light tokens via media queries; `apple-touch-icon`, `apple-mobile-web-app-*` tags.
* Lighthouse CI config (`ops/ci/lighthouserc.json`) asserting `installable` and PWA category 100; wired into `quality/perf-budgets` later.
DOD:
* Chrome DevTools Application panel shows manifest without warnings; Lighthouse PWA checks pass on the Pages preview.
* Playwright test: load page, go offline (`context.setOffline(true)`), reload, shell renders with `<OfflineBanner/>`; back online hides banner.
* Update toast appears when a new SW is deployed (test by bumping a constant between two builds).
* Install tested on Chrome desktop, Android Chrome, iOS Safari (add to home screen); short recordings attached.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 of installed/standalone mode where applicable and of the offline banner.
* `docs/shell/pwa.md` and CHANGELOG updated; Linear comment with preview URL and recordings.
EDGE:
* Pages preview scope `/pr/12/` must not hijack `/pr/13/`; scope set precisely.
* Storage quota exceeded on iOS (50 MB): image cache `purgeOnQuotaError: true`.
* User dismissed install prompt: do not re-ask for 14 days (`localStorage`).
* SW registered on `localhost` dev breaks HMR: keep `devOptions.enabled=false`.
* API responses with `Set-Cookie` must never be cached: exclude `/api/auth`.
* Stale precache after a failed deploy: `cleanupOutdatedCaches: true`.
* Browsers without SW (Firefox private mode): app still works, hooks return safe defaults.
DEPS: `app-shell/monorepo-scaffold` (hard), `app-shell/gh-pages-demo` (to test scope), `design-system/tokens` (theme colours; use placeholders until merged).


## PAP-19 [P0 Build L prio1 Backlog] Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle
key=app-shell/tauri-desktop milestone=Desktop and mobile shells build agent=Built by Forge (Tauri Smith sub-agent). Reviewed by Sentinel
blockedBy=['PAP-13'] blocks=['PAP-24', 'PAP-21', 'PAP-20']
GOAL: Wrap the same web bundle in Tauri 2 so PaperOS apps ship as signed, auto-updating native desktop apps on Linux, macOS and Windows with real OS windows, menus and file access. This is the foundation `app-shell/breakpoints-windows` and `app-shell/linux-kiosk` build on.
SCOPE: In:

* `apps/desktop/` Tauri 2.x project (`src-tauri/` Cargo crate in the root Cargo workspace) pointing `frontendDist` at `apps/web/dist` and `devUrl` at Vite.
* Capabilities (`src-tauri/capabilities/*.json`) with least privilege: `core:window`, `core:event`, `shell:open` (allowlist https), `dialog`, `fs` scoped to app data dir, `updater`, `notification`, `os`, `process`.
* Plugins: `tauri-plugin-window-state`, `tauri-plugin-updater`, `tauri-plugin-dialog`, `tauri-plugin-fs`, `tauri-plugin-shell`, `tauri-plugin-os`, `tauri-plugin-single-instance`, `tauri-plugin-deep-link` (`paperos://` scheme).
* Native menu (File, Edit, View, Window, Help) and tray icon with Show/Quit.
* CI workflow `ops/ci/desktop.yml` building `.deb`, `.rpm`, `.AppImage`, `.dmg`, `.msi`/`.nsis` via `tauri-apps/tauri-action`, signing with keys from secrets, uploading to a GitHub Release draft and `latest.json` for the
SPEC(first 1200): * `tauri.conf.json`: `identifier: os.imagine.paperos.<app>`, `bundle.active`, `windows[0]` 1280x800 min 960x600, `decorations` native, `titleBarStyle: 'Overlay'` on macOS, CSP `default-src 'self'; connect-src https: wss: <API>; img-src 'self' data: blob: https:`.
* Updater: pubkey in config, endpoints `https://github.com/imagine-os/<repo>/releases/latest/download/latest.json`; check on launch and every 6 h; UI via `<UpdateToast/>` from `app-shell/pwa` reused.
* Rust commands: `app_info`, `secret_*` (from `app-shell/env-config`), `open_path`. Commands live in `src-tauri/src/commands/`.
* Single instance: second launch focuses existing window and forwards deep link.
* Deep link `paperos://open/<route>` navigates the router.
* Dev script `pnpm dev:desktop` runs Vite and `tauri dev` concurrently; `pnpm build:desktop`.
* Rust toolchain pinned in `rust-toolchain.toml` (stable 1.8x); `cargo clippy -D warnings` and `cargo fmt --check` in CI.
* Linux deps documented (`libwebkit2gtk-4.1`, `libappindicator3`).
DOD:
* CI produces installers for all three OSes on a tag; artifacts attached to a draft release; `latest.json` valid.
* App launches, loads the web bundle, shows the version from `getVersion()` in `<BuildInfo/>`.
* Updater tested by publishing 0.0.1 then 0.0.2 and observing the prompt (recording attached).
* Vitest for the TS bridge; Rust tests for commands; capability files pass `tauri` schema validation.
* Screenshots at window sizes 960x600, 1280x800, 1920x1080 on Linux and macOS (Windows via CI screenshot step if available).
* `docs/shell/desktop.md` covers prerequisites, signing, releasing; CHANGELOG entry; Linear comment with release-draft link.
EDGE:
* Unsigned macOS build shows Gatekeeper warning: document `xattr -d` workaround and the notarisation TODO.
* Wayland vs X11 differences in window placement and tray (tray may be absent on GNOME without extension).
* Corporate proxy blocking updater endpoint: fail silently, log, retry later.
* Web bundle expects `/pr/<n>/` base path: desktop build must use `BASE_PATH=/`.
* Window closed while a background task runs: intercept `CloseRequested`, confirm if dirty.
* User has no write access to install dir on Windows: NSIS per-user install mode.
DEPS: `app-shell/monorepo-scaffold` (hard). `app-shell/env-config` for keychain commands (can merge in either order). Unblocks `app-shell/tauri-mobile`, `app-shell/breakpoints-windows`, `app-shell/template-docs`, `realtime/multi-window-sync`.


## PAP-20 [P1 Build L prio2 Backlog] Add Tauri 2 mobile targets (iOS, Android) with platform capability shims
key=app-shell/tauri-mobile milestone=Desktop and mobile shells build agent=Built by Forge (Tauri Smith). Reviewed by Sentinel (Security
blockedBy=['PAP-19'] blocks=['PAP-154']
GOAL: Extend the Tauri 2 project to iOS and Android so the same web bundle runs as a native mobile app with access to camera, haptics, secure storage, share sheet and biometrics through a single TypeScript shim layer that degrades gracefully on web.
SCOPE: In:

* `apps/mobile/` sharing `src-tauri` with desktop via Cargo features, or a sibling crate re-using the same commands (decide and record in ADR; default: single crate, `tauri android init` / `tauri ios init` inside `apps/desktop/src-tauri`, with `apps/mobile` holding platform assets and scripts).
* Plugins: `tauri-plugin-barcode-scanner` (camera), `tauri-plugin-haptics`, `tauri-plugin-biometric`, `tauri-plugin-secure-storage` (or stronghold) wired to `SecretStore` from `app-shell/env-config`, `tauri-plugin-share`, `tauri-plugin-geolocation`, `tauri-plugin-notification`.
* `packages/core/src/native/capabilities.ts`: `Capabilities` interface (`camera`, `haptics`, `biometrics`, `secureStore`, `share`, `geo`, `notify`) with `NativeCapabilities` and `WebCapabilities` (Web Share, `navigator.vibrate`, WebAuthn, MediaDevices) implementations selected by `getTarget()`.
* Safe-area CSS variable
SPEC(first 1200): * Android: `minSdk 26`, `targetSdk 35`, ABIs arm64-v8a + x86_64; Gradle wrapper pinned; `applicationId` from `identifier`.
* iOS: deployment target 15.0; Info.plist usage strings for camera, location, Face ID.
* Capability files `mobile.json` granting only the mobile plugins to the main window.
* `useCapability('camera')` returns `{ available, request(), status }`; unavailable on web returns `available:false` without throwing.
* Deep links: `paperos://` plus universal links config placeholders.
* Viewport meta `viewport-fit=cover, interactive-widget=resizes-content`; `env(safe-area-inset-*)` mapped to `--safe-*` tokens.
* Dev: `pnpm dev:android`, `pnpm dev:ios` wrapping `tauri android dev`/`tauri ios dev` with the Vite server bound to `0.0.0.0`.
* Test devices: per `app-shell/device-matrix-research` (Pixel 8 emulator, iPhone 15 simulator, iPad 11).
DOD:
* Debug APK and iOS simulator build succeed in CI on the PR.
* App runs on Android emulator and iOS simulator; recording of navigating three routes, scanning a QR code, triggering haptics and storing/reading a secret.
* Vitest for capability selection and web fallbacks; Rust builds with mobile features under `clippy -D warnings`.
* Screenshots at 375x812, 390x844, 768x1024 (portrait and landscape) attached; safe areas verified on notch device.
* `docs/shell/mobile.md` covers toolchain setup (Android Studio, Xcode), signing and release; CHANGELOG entry; Linear comment with CI artifact links.
EDGE:
* Camera permission denied: `status:'denied'` with a settings deep-link helper.
* Android back button: map to router `history.back()`; exit on root after confirmation.
* Keyboard covering inputs: verify `resizes-content` works in WebView on both OSes.
* Low-memory WebView kill on Android restores route from `sessionStorage`.
* Simulator has no biometrics: shim returns `available:false`, tests skip.
* Localhost dev URL unreachable from device: script prints LAN IP and QR.
DEPS: `app-shell/tauri-desktop` (hard), `app-shell/env-config` (secure store), `app-shell/device-matrix-research` (target sizes). Feeds `input/touch-gestures`, `input/pen`, `data-layer/file-storage` (camera uploads).


## PAP-21 [P1 Build L prio1 Backlog] Build responsive breakpoint matrix and multi-monitor window manager that detaches panels into OS windows
key=app-shell/breakpoints-windows milestone=Desktop and mobile shells build agent=Built by Forge (Tauri Smith) with Nova consulting on sync bo
blockedBy=['PAP-14', 'PAP-19'] blocks=['PAP-145', 'PAP-23']
GOAL: Implement the responsive layer from the device matrix as container queries and a window manager that lets any panel detach into its own OS window on desktop, drag across monitors, remember placement, and re-dock, so staff can spread one app over several screens.
SCOPE: In:

* `packages/core/src/layout/breakpoints.css` and Tailwind v4 theme variables generated from `BREAKPOINTS` (`app-shell/device-matrix-research`); `@container` names for `shell`, `sidebar`, `main`, `inspector`, `panel`.
* `useBreakpoint()` and `useContainerSize(ref)` hooks (ResizeObserver based).
* `packages/core/src/windows/`: `WindowManager` with `detach(panelId)`, `dock(panelId)`, `list()`, `focus(id)`, `moveToDisplay(id, displayId)`; persistence in `tauri-plugin-window-state` plus our own `layouts` store in `localStorage` keyed by display topology hash.
* Detached window renders route `/_window/<panelId>` inside a minimal chrome shell (no nav) via `app-shell/router-layouts`.
* Web fallback: `window.open` popups with the same route; `BroadcastChannel` for state (full sync via `realtime/multi-window-sync`).
* Panel header affordance: "Pop out" / "Dock" button, keyboard `Ctrl/Cmd+Shif
SPEC(first 1200): * Tauri side: `WebviewWindowBuilder` per detached panel, label `panel-<id>`, `parent` unset, `decorations true`, remembers `outerPosition/size`; `monitor()`/`available_monitors()` exposed via command `list_displays` returning `{ id, name, bounds, scale, primary }`.
* Display topology hash = sorted `${name}:${w}x${h}@${scale}` joined; on mismatch fall back to primary display centre.
* Store shape: `{ panels: { [id]: { state: 'docked'|'detached', bounds?, display? } }, presets: { [name]: PanelsState } }`; Zod-validated; migrations by `version`.
* Docking: closing a detached window docks it; `dock()` from the main window closes the child.
* Focus and z-order: `focus(id)` brings window forward; main window shows a chip per detached panel.
* Container query classes: `@container shell (min-width: 1024px)` etc.; utilities `cq-md:` mapped in Tailwind via plugin.
* Breakpoints also drive `AppShell` collapse rules defined in `app-shell/router-layouts` (replace the interim media queries).
DOD:
* On Linux and macOS: detach inspector, move to a second display, quit, relaunch; window reappears on the same display (recording).
* Unplug the second display and relaunch: window recovers to primary (recording).
* Web: pop-out opens popup, state mirrors via BroadcastChannel (Playwright multi-page test).
* Vitest: topology hash, store migrations, dock/detach reducer.
* Screenshots of the shell at all 7 widths plus a two-display composite; `quality/playwright-matrix` config updated to use `breakpoints.json`.
* `docs/shell/windows.md`; CHANGELOG; Linear comment with recordings and preview.
EDGE:
* Popup blockers on web: show inline hint, keep panel docked.
* Display scale changes (1x to 2x) while running: re-query bounds on `scale-changed`.
* Detached window closed by OS (crash): main detects via `onCloseRequested`/heartbeat and re-docks.
* Panel that requires main-window context (selection) opens with empty state and a message.
* More than 8 detached windows: warn about memory; cap at 12.
* Wayland does not allow apps to position windows: persist size only, document.
DEPS: `app-shell/tauri-desktop`, `app-shell/device-matrix-research` (hard), `app-shell/router-layouts` (window route). Pairs with `realtime/multi-window-sync` for data coherence; consumed by `app-shell/linux-kiosk`, `design-system/layout-components`.


## PAP-22 [P1 Build M prio1 Backlog] Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project
key=app-shell/create-cli milestone=Desktop and mobile shells build agent=Built by Forge with Atlas's Dispatcher sub-agent reviewing t
blockedBy=['PAP-91', 'PAP-47', 'PAP-16'] blocks=['PAP-29', 'PAP-28']
GOAL: `paperos create <app>` takes a blank imagine-os repo to a running, tracked, deployable app in one command: it clones the template, renames identifiers, pushes to GitHub and Forgejo, configures CI and Pages, and creates a Linear project seeded with the standard starter issues. This is the direct answer to PAP-5.
SCOPE: In:

* `packages/cli/` published as `@paperos/cli` (bin `paperos`), built with `tsup`, using `commander` 13, `@clack/prompts`, `execa`, `simple-git`, `octokit`, `@linear/sdk`.
* Commands: `create <name> [--repo imagine-os/<name>] [--linear-project] [--no-push] [--template <ref>] [--yes]`, `doctor` (checks tokens/tools), `demo:url`.
* Steps: validate name; verify target repo exists and is empty; degit template at pinned tag; run `rename` (package names, `identifier`, manifest, README, CLAUDE.md); `pnpm i`; `pnpm check`; initial commit; push `main`; call `forge bootstrap` (`forge/repo-bootstrap`) for mirror, secrets, labels, webhooks; enable Pages; create Linear project with description, milestones and starter issues from `templates/linear/starter-issues.yaml`; print URLs.
* Idempotent re-run: each step records completion in `.paperos/create.state.json` and skips.
* Dry-run mode printing t
SPEC(first 1200): * Tokens read from env (`GITHUB_TOKEN`, `FORGEJO_TOKEN`, `LINEAR_API_KEY`) or `SecretStore` (`app-shell/env-config`); `doctor` reports which are present without printing values.
* Name rules: kebab-case, 3-40 chars, not reserved; derived `PascalName`, `identifier os.imagine.paperos.<name>`.
* Rename implemented as a token-replacement map applied to a curated glob list (no blind sed on binaries); tested against a fixture template.
* Linear: team `PAP` by default (`--team`), project state `planned`, labels from `pm-linear/configure-workspace`; starter issues include "Write app.spec.yaml", "First page spec", "Enable design tokens", each in Backlog with the `Spec` label.
* Output summary: repo URLs (GitHub, Forgejo), Pages URL, Linear project URL, next steps.
* Exit codes: 0 success, 2 validation, 3 external API failure with retry hint.
* Logs written to `.paperos/create.log` for agent post-mortems; also emits a Linear comment on the new project's first issue linking the log if `--linear-project`.
* Unit-test external calls behind interfaces (`GitHubClient`, `ForgejoClient`, `LinearClient`) with fakes.
DOD:
* Running against a throwaway imagine-os repo produces a green CI, a live Pages URL and a Linear project within 10 minutes; recording attached.
* Re-running is a no-op (state file) and `--force` redoes steps.
* Vitest covering name validation, rename map, state machine, fakes for all clients; e2e script in CI using a sandbox repo (nightly, not per-PR).
* `paperos doctor` output screenshot; generated app's home screenshots at 375, 1024, 1920.
* `docs/cli/create.md`; README quick start updated; CHANGELOG; Linear comment with the demo app's links.
EDGE:
* Target repo not empty: abort unless `--force-empty` explicitly given; never delete history.
* Rate-limited GitHub API: exponential backoff, resume from state.
* Linear project name collision: suffix with date and warn.
* Missing Forgejo token: skip mirror step with a warning, mark state `pending` so `forge bootstrap` can finish later.
* Template tag not found: list available tags.
* Running inside an existing git repo directory: refuse.
DEPS: `app-shell/router-layouts` (template must be real), `forge/mirror` and `forge/repo-bootstrap` (mirror step), `pm-linear/configure-workspace` (labels/states), `app-shell/gh-pages-demo` (Pages settings). Feeds `agents/skills-library` (a `create-app` skill wraps it).


## PAP-23 [P2 Build M prio3 Backlog] Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag
key=app-shell/linux-kiosk milestone=Multi-monitor and PWA polish agent=Built by Forge (Tauri Smith, Ops Runner for systemd). Review
blockedBy=['PAP-145', 'PAP-21'] blocks=[]
GOAL: From one CLI flag, launch a PaperOS desktop build in kiosk mode on Linux that opens one full-screen, synced window per connected display (or several browser windows in "parallel-browser" mode), so a shop, clinic or warehouse can run staff dashboards and signage from a single cheap box.
SCOPE: In:

* Tauri launch flags parsed in Rust: `--kiosk`, `--displays all|1,2`, `--routes /board,/queue` (one per display, cycled), `--parallel-browser` (spawn Chromium/Firefox windows instead of Tauri webviews for setups that need browser extensions), `--reload-hours 24`, `--watchdog`.
* `ops/kiosk/`: systemd user service template, `paperos-kiosk.service`, a `cage`/`sway` minimal compositor recipe, udev-less display detection via `available_monitors()`, `unclutter` cursor hiding, auto-login instructions for Debian/Ubuntu and Fedora.
* Kiosk window options: fullscreen, `always_on_top`, `decorations false`, `closable false`, disabled context menu and devtools, keyboard shortcut `Ctrl+Alt+Shift+Q` to exit (configurable, can be disabled).
* Health: watchdog restarts a crashed window; heartbeat endpoint `/_kiosk/health` for `data-layer/observability`; nightly reload.
* Remote config: `~/.config/p
SPEC(first 1200): * Startup sequence: parse flags -> enumerate displays -> for each selected display create `WebviewWindow` labelled `kiosk-<n>` with bounds = display bounds, `fullscreen(true)`, load route `${routes[n % routes.length]}?kiosk=1&display=n`.
* Routes receive `kiosk=1` search param; `AppShell` (`app-shell/router-layouts`) hides nav/command bar and enlarges type via a `data-kiosk` attribute (10-foot rules from `app-shell/device-matrix-research`).
* Cross-window coherence via `realtime/multi-window-sync` (selection, filters follow the primary display when `--follow-primary`).
* Parallel-browser mode: spawn `chromium --kiosk --app=<url> --window-position=<x>,<y> --user-data-dir=<tmp/n>` per display using `tauri-plugin-shell` sidecar; supervise children.
* Watchdog: Rust thread polls each window every 10 s; on missing window or webview crash (`tauri::WindowEvent::Destroyed`) recreate after 2 s backoff, max 10 tries, then exit non-zero for systemd restart.
* Logging to journald via `tracing-journald`.
* `paperos kiosk install` subcommand in `@paperos/cli` writes the systemd unit and config.
DOD:
* On a Linux VM with two virtual displays (Xvfb or a real dual-monitor box): `paperos-desktop --kiosk --displays all --routes /board,/queue` shows both routes fullscreen; recording attached.
* Kill one window: watchdog restores it within 5 s (recording).
* `systemctl --user enable` recipe works from cold boot to app in under 60 s on Ubuntu 24.04.
* Rust unit tests for flag parsing and display-to-route assignment; Vitest for kiosk search-param handling.
* Screenshots at 1920x1080, 3840x2160 and a portrait 1080x1920 display.
* `docs/shell/kiosk.md` with hardware recommendations; CHANGELOG; Linear comment with recordings.
EDGE:
* Display hot-plugged after start: listen for monitor changes, open/close windows accordingly.
* Zero displays detected (headless): exit with code 4 and clear message.
* Network down at boot: shell loads from cache (`app-shell/pwa`), shows offline banner, retries.
* Screen blanking/DPMS: disable via config in compositor recipe; document.
* Portrait-rotated display: bounds already rotated by compositor; verify layout.
* Exit shortcut on a public screen: default disabled when `--public` flag set.
DEPS: `app-shell/breakpoints-windows` (window manager, display enumeration), `realtime/multi-window-sync` (coherence). Soft: `app-shell/create-cli` for the install subcommand.


## PAP-24 [P1 Docs M prio2 Backlog] Write the repo template guide: folder conventions, how an agent adds a page, how to ship each target
key=app-shell/template-docs milestone=Multi-monitor and PWA polish agent=Written by Quill (Spec and Documentation Lead) with Forge su
blockedBy=['PAP-19', 'PAP-16'] blocks=[]
GOAL: Write the guide every new Claude Code session reads before touching the template: where things live, how a page is added from spec to route to test, how each target is run and shipped, and which conventions are non-negotiable. It is the onboarding path for agents and future humans alike.
SCOPE: In:

* `docs/template-guide.md` (main, 3,000-5,000 words) plus focused pages under `docs/shell/` (already stubbed by earlier issues) cross-linked and indexed.
* Root `CLAUDE.md` rewritten to a 300-word summary linking to the guide, with the "never do" list.
* `.claude/rules/*.md`: naming, imports, tests, specs-before-code, no secrets, commit format (from `forge/branch-policy`).
* Worked example: add a `/_app/invoices` page end-to-end (spec, route, component, test, screenshot, PR) with copy-pasteable snippets tested in CI.
* Target cheat-sheets: web dev/build/preview, desktop dev/build/release, mobile dev/build, kiosk, Pages preview.
* Troubleshooting FAQ seeded from real errors hit in P0 issues.

Out: component guidelines (`design-system/guidelines-docs`), spec-writing tutorial (`spec-builder/spec-docs`), agent character docs (`agents/character-docs`).
SPEC(first 1200): * Structure of `template-guide.md`: 1 Purpose; 2 Folder map (table: path, owner project, what goes here, what never goes here); 3 Commands; 4 Adding a page (10 numbered steps with file paths); 5 Data access pattern (link `data-layer/api-layer`); 6 Auth and audiences (link identity); 7 Targets; 8 Quality gates and what each expects (link `quality/*`); 9 Conventions; 10 Glossary.
* Every code snippet is extracted from files in `docs/examples/` that are compiled and tested in CI (`pnpm docs:check` uses a small script to verify snippet markers match source), so docs cannot rot silently.
* Docs are Markdown with front-matter (`title`, `owner`, `updated`) compatible with `collab/docs-engine` rendering; until that exists, GitHub renders them.
* Diagrams in Mermaid (folder tree, request flow, release flow).
* Reading-time budget: an agent must be able to read CLAUDE.md + section 4 in under 2,000 tokens; verify with a token count script.
* Links to Linear issue keys for anything not yet built are marked `(planned: <key>)`.
DOD:
* Guide, CLAUDE.md, rules and worked example merged; `pnpm docs:check` green.
* A fresh Claude Code session given only the guide adds the example page and passes Gate 1 without asking a question (Atlas runs this trial; transcript linked).
* Token count of CLAUDE.md under 1,200; guide section 4 under 900.
* Docs rendered screenshot at 375, 1024 and 1920 (GitHub render or docs engine).
* Mermaid diagrams render on GitHub.
* CHANGELOG entry; Linear comment with the trial transcript and doc links.
EDGE:
* Guide references a command renamed later: `docs:check` also verifies every backticked `pnpm <script>` exists in `package.json`.
* Sections growing past budget: CI warns above token limits.
* Windows path separators in examples: use POSIX and note.
* Agent with no Rust toolchain: desktop section starts with a "skip if" check.
* Docs engine not yet live: relative links must work on GitHub and in-app.
* Out-of-date screenshots: mark with the SHA they were taken at.
DEPS: `app-shell/router-layouts` and `app-shell/tauri-desktop` (hard, to document real behaviour). Soft: `app-shell/pwa`, `app-shell/env-config`, `forge/branch-policy`, `pm-linear/session-playbook`. Consumed by every build issue thereafter and by `agents/skills-library`.


## PAP-25 [P0 Infra M prio1 Ready for Claude] Provision the Hetzner VPS with Coolify, Caddy, DNS for the PaperOS domain, object storage, sops keys and the paperos-infra repo
key=app-shell/vps-coolify-bootstrap milestone=Template scaffolds and runs on web agent=Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel 
blockedBy=[] blocks=['PAP-140', 'PAP-45', 'PAP-30', 'PAP-26']
GOAL: Create the single self-hosted environment that `forge/forgejo-deploy`, `data-layer/postgres-provision`, `realtime/yjs-server`, `pm-linear/orchestrator`, `data-layer/local-first-sync` (Electric) and `quality/release-train` all silently assume already exists: a Hetzner VPS running Coolify behind Caddy, the `PAPEROS_DOMAIN` DNS zone, a Hetzner Object Storage bucket for backups, an age/sops key pair for encrypted secrets, a Resend account with a verified sending domain, and the `imagine-os/paperos-infra` repository that holds all of it as code. Without this issue the P0 infra issues are not actually parallel: each would provision its own host or block on Justin.
SCOPE: In:

* Hetzner Cloud project and one VPS (`cpx31` class, Ubuntu 24.04, 8 GB RAM minimum so Forgejo, Postgres, Hocuspocus, Electric and the orchestrator co-locate; document the upgrade path to a second host).
* Coolify (latest stable) installed via the official script; server proxy switched from Traefik to Caddy before any resource is created (matches `forge/forgejo-deploy`); Coolify admin account for Justin; API token for the release pipeline stored as a GitHub Actions secret `COOLIFY_TOKEN` and in sops.
* DNS: zone for `PAPEROS_DOMAIN` (Justin's registrar; if he has none, Cloudflare free) with records `@`, `app.`, `api.`, `staging.`, `git.`, `collab.`, `sync.`, `orchestrator.`, `s3.`; wildcard `*.preview.` for per-PR previews; Let's Encrypt via Caddy.
* Hetzner Object Storage bucket `paperos-backups` (restic repo) and `paperos-files` (MinIO alternative for `data-layer/file-storage` if M
SPEC(first 1200): * `ops/bootstrap.sh` is idempotent: re-running on a provisioned host changes nothing (checked with a dry-run flag that prints planned actions).
* Environment matrix recorded in `docs/runbooks/host.md`: `production` and `staging` are separate Coolify projects on the same host with separate Postgres instances (`data-layer/postgres-provision`), separate domains (`app.` vs `staging.`) and separate secrets files.
* Coolify resource naming convention `paperos-<env>-<service>` and a label `paperos.owner=<agent>` so the orchestrator can list what each character deployed.
* Health endpoint convention: every service exposes `GET /healthz` returning `{ ok, version, sha }`; Coolify health checks every 30 s.
* Secret inventory `ops/secrets/INVENTORY.md`: name, service, rotation owner, last rotated; CI job fails when a secret referenced in any `*.enc.yaml` is missing from the inventory.
* Cost note in the ADR: monthly total for VPS, object storage, domain, Resend, Tailscale (expected under 40 EUR/month) so Justin approves once.
DOD:
* `https://git.PAPEROS_DOMAIN`, `https://staging.PAPEROS_DOMAIN` and `https://app.PAPEROS_DOMAIN` return a Coolify placeholder or the first deployed service over valid TLS (screenshots at 1280 and 375).
* `ssh` to the host works only over the tailnet; public port scan shows 80/443 only (nmap output attached).
* `sops -d ops/secrets/example.enc.yaml` works with the orchestrator key; Justin's recovery key decrypts the same file (he confirms once in the Needs Justin item that also asks for the Hetzner and registrar credentials).
* Resend test email delivered to Justin's inbox from `noreply@PAPEROS_DOMAIN` with passing SPF/DKIM (headers attached).
* Restic repo initialised in `paperos-backups`; `restic snapshots` lists the first snapshot of `/data/coolify`.
* `docs/runbooks/host.md`, ADR `docs/adr/00xx-hosting-bootstrap.md`, `CHANGELOG.md` entry, Linear comment with URLs and the cost table.
EDGE:
* Justin has no domain yet: use a `*.sslip.io` address for staging so nothing blocks, and leave a single Needs Justin item asking for the domain; switching later is one env var (`PAPEROS_DOMAIN`) and a Caddy reload.
* Hetzner account needs identity verification (can take a day): the Needs Justin item is filed first thing in the session, and the rest of the issue proceeds against a local Coolify in a VM (`multipass`) so scripts are verified before the host exists.
* Coolify install script fails on Ubuntu 24.04 kernel: pin the Coolify version tested and record the fix.
* Cloudflare proxy (orange cloud) breaks Let's Encrypt HTTP challenge and WebSockets for `collab.`: keep DNS-only (grey cloud) for all records.
* sops key loss: the recovery key is printed once for Justin to store offline; the runbook covers re-keying every file.
* Host disk fills from Docker images: weekly `docker system pr
DEPS: None; ready now, and the earliest infra issue to start because `forge/forgejo-deploy`, `data-layer/postgres-provision`, `pm-linear/orchestrator`, `realtime/yjs-server` and `app-shell/app-deploy-pipeline` deploy onto it. Soft: `app-shell/env-config` (secret names), `libraries/license-policy`.


## PAP-26 [P0 Infra M prio1 Backlog] Build the app deploy pipeline: Docker images for apps/web and apps/api, staging on merge to main, production on tag, per-PR previews and rollback via Coolify
key=app-shell/app-deploy-pipeline milestone=Template scaffolds and runs on web agent=Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel 
blockedBy=['PAP-30', 'PAP-25', 'PAP-13'] blocks=['PAP-88', 'PAP-86', 'PAP-29']
GOAL: Turn a merge into a running application. `quality/release-train` schedules a nightly staging deploy and a Monday production promotion, `quality/e2e-flows` and `realtime/load-test` need a staging URL, and `app-shell/create-cli` promises every new app a live environment, but no issue builds the images or the Coolify applications they deploy to. This issue does, for the template itself and for every app generated from it.
SCOPE: In:

* `apps/web/Dockerfile` (multi-stage: pnpm install with Turbo prune, Vite build, `caddy` static image serving `dist/` with SPA fallback and immutable asset caching) and `apps/api/Dockerfile` (Node 22 distroless, `node dist/server.js`); if `apps/api` does not exist yet when this issue runs, ship a `healthz` stub server in `apps/api` that `data-layer/api-layer` replaces.
* GitHub Actions workflow `deploy.yml`: on push to `main` build both images, tag `sha-<short>` and `main`, push to GHCR (`ghcr.io/imagine-os/<app>-web|api`) and mirror to Forgejo's registry when `forge/actions-runner` lands; then call the Coolify deploy webhook for `paperos-staging-web` and `paperos-staging-api`.
* Production: on tag `v*` (from `forge/release-tags`) deploy the same immutable image digest to `paperos-production-*`; never rebuild for production.
* Migrations: `apps/api` container runs `drizzle-kit migra
SPEC(first 1200): * Image size budgets: web under 40 MB, api under 200 MB; CI fails above.
* Build cache: `docker/build-push-action` with GHA cache; a no-change rebuild completes under 3 minutes.
* Deploy job waits on Coolify's deployment status API until `finished`, then smoke-tests `GET /healthz` and asserts `/__version` equals the pushed SHA; failure marks the job red and posts to the Linear issue through `pm-linear/webhooks` when available.
* Concurrency group `deploy-<env>` cancels superseded staging deploys; production deploys never cancel.
* Secrets are injected by Coolify from sops-decrypted values (`ops/secrets/<env>-api.enc.yaml`), never baked into images; `quality/security-scans` scans images with Trivy before push.
* `paperos create` (`app-shell/create-cli`) copies `deploy.yml` and `preview.yml` and templates the app name into Coolify resource names.
DOD:
* Merge to `main` deploys to `https://staging.PAPEROS_DOMAIN`; `/__version` shows the SHA (screenshot and workflow link).
* A test tag `v0.0.1-test` deploys the same digest to production; `docker inspect` digests match (log attached), then the tag is deleted.
* A PR opens a preview at `pr-<n>.preview.PAPEROS_DOMAIN` within 5 minutes and is removed within 5 minutes of close.
* Rollback command restores the previous SHA on staging in under 2 minutes (timed log).
* Migration failure test: a PR with a deliberately broken migration is blocked before rollout, staging keeps serving the old version.
* `docs/runbooks/deploy.md`, ADR on image and registry choices, `CHANGELOG.md` entry, Linear comment with the URLs.
EDGE:
* GHCR rate limits or outage: registry mirror on Forgejo is the fallback pull source; documented in the runbook.
* Web image built with the wrong `BASE_PATH`: web images always use `/`; only `app-shell/gh-pages-demo` sets a sub-path.
* Two merges within a minute: the concurrency group cancels the first staging deploy; the second carries both changes.
* Coolify webhook fires but the API token was rotated: job fails with a clear message pointing at `ops/secrets/INVENTORY.md`.
* Preview environment for a PR from a fork: skipped (no secrets exposure) with a comment explaining why.
* Database migration succeeds but the rollout fails health checks: automatic redeploy of the previous image; migration rollback stays manual and documented, since Drizzle migrations are forward-only by default.
DEPS: `app-shell/monorepo-scaffold` (build scripts), `app-shell/vps-coolify-bootstrap` (host, Coolify token, domain), `data-layer/postgres-provision` (staging and production databases). Soft: `app-shell/env-config`, `data-layer/api-layer`, `forge/release-tags`, `quality/security-scans`. Consumed by `quality/release-train`, `quality/e2e-flows`, `realtime/load-test`, `app-shell/create-cli`, `app-shell/new-app-drill`.


## PAP-27 [P1 Build M prio2 Backlog] Add internationalisation and localisation: ICU message catalogs, locale negotiation, Intl formatting helpers, RTL layout flip, pseudo-locale testing and an agent translation skill
key=app-shell/i18n-l10n milestone=Desktop and mobile shells build agent=Built by Forge (Platform Engineer) with Iris (Component Craf
blockedBy=['PAP-66', 'PAP-13'] blocks=['PAP-126']
GOAL: Justin's brief asks for software that adapts to "every single type of business in the whole wide world", and the finance, tables and design-system specs each mention multi-currency or RTL in passing, yet no issue owns the locale layer. Retrofitting i18n after 200 pages exist is one of the most expensive refactors there is. This issue makes localisation a template default: catalogs, formatting, direction and a translation workflow that agents run.
SCOPE: In:

* `packages/i18n/`: Lingui 5 (ICU MessageFormat, compile-time extraction, small runtime; ADR compares FormatJS and i18next) with macros `t`, `Trans`, `plural`, `select`; catalogs per locale in `apps/web/src/locales/<locale>/messages.po`; `pnpm i18n:extract` and `pnpm i18n:compile` wired into `quality/ci-gate1` so an unextracted string fails the build.
* Locale negotiation: order of precedence tenant default (`identity/org-tenancy` setting), user preference (`identity/better-auth` profile), `Accept-Language`, browser; persisted in the URL only when a tenant enables locale routes; Tauri targets read OS locale.
* Formatting helpers `formatNumber`, `formatCurrency` (minor units, `currencyDisplay: 'narrowSymbol'`, matching `design-system/data-display`), `formatDate`, `formatRelative`, `formatList`, `formatUnit`, all wrapping `Intl` with the active locale and tenant timezone; `tables/fiel
SPEC(first 1200): * Source language strings live in code; catalogs are the only translation store; no database-stored UI strings except tenant-authored content.
* Every `Intl` call goes through `packages/i18n`; a lint rule bans direct `toLocaleString` and `new Intl.*` outside the package.
* Message IDs are auto-generated hashes with explicit IDs allowed for reusable terms; a CI check flags catalogs with more than 2 percent fuzzy entries as a warning, 10 percent as failure for enabled locales.
* Bundle: catalogs lazy-loaded per locale; the `en` runtime adds under 8 KB gzipped.
* Dates stored as UTC ISO; tenant timezone from `identity/org-tenancy`; the formatting layer never guesses.
* Number input parsing respects locale decimal separators (`packages/i18n/parse`), used by `tables/field-types` number and currency editors.
DOD:
* The template app renders in `en`, `es`, `ar` and `en-XA` with a locale switcher in the staff shell; screenshots at 375 and 1280 for each, `ar` shows mirrored layout with no clipped text.
* `pnpm i18n:extract` on a PR that adds a literal string produces a catalog diff; forgetting to run it fails CI (demonstrated in a test PR).
* Translation skill run on the `es` catalog produces a PR with glossary-consistent translations; Quill reviews and merges (link).
* Currency and date rendering verified against 6 locales in a Vitest table; `ar` uses Arabic-Indic digits only when the tenant opts in.
* Playwright pseudo-locale column green on the matrix.
* Docs `docs/platform/i18n.md`, ADR, `CHANGELOG.md`, Linear comment.
EDGE:
* Plural rules for Arabic (six forms) and Polish: `plural` macro tests per locale.
* Strings concatenated from fragments: lint rule detects `+` with string literals adjacent to JSX text and points to `Trans`.
* Long German compounds overflowing buttons: pseudo-locale expansion catches it; component guidelines specify truncation with a tooltip.
* Mixed-direction content (an English product name in an Arabic sentence): `unicode-bidi: isolate` on inline data spans in `design-system/data-display`.
* Tenant switches default locale while users are online: change applies at next navigation, not mid-form.
* Locale with no catalog enabled by a tenant: fall back to `en` with a staff-visible warning, never blank strings.
DEPS: `app-shell/monorepo-scaffold` (packages layout), `design-system/tokens` (typography tokens per script). Soft: `spec-builder/schema`, `spec-builder/layout-codegen`, `design-system/primitives`, `identity/org-tenancy`, `quality/playwright-matrix`, `tables/field-types`. Consumed by `spec-builder/business-profile`, `business-core/ledger`, `growth/outreach-sequences`, `migration/business-templates`.


## PAP-28 [P1 Build L prio2 Backlog] Make every platform capability a removable module: module manifests, `modules:` in app.spec.yaml, `paperos create --without`, per-tenant module toggles and dead-code checks
key=app-shell/feature-modules milestone=Multi-monitor and PWA polish agent=Built by Forge (Platform Engineer) with Quill (Page Spec Wri
blockedBy=['PAP-117', 'PAP-22'] blocks=['PAP-126']
GOAL: The brief's premise is "build everything into the template, then remove what an app does not need". Nothing in the plan makes removal cheap: packages are wired by imports, routes are files, navigation is hand-written. This issue defines a module contract so that every capability project (tables, collab, realtime, business-core, growth, migration, agents UI) registers itself as a module, an app declares which modules it uses in `app.spec.yaml`, `paperos create` can omit modules at generation time, and tenants can toggle optional modules at runtime.
SCOPE: In:

* Module manifest `module.ts` exported by each capability package: `{ id, title, version, routes, navItems, entities, permissions, jobs, settingsSchema, integrations, dependsOn: moduleIds, optional: boolean }` validated by Zod; `packages/core/modules` registry that loads manifests listed in `app.spec.yaml` `modules:` and refuses unknown or dependency-incomplete sets.
* `app.spec.yaml` `modules:` section (coordinated with `spec-builder/app-level-spec`): `enabled`, `defaultForNewTenants`, `tenantToggleable`; the spec validator fails a page spec that references a component or entity from a disabled module.
* Router integration: `app-shell/router-layouts` composes the route tree from enabled modules' `routes`; navigation from `navItems`; `identity/rbac-abac` loads `permissions`; `data-layer/jobs-queue` registers `jobs`; `data-layer/drizzle-schema` migration sets are per module and appli
SPEC(first 1200): * Core (non-removable) modules: `shell`, `identity`, `data`, `design-system`, `spec`, `input`, `i18n`; every other project is optional and must declare `optional: true`.
* Cross-module coupling only via events (`packages/core/events`: `emit('invoice.paid', payload)`) or explicit `dependsOn`; a lint rule bans direct imports across optional module boundaries.
* Manifest `entities` reference Drizzle tables; `pnpm db:migrate` applies `drizzle/<module>/*.sql` for enabled modules only and records the module in `_migrations_modules`.
* A disabled optional module's data is retained; re-enabling is instant; deletion is a separate explicit `pnpm modules:purge <id>` with a Needs Justin gate for production tenants (destructive class per `libraries/mcp-servers`).
* `paperos create` templates the module list into the Linear project it creates (`pm-linear/configure-workspace` labels), so agents know which modules exist in that app.
DOD:
* Template with all modules builds; `paperos create demo --without payroll,crm,growth` produces a repo that builds, passes `pnpm check` and shows no CRM or payroll navigation (screenshots).
* CI matrix removes each optional module in turn from the template and the build stays green (workflow link).
* Tenant admin disables `canvas` at runtime: route returns 404, nav item disappears, API procedure rejected, data retained; re-enable restores (Playwright test).
* Spec validator rejects a page referencing a disabled module's component with a readable error (test).
* `knip` report clean on the template.
* `docs/platform/modules.md`, ADR, `CHANGELOG.md`, Linear comment.
EDGE:
* Module A optional, module B depends on A, tenant disables A: the settings page blocks with the dependency list; the API enforces the same rule.
* A migration from a disabled module was already applied on a tenant database: retained; `pnpm db:check` treats module-scoped migrations of disabled modules as ignorable.
* Removing a module at create time that the design system's Storybook stories import: stories live inside the module package, so they leave with it; `design-system/storybook` globs only enabled packages.
* Two modules registering the same route path: registry fails at boot with both module IDs.
* Business templates (`migration/business-templates`) that require a module: the seed pack declares `requiresModules` and the importer refuses or prompts to enable.
* Mobile Tauri bundle size: disabled modules must be tree-shaken from the web bundle; `quality/perf-budgets` asserts the `
DEPS: `app-shell/create-cli` (the CLI this extends), `spec-builder/app-level-spec` (`modules:` section). Soft: `app-shell/router-layouts`, `identity/rbac-abac`, `data-layer/jobs-queue`, `business-core/entitlements`, `data-layer/drizzle-schema`. Consumed by `spec-builder/business-profile`, `migration/business-templates`, `app-shell/new-app-drill`.


## PAP-29 [P2 Review M prio1 Backlog] Run the blank-screen-to-running-app drill: time `paperos create` through first spec'd page, deploy and desktop build; record it; answer PAP-5 with numbers
key=app-shell/new-app-drill milestone=Multi-monitor and PWA polish agent=Run by Atlas (Dispatcher) with Forge, Quill and Sentinel in 
blockedBy=['PAP-88', 'PAP-26', 'PAP-22'] blocks=[]
GOAL: PAP-5 asks a measurable question: how quickly do we get from a blank screen to a running app. Every project in this plan claims to shorten that path; none of them measures it. This drill creates a brand-new app from the template with an agent, using only the documented tools, and records the wall-clock time and credit cost to reach five checkpoints: repo exists, first spec'd page renders locally, staging URL live, desktop binary launches, first release candidate cut. Findings become issues; the drill repeats weekly until the numbers stop improving.
SCOPE: In:

* Drill protocol `docs/drills/new-app.md`: fixed scenario (a two-audience app, e.g. "clinic booking": customer books, staff manages a schedule, one table view, one comment thread), fixed starting state (fresh imagine-os repo, empty Linear project), who runs it (Atlas dispatches, Forge builds, Quill writes the two page specs, Sentinel reviews), and what may not be done by hand.
* Timer harness `pnpm drill:new-app` that stamps checkpoints from CLI events, PR merges and deploy webhooks into `reports/drills/new-app-<date>.json` with token spend from `pm-linear/credit-metering`.
* Video: Playwright records the web flow at 375 and 1280 (`quality/video-replays`) and `asciinema` records the terminal; a 3-minute cut is published to the docs.
* Report: `docs/drills/new-app-<date>.md` with the checkpoint table, cost, the top five frictions ranked by minutes lost, and the issues filed for each 
SPEC(first 1200): * Checkpoints and targets for the first run, revised after: C1 repo, mirror, CI, Linear project exist under 10 minutes; C2 two pages from specs render locally under 60 minutes; C3 staging URL live with auth and a seeded tenant under 90 minutes; C4 Linux and macOS desktop builds launch under 150 minutes; C5 release candidate digest in Needs Justin under 240 minutes. Credit target under 150 USD for the full drill.
* Everything through the documented path: `paperos create`, the spec authoring skill, `pm-linear/orchestrator` claiming issues, gates 1 to 4. Any manual intervention is logged as a friction with minutes lost.
* The drill runs in a throwaway imagine-os repo prefixed `drill-` that `forge/repo-bootstrap` deletes afterwards (archive the report first).
* Comparisons across runs are plotted in the docs (`tables/map-chart-views` when available, otherwise a static SVG).
DOD:
* First drill completed end to end with all five checkpoints stamped, report and video published in the docs engine, five or more friction issues filed and linked.
* PAP-5 has a comment with the checkpoint table and the report link; Justin can close it or leave it as the standing scoreboard (no Needs Justin item; informational).
* Second drill scheduled through `quality/release-train` weekly cadence and documented as a recurring Linear issue template.
* `CHANGELOG.md` entry; Linear comment on this issue with the numbers.
EDGE:
* The drill stalls on a missing feature: stamp the checkpoint as `blocked`, file the issue, continue with a documented manual step and count the minutes; do not abort the drill.
* Costs blow past the target because of retries: the report separates first-attempt cost from retry cost so the fix targets the right friction.
* Signed macOS build impossible without Justin's Apple developer credentials: record as an external friction, produce an unsigned build for the checkpoint and note the signing status.
* Orchestrator concurrency limits delay claims: the drill runs during a quiet window; scheduling delays are recorded separately from build time.
* The scenario becomes too familiar to the agents (memorised paths): rotate between three scenarios (clinic, agency, retail) after the second run.
DEPS: `app-shell/create-cli`, `app-shell/app-deploy-pipeline`, `quality/release-train`, `spec-builder/layout-codegen`, `app-shell/feature-modules`. Soft: `app-shell/tauri-desktop`, `quality/video-replays`, `pm-linear/credit-metering`, `pm-linear/orchestrator`, `forge/repo-bootstrap`. Feeds `pm-linear/pap5-decompose` (closure comment) and every project through friction issues.
