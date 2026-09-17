SPECS = {}

SPECS["PAP-13"] = dict(
Goal="""Create the `paperos-template` monorepo that every PaperOS app is cloned from. From a clean checkout, one command builds, typechecks, lints and tests; every later issue drops code into a folder this issue creates. `packages/core` is owned by app-shell: this issue creates its `src/index.ts` barrel and the rule that other projects add sub-folders (`shell/`, `config/`, `pwa/`, `windows/`, `devices/`, `events/`) but never edit the barrel without an app-shell review. The PM Drizzle schema (PAP-100) lives in `packages/pm`, not here.""",
Scope="""In:

* pnpm 10 workspaces, Turborepo 2.x pipelines `build`, `dev`, `lint`, `typecheck`, `test`, `clean`; remote cache off.
* `apps/web` (React 19.1, Vite 7, TypeScript 5.9 strict) rendering one placeholder route.
* Wired-but-empty packages `packages/ui`, `packages/core`, `packages/spec`, `packages/views`, `packages/agents`, `packages/config-ts`, `packages/config-biome`, each with `package.json`, `tsconfig.json`, `src/index.ts` and one passing Vitest test.
* README-stub folders `apps/desktop`, `apps/mobile`, `apps/api`, `specs/`, `docs/`, `.claude/` (CLAUDE.md, `agents/`, `skills/`, `rules/`), `ops/compose`, `ops/ci`.
* `.github/workflows/ci.yml` running `pnpm turbo lint typecheck test build` (Gate 1 hand-off to PAP-78).
* Node 22 LTS pinned (`.nvmrc`, `packageManager`, `engine-strict`).

Out: pages, Tauri (PAP-19), router (PAP-16), PWA (PAP-18), tokens, database code.""",
Spec="""* Root scripts: `dev`, `build`, `lint`, `lint:fix`, `typecheck`, `test`, `test:watch`, `clean`, `check` (all gates locally).
* `turbo.json`: `build` depends on `^build`; `test` and `typecheck` depend on `^build`; outputs `dist/**`, `.vite/**`; inputs include `tsconfig*.json` and `.env.example`.
* TS: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `moduleResolution: bundler`, alias `@paperos/*` -> `packages/*/src`.
* `apps/web/src/main.tsx` mounts `<App/>`; `App` renders "PaperOS template" and `import.meta.env.VITE_GIT_SHA` (Vite `define`).
* `vite.config.ts`: `@vitejs/plugin-react`, `base: process.env.BASE_PATH ?? '/'`, `build.target: 'es2022'`.
* Vitest 3 workspace at root; React tests use jsdom + Testing Library; `passWithNoTests` per package.
* Biome 2.x: 2-space, single quotes, import sorting, `noImportCycles` on.
* CLAUDE.md: folder map, commands, "never edit generated files", link to `docs/template-guide.md` (PAP-24).
* `.editorconfig`, `.gitignore`, `.gitattributes` (LF), `LICENSE` placeholder, `CHANGELOG.md` with Unreleased.""",
**{"Interface contract": """Provides:

* Package names `@paperos/ui`, `@paperos/core`, `@paperos/spec`, `@paperos/views`, `@paperos/agents`; tsconfig presets `@paperos/config-ts/{base,react,node}.json`; Biome preset `@paperos/config-biome`.
* `packages/core/src/index.ts` barrel exporting a `PAPEROS_VERSION` constant; sub-folder ownership table in `packages/core/README.md` (app-shell owns the barrel; data-layer adds `events/`, identity adds `principal.ts`).
* Env vars read at build: `BASE_PATH`, `VITE_GIT_SHA`.
* CI job name `ci / check` that PAP-78 extends; artifact `coverage/`.

Consumes: nothing. Everything downstream imports these names, so renaming any of them is a breaking change requiring an ADR."""},
**{"Definition of done": """* Fresh clone: `pnpm i && pnpm check` green in under 3 minutes on a GitHub-hosted runner.
* `pnpm dev` serves `apps/web` on :5173 and hot-reloads an edit in `packages/ui`.
* Every package has one Vitest test; coverage written to `coverage/`.
* CI green on the PR; badge in README.
* `docs/adr/0001-monorepo-stack.md` records versions and rejected alternatives.
* Linear comment with PR, CI run and the Pages URL once PAP-15 merges."""},
**{"Test plan": """* Unit: Vitest smoke test per package; a test importing `@paperos/core` from `apps/web` proves the alias.
* Static: `pnpm typecheck` with a deliberate circular import in a fixture branch must fail; `engine-strict` error on Node 20 captured.
* Integration: CI runs `pnpm check` on ubuntu-latest and macos-latest; frozen lockfile enforced.
* Visual: placeholder page screenshots at 320, 768, 1280 and 1920 attached to the PR.
* Timing: CI job duration recorded in the PR; fails the DoD if over 3 minutes."""},
Demo="""Reviewer clones the repo, runs `pnpm i && pnpm check && pnpm dev`, opens `http://localhost:5173`, sees "PaperOS template" with the git SHA, edits a string in `packages/ui/src/index.ts` and watches it hot-reload. Under 2 minutes with a warm pnpm store.""",
**{"Edge cases": """* Windows contributors: no symlink-dependent scripts; paths via `node:path`.
* Offline pnpm store: lockfile committed, `--frozen-lockfile` in CI.
* Node mismatch prints a clear error through `engines` and `.npmrc`.
* Turbo cache poisoning: config files are declared inputs.
* Package with zero tests must not fail Vitest."""},
Dependencies="""None; root of the graph. Unblocks PAP-15, PAP-16, PAP-17, PAP-18, PAP-19, PAP-26, PAP-27, PAP-42, PAP-78.""",
Agent="""Built by Forge (Platform Engineer). Reviewed by Sentinel (Code Reviewer).""",
Size="""M: many files, no unknowns; must be exact because everything else builds on it.""",
)

SPECS["PAP-14"] = dict(
Goal="""Decide and publish the device classes, viewport widths, DPRs and input modes PaperOS commits to, as one machine-readable matrix that the quality pipeline screenshots against (PAP-82, PAP-84) and that PAP-21 implements as container queries. The seven widths become the vocabulary every DoD in this plan uses.""",
Scope="""In:

* Market and viewport data for phone, tablet, laptop, desktop, ultra-wide, TV/kiosk and foldable (StatCounter, Steam survey, Apple and Android device lists).
* `packages/core/src/devices/matrix.ts` plus generated `ops/ci/breakpoints.json`.
* Test-device recommendations (real and emulated) with cost.
* Guidance on container queries versus viewport breakpoints, DPR, safe areas, hover and pointer queries.

Out: CSS implementation (PAP-21), component design.""",
Spec="""* Starting point to confirm or overturn with data: `xs 320`, `sm 375`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536`, `3xl 1920`; `tv 3840` documented as optional eighth.
* Entry shape: `{ name, minWidth, exampleDevices[], dpr[], pointer: 'coarse'|'fine'|'both', hover: boolean, orientation, safeArea: boolean }`.
* `pnpm gen:breakpoints` writes `breakpoints.json` from the TS file; CI fails when stale.
* Playwright mapping table per width: preset or `{ viewport, deviceScaleFactor, hasTouch, isMobile }`.
* Foldables: `device-posture` notes; unfolded treated as `md`. TV: 10-foot rules, focus ring minimums, 4K at DPR 1 and 2.
* `docs/research/device-matrix.md` (1,500-2,500 words) with sources, decision, rejected options, review date 2027-01.
* Three physical devices worth buying, with prices.""",
**{"Interface contract": """Provides:

* `BREAKPOINTS: readonly Breakpoint[]` and `DEVICE_CLASSES` from `@paperos/core/devices`; type `BreakpointName = 'xs'|'sm'|'md'|'lg'|'xl'|'2xl'|'3xl'`.
* `ops/ci/breakpoints.json` schema `{ version, breakpoints: [{ name, width, height, deviceScaleFactor, hasTouch, isMobile }] }` read by PAP-82 Playwright projects and PAP-84 video replays without importing TS.
* `PLAYWRIGHT_DEVICES` map for PAP-82.

Consumes: nothing. Changing a width after PAP-82 has baselines requires a baseline regeneration, so the file carries a `version` field."""},
**{"Definition of done": """* `matrix.ts`, `breakpoints.json` and the research doc merged; generator snapshot-tested.
* ADR `docs/adr/0002-device-matrix.md` records the seven widths.
* Placeholder app screenshots at all seven widths via a throwaway Playwright script attached to the PR.
* Sentinel (PAP-82 owner) approves on the PR.
* Linear comment linking the doc."""},
**{"Test plan": """* Unit: Vitest snapshot of `gen:breakpoints` output; type test that `BreakpointName` is exhaustive.
* Static: `pnpm gen:breakpoints --check` in CI detects a hand-edited JSON.
* Visual: seven screenshots of the placeholder page, one per width, plus 375 at DPR 3 and 1920 at DPR 1.
* Review: every numeric claim in the doc has a source URL; reviewer spot-checks three."""},
Demo="""Reviewer opens `docs/research/device-matrix.md`, then runs `pnpm gen:breakpoints && cat ops/ci/breakpoints.json` and `pnpm exec playwright test scripts/matrix-shots.spec.ts` to produce the seven screenshots in `test-results/`. Under 2 minutes.""",
**{"Edge cases": """* Browser zoom 125-200 percent changes effective width; layouts must be tested at zoom.
* Split-screen tablets produce widths between breakpoints; behaviour for any width is defined.
* Virtual keyboard shrinking `100vh`; recommend `100dvh` and `interactive-widget=resizes-content`.
* Fractional DPR on Windows (1.25, 1.5).
* Old kiosks on Chromium 90-ish: state minimum browser versions."""},
Dependencies="""None. Consumed by PAP-21, PAP-20, PAP-82, PAP-84, PAP-70, PAP-154, PAP-158.""",
Agent="""Researched by Scout (Library Evaluator) with Forge confirming feasibility. Reviewed by Sentinel.""",
Size="""S: half a day of research plus a small TS file and generator.""",
)

SPECS["PAP-15"] = dict(
Goal="""Every merge to `main` and every pull request publishes a static build of `apps/web` to GitHub Pages so reviewers, the vision agent (PAP-83) and Justin open a URL instead of running code. This is the imagine-os public demo convention made automatic.""",
Scope="""In:

* `pages-main.yml` and `pages-preview.yml` in `ops/ci/` (symlinked into `.github/workflows/`).
* Production URL `https://imagine-os.github.io/<repo>/` from `main`; previews at `/pr/<n>/`, removed on close.
* Sticky PR comment with preview URL, SHA and a Lighthouse placeholder.
* SPA fallback (`404.html`), correct `base`.
* `<BuildInfo/>` footer badge in `packages/ui`.

Out: Storybook deploy (PAP-75), custom domains, SSR, the Coolify preview environments (PAP-26).""",
Spec="""* Both flows publish to the `gh-pages` branch (root for `main`, `pr/<n>/` for previews) via `peaceiris/actions-gh-pages@v4` with `keep_files: true`; the `closed` event deletes the folder. Pages source is the `gh-pages` branch.
* Build with `BASE_PATH=/<repo>/pr/<n>/ pnpm --filter web build`; inject `VITE_GIT_SHA`, `VITE_BUILD_TIME`, `VITE_PR_NUMBER`.
* Sticky comment via `marocchino/sticky-pull-request-comment@v2`, template `ops/ci/templates/preview-comment.md`.
* Concurrency group per PR cancels stale builds.
* `pnpm demo:url` prints the URL for the current branch (agents paste it into Linear comments).
* `ops/ci/README.md` documents the repo settings checklist and the base-path rule.""",
**{"Interface contract": """Provides:

* URL convention `https://imagine-os.github.io/<repo>/` and `/pr/<n>/`, consumed by PAP-82 (screenshot target), PAP-83 (vision review), PAP-89 (review report) and PAP-22 (prints it after create).
* `<BuildInfo/>` component and `import.meta.env.VITE_GIT_SHA|VITE_BUILD_TIME|VITE_PR_NUMBER` typed in `packages/core/src/config/public.ts` (PAP-17 extends the schema).
* Script `pnpm demo:url`.

Consumes: `BASE_PATH` from PAP-13's `vite.config.ts`. PAP-18 must propagate `BASE_PATH` into the PWA manifest scope."""},
**{"Definition of done": """* A PR yields a working preview within 4 minutes; closing removes the folder.
* Deep link `/<repo>/pr/<n>/some/route` loads the SPA.
* `main` demo linked from README.
* CI smoke test hits the preview and asserts the `<BuildInfo/>` SHA equals the commit.
* Screenshots at 375, 1024 and 1920; README and CHANGELOG updated; Linear comment with both URLs."""},
**{"Test plan": """* Unit: Vitest for `demo:url` URL derivation from `GITHUB_REPOSITORY` and branch or PR number.
* Integration: Playwright job after deploy loads the preview root and a deep link, asserts SHA text and no console errors.
* E2E: open, push twice and close a test PR; verify folder appears, updates, disappears (workflow logs in PR).
* Visual: screenshots at 375, 1024, 1920 of the deployed page."""},
Demo="""Reviewer opens the PR, clicks the preview URL in the sticky comment, confirms the SHA in the footer matches the PR head, then navigates to `/pr/<n>/does-not-exist` and sees the SPA not-found page rather than the GitHub 404. Under a minute.""",
**{"Edge cases": """* Repo renamed: derive `base` from `github.event.repository.name`.
* Fork PRs lack a write token: skip with an explanatory comment.
* Two PRs deploying within a minute race on `gh-pages`: `force_orphan: false` plus one retry.
* Site over 1 GB or asset over 100 MB: `size-limit` check fails clearly.
* Private repo needs GitHub Pro: document publishing to a public `-demo` repo."""},
Dependencies="""PAP-13 (hard: `vite.config.ts` base option). Feeds PAP-18, PAP-22, PAP-51, PAP-82, PAP-83, PAP-89.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer).""",
Size="""S: two workflows and a badge component.""",
)

SPECS["PAP-16"] = dict(
Goal="""Give every PaperOS app one file-based, fully typed router whose pages render inside a layout with named slots (nav, sidebar, main, inspector, command bar, status bar), with slot contents chosen by the page's `page.spec.yaml`. Agents add a page by adding a spec and a route file; the shell does the rest.""",
Scope="""In:

* TanStack Router 1.x with the Vite plugin, routes in `apps/web/src/routes/`.
* `packages/core/src/shell/`: `<AppShell>`, slot registry, `useLayout()`.
* Spec-to-layout adapter reading the `layout` section (interim type in `packages/spec/src/interim.ts` until PAP-116).
* Route metadata: title, breadcrumb, `audience` string (enforced later by PAP-59), default slot visibility.
* Not-found, error boundary and pending routes.
* Panel state in search params (`?inspector=open&sidebar=collapsed`) validated with Zod 4.

Out: navigation content, auth guards, window detach (PAP-21), route codegen (PAP-120).""",
Spec="""* `__root.tsx` renders `<AppShell>`; `_app.tsx` for authenticated pages, `_public.tsx` for marketing and auth; examples `index.tsx`, `_app/dashboard.tsx`, `_app/settings/index.tsx`.
* Grid areas `nav | sidebar | main | inspector`, `commandbar` overlay, `statusbar` bottom; sidebar collapses to a drawer under `md`, inspector under `lg` (interim media queries; PAP-21 replaces them with container queries).
* Slot API: `registerSlot(name, Component, { priority, when })`; pages call `useLayout({ sidebar: <Filters/> })` or declare `layout.slots.sidebar: FiltersPanel` resolved through the component registry (PAP-69).
* Route export: `createFileRoute('/_app/dashboard')({ component, loader, validateSearch, staticData: { spec: 'dashboard' } })`.
* `useSpec(routeId)` loads the parsed spec; `vite-plugin-paperos-specs` imports `specs/**/*.yaml` as JSON.
* `<Slot name="commandbar"/>` reserved for PAP-151.""",
**{"Interface contract": """Provides (from `@paperos/core/shell`):

* `AppShell`, `Slot`, `registerSlot`, `useLayout`, `useSpec`, `useShellSearch`; types `SlotName = 'nav'|'sidebar'|'main'|'inspector'|'commandbar'|'statusbar'`, `RouteStaticData = { spec?: string; audience?: string; title?: string }`.
* Route tree type `AppRouter` exported from `apps/web/src/routeTree.gen.ts` for typed `Link`.
* Convention: route file path mirrors `specs/pages/<name>.spec.yaml`.
* Search-param schema `ShellSearch = { inspector?: 'open'|'closed'; sidebar?: 'expanded'|'collapsed' }`.

Consumes: `LayoutSection` from `@paperos/spec` (interim until PAP-116), component registry `resolveComponent(name)` from PAP-69, `BREAKPOINTS` from PAP-14. PAP-28 later composes the route tree from module manifests through `composeRoutes(modules)`, which this issue exposes as a stub."""},
**{"Definition of done": """* Three example routes render in the shell; a typed `Link` to a missing route fails typecheck.
* Vitest: slot registry, search validation, spec adapter on three fixtures.
* Playwright at all seven widths: drawers at 375 and 768, inspector drawer at 1024, full grid at 1280+; not-found and error routes captured.
* `docs/shell/routing.md` explains adding a route plus spec in under 10 steps; CHANGELOG; Linear comment with preview links."""},
**{"Test plan": """* Unit: slot priority resolution, `when` predicates, `ShellSearch` fallbacks on invalid values, adapter mapping for three spec fixtures.
* Type: `expectTypeOf` test that `Link to="/nope"` errors.
* Integration: Testing Library renders `AppShell` with a fake route and asserts slot content.
* E2E: Playwright visits all example routes at 320, 375, 768, 1024, 1280, 1536, 1920; asserts drawer versus grid mode via `data-layout` attribute; screenshots light and dark.
* Error path: route throwing in loader renders the error boundary with a retry button."""},
Demo="""Reviewer opens the Pages preview, navigates `/`, `/dashboard`, `/settings`, resizes the window from 1920 to 375 watching sidebar and inspector fold into drawers, appends `?inspector=open` to the URL and sees the inspector open. Under 2 minutes.""",
**{"Edge cases": """* Spec names a component missing from the registry: visible `<MissingComponent/>` in dev, logged and hidden in prod.
* Two registrations with equal priority: last wins with a dev warning.
* Invalid search params fall back to defaults.
* Nested layouts under `_app/settings/*` never double-render nav.
* Width under 320 scrolls horizontally rather than overlapping."""},
Dependencies="""PAP-13 (hard). Soft: PAP-116 schema, PAP-70 layout components. Unblocks PAP-22, PAP-24, PAP-21, PAP-54, PAP-62, PAP-63, PAP-70, PAP-128.""",
Agent="""Built by Forge. Reviewed by Sentinel (Code Reviewer) and Quill (spec adapter naming).""",
Size="""M: one library, one adapter, three example routes.""",
)

SPECS["PAP-17"] = dict(
Goal="""One typed, validated configuration layer shared by web, desktop and mobile, with client-side secrets stored in the right place per target (browser: never persisted; desktop: OS keychain; mobile: Keychain or Keystore) so agent-written code cannot leak a key into a bundle. Server-side encryption of stored secrets is a separate data-layer issue (field encryption gap); runtime feature flags move to the app-shell runtime-flags issue; this issue only provides the env-level bootstrap `VITE_FLAGS`.""",
Scope="""In:

* `packages/core/src/config/`: Zod 4 `publicEnvSchema` (`VITE_*`) and `serverEnvSchema`; accessors `publicEnv`, `serverEnv`.
* `.env.example`, `.env.test`, gitignored `.env.local`; `pnpm env:check`.
* `SecretStore` with `WebSecretStore`, `TauriKeychainStore` (`keyring` crate via Tauri command), `MobileSecureStore` (Tauri secure-storage plugin).
* Vite plugin failing the build when any non-`VITE_` variable reaches the bundle.

Out: remote flag service, per-tenant settings, auth token lifecycle (PAP-57), server-side field encryption.""",
Spec="""* `publicEnvSchema`: `VITE_API_URL`, `VITE_APP_NAME`, `VITE_GIT_SHA`, `VITE_ELECTRIC_URL`, `VITE_YJS_URL`, `VITE_SENTRY_DSN?`, `VITE_FLAGS?` (comma list, bootstrap only).
* `serverEnvSchema`: `DATABASE_URL`, `DATABASE_URL_MIGRATOR`, `S3_*`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `STRIPE_SECRET_KEY?`, `OTEL_EXPORTER_OTLP_ENDPOINT?`, `APP_ENCRYPTION_KEY?` (consumed by the field-encryption issue), `NODE_ENV`.
* Parse once at module load; failure throws a table of missing keys.
* `SecretStore`: `get`, `set`, `delete`, `list`; keys namespaced `paperos.<app>.<key>`.
* `getTarget(): 'web'|'desktop'|'ios'|'android'` via `window.__TAURI_INTERNALS__` then UA fallback.
* Rust commands `secret_get|set|delete` in `apps/desktop/src-tauri/src/commands/secrets.rs`; capability limited to the main window.
* `docs/shell/config.md`: which vars go where, CI and Coolify supply, rotation.""",
**{"Interface contract": """Provides (from `@paperos/core/config`):

* `publicEnv: PublicEnv`, `serverEnv: ServerEnv` (Zod-inferred), `publicEnvSchema`, `serverEnvSchema` (other packages extend with `.extend()` and register the extension in `config/registry.ts`).
* `SecretStore` interface and `getSecretStore()`; `getTarget()`, type `Target`.
* Tauri command names `secret_get`, `secret_set`, `secret_delete` (used by PAP-57 for session tokens).
* Env names are the contract for PAP-25 sops files, PAP-26 Coolify injection and PAP-30 role URLs.

Consumes: nothing beyond PAP-13. PAP-19 mounts the Rust commands; until then the desktop backend is compiled but unreachable."""},
**{"Definition of done": """* `pnpm env:check` passes on `.env.example` and fails with a table when a key is removed.
* Vitest: schemas, target detection, `WebSecretStore`; Rust keychain round-trip test (skipped without a keychain, noted).
* Bundle guard proven: a test build with a stray `SECRET=` import fails.
* Linux `secret-service` and macOS Keychain round-trips recorded; settings debug page screenshots at 375, 1024, 1920.
* Docs, `.env.example`, CHANGELOG; Linear comment with recording links."""},
**{"Test plan": """* Unit: schema parsing (missing, empty string, bad URL), `getTarget()` under four fake globals, `WebSecretStore` session semantics.
* Rust: `cargo test` for `secrets.rs` with the `keyring` mock backend.
* Build: CI step builds `apps/web` with `LEAK_TEST=1` and asserts the plugin fails.
* Tree-shaking: `size-limit` asserts `serverEnvSchema` is absent from the web bundle.
* Visual: `/settings/debug` page at 375, 1024, 1920 showing target and public config."""},
Demo="""Reviewer removes `VITE_API_URL` from `.env.local`, runs `pnpm env:check` and reads the table; restores it, runs `pnpm dev:desktop`, opens Settings, stores a test secret, quits, relaunches and sees it read back from the OS keychain. Under 2 minutes on Linux or macOS.""",
**{"Edge cases": """* Headless Linux without a secret service: encrypted-file fallback with a loud warning.
* Empty string counts as missing.
* Two windows setting the same key: last write wins; `list()` is immediate.
* Vitest reads `.env.test` only, never `.env.local`.
* Android Keystore values over 4 KB: chunk or reject with a clear error."""},
Dependencies="""PAP-13 (hard). PAP-19 for native backends (either merge order). Consumed by PAP-20, PAP-22, PAP-26, PAP-35, PAP-37, PAP-57, the runtime-flags and field-encryption issues.""",
Agent="""Built by Forge (Tauri Smith for native stores). Reviewed by Sentinel (Security Auditor).""",
Size="""M: small TS surface plus one Rust command set.""",
)

SPECS["PAP-18"] = dict(
Goal="""Make the web build installable in any browser and load its shell instantly offline, so customers on flaky connections and staff on shared tablets get an app-like experience without a store download. Offline data sync is PAP-36 and PAP-148; this is the shell only.""",
Scope="""In:

* `vite-plugin-pwa` 1.x with Workbox 7 `generateSW` in `apps/web`.
* Manifest: name, short name, theme colours from tokens, 192/512 and maskable icons, screenshots, `display: standalone`, `display_override`, shortcuts for three routes, `id`.
* Precache of HTML, JS, CSS, fonts, icons; runtime caching for API (`NetworkFirst`, 10 s), images (`CacheFirst`, 30 days, 200 entries), fonts (`StaleWhileRevalidate`).
* `registerType: 'prompt'` with `<UpdateToast/>` in `packages/ui`; `<OfflineBanner/>` in `packages/ui` (moved from `core/pwa` so codegen's `ui.offlineBanner` from PAP-120 resolves).
* `useInstallPrompt()` with an iOS instructions sheet.

Out: push transport, offline writes, native updater (PAP-19 reuses the toast).""",
Spec="""* `VitePWA({ registerType:'prompt', manifest, workbox:{ navigateFallback:'index.html', navigateFallbackDenylist:[/^\\/api/], globPatterns, maximumFileSizeToCacheInBytes: 3_000_000, cleanupOutdatedCaches: true, runtimeCaching }, devOptions:{ enabled:false } })`.
* `BASE_PATH` propagates to `start_url`, `scope` and `id` so `/pr/12/` never hijacks `/pr/13/`.
* `pnpm gen:icons` from `packages/ui/assets/logo.svg` via `@vite-pwa/assets-generator`.
* `packages/core/src/pwa/`: `useServiceWorker()` (`needRefresh`, `offlineReady`, `update()`), `useOnline()` (navigator plus heartbeat), `useInstallPrompt()`.
* `skipWaiting` only after the user accepts; `clients.claim()` on activate.
* `<meta name="theme-color">` bound to light and dark tokens; Apple meta tags.
* `ops/ci/lighthouserc.json` asserting installability (feeds PAP-87).""",
**{"Interface contract": """Provides:

* Hooks `useServiceWorker`, `useOnline`, `useInstallPrompt` from `@paperos/core/pwa`; components `UpdateToast`, `OfflineBanner` from `@paperos/ui` (the `ui.offlineBanner` target for PAP-120 codegen).
* Cache names `paperos-api-v1`, `paperos-img-v1`, `paperos-font-v1`; `/api/auth/*` and any response with `Set-Cookie` are never cached (PAP-57 relies on this).
* Event `paperos:sw-updated` on `window` for PAP-19's updater to share the toast.

Consumes: `BASE_PATH` (PAP-13), Pages preview URLs (PAP-15) for scope testing, colour tokens (PAP-66; placeholders until merged)."""},
**{"Definition of done": """* DevTools Application panel shows the manifest without warnings; Lighthouse installability passes on the preview.
* Playwright: load, `setOffline(true)`, reload, shell renders with `<OfflineBanner/>`; online hides it.
* Update toast appears between two builds with a bumped constant.
* Install recorded on Chrome desktop, Android Chrome and iOS Safari.
* Screenshots at all seven widths of standalone mode and the banner; `docs/shell/pwa.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: `useOnline` with mocked `navigator.onLine` and heartbeat failures; install-prompt 14-day dismissal logic.
* Integration: Vitest with `vite-plugin-pwa` config snapshot asserting `scope` and `id` follow `BASE_PATH`.
* E2E: Playwright offline reload test; second-build update-toast test; assert `/api/auth/session` is `no-store` via the SW.
* Visual: banner and toast at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark.
* Lighthouse CI on the preview URL."""},
Demo="""Reviewer opens the Pages preview in Chrome, clicks Install, launches the standalone window, toggles DevTools offline, reloads and sees the shell with the offline banner; toggles online and the banner disappears. Under 90 seconds.""",
**{"Edge cases": """* iOS 50 MB quota: `purgeOnQuotaError: true` on image cache.
* Dismissed install prompt: no re-ask for 14 days.
* SW on localhost breaks HMR: `devOptions.enabled=false`.
* Stale precache after a failed deploy: `cleanupOutdatedCaches`.
* Browsers without SW: hooks return safe defaults."""},
Dependencies="""PAP-13 (hard), PAP-15 (scope testing, now encoded as blocks). Soft: PAP-66 tokens.""",
Agent="""Built by Forge. Reviewed by Sentinel (Visual Inspector for install UI).""",
Size="""S: mostly configuration plus three hooks and two components.""",
)

SPECS["PAP-19"] = dict(
Goal="""Umbrella: wrap the same web bundle in Tauri 2 so PaperOS apps ship as native, auto-updating desktop apps on Linux, macOS and Windows. Work is split into three children that can run in parallel after the first merges; this issue closes when the integration test below passes on a tagged build.""",
Scope="""Children:

1. Tauri desktop scaffold, capabilities and plugins (`apps/desktop`, least-privilege capability files, menu, tray, dev scripts).
2. Desktop CI installers for Linux, macOS and Windows (`ops/ci/desktop.yml`, tauri-action, draft release, Rust lint).
3. Updater, single instance and deep links (`latest.json`, 0.0.1 to 0.0.2 proof, `paperos://` routing).

Out of the whole tree: code signing and notarisation (separate app-shell signing issue), mobile (PAP-20), window manager (PAP-21).""",
Spec="""* `apps/desktop/src-tauri` is the single Cargo crate in the root workspace; `frontendDist` points at `apps/web/dist`, `devUrl` at Vite; desktop builds always use `BASE_PATH=/`.
* `identifier: os.imagine.paperos.<app>`; window 1280x800, min 960x600; `titleBarStyle: 'Overlay'` on macOS; CSP `default-src 'self'; connect-src https: wss:; img-src 'self' data: blob: https:`.
* Rust toolchain pinned in `rust-toolchain.toml`; `cargo clippy -D warnings` and `cargo fmt --check` in CI.
* Commands live in `src-tauri/src/commands/` (`app_info`, `open_path`, `secret_*` from PAP-17).
* Children own the detailed specs; this issue owns `docs/shell/desktop.md` and the integration test.""",
**{"Interface contract": """Provides:

* Tauri commands `app_info`, `open_path`, `list_displays` (stub, completed by PAP-21), `secret_*`; TS bridge `@paperos/core/native/desktop` exporting `isDesktop()`, `getVersion()`, `onDeepLink(cb)`.
* Deep-link scheme `paperos://open/<route>` handled by the router (PAP-57 uses `paperos://auth/callback`).
* Release artifacts on a draft GitHub release: `.deb`, `.rpm`, `.AppImage`, `.dmg`, `.msi`, `.nsis`, plus `latest.json` (Tauri updater format).
* Capability files under `src-tauri/capabilities/` that PAP-20 extends with `mobile.json`.

Consumes: `SecretStore` Rust commands (PAP-17), `UpdateToast` and `paperos:sw-updated` (PAP-18), CI secrets `TAURI_SIGNING_PRIVATE_KEY` (updater key, not OS signing) from PAP-25 sops."""},
**{"Definition of done": """* All three children Done.
* Integration test: tag `v0.0.2-test` produces installers for three OSes; a 0.0.1 install on Linux and macOS prompts to update to 0.0.2 and relaunches (recording).
* `docs/shell/desktop.md` covers prerequisites, dev loop, release; CHANGELOG; Linear comment with the release-draft link.
* Unsigned builds documented with the Gatekeeper and SmartScreen workaround until the signing issue lands."""},
**{"Test plan": """* Unit: Vitest for the TS bridge; `cargo test` for commands; `tauri` schema validation of capability files.
* Integration: `pnpm build:desktop` on ubuntu, macos and windows runners; installer smoke (`--version` output) on each.
* E2E: updater proof 0.0.1 to 0.0.2; single-instance test launching twice and asserting one process; deep-link test via `xdg-open paperos://open/settings`.
* Visual: window screenshots at 960x600, 1280x800, 1920x1080 on Linux and macOS."""},
Demo="""Reviewer downloads the AppImage from the draft release, runs it, sees the web bundle with the version in `<BuildInfo/>`, runs `xdg-open paperos://open/settings` and watches the running instance navigate. Under 2 minutes.""",
**{"Edge cases": """* Wayland versus X11 tray and placement differences (tray may be absent on GNOME).
* Corporate proxy blocks the updater: log and retry silently.
* Close requested during a background task: intercept and confirm if dirty.
* Windows without install-dir write access: NSIS per-user mode.
* Hosted macOS runner minutes are billed at 10x: CI builds macOS only on tags and `workflow_dispatch`."""},
Dependencies="""PAP-13 (hard). PAP-17 either order. Unblocks PAP-20, PAP-21, PAP-24, PAP-145, the signing issue.""",
Agent="""Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for capabilities and CSP, Code Reviewer for Rust).""",
Size="""L as an umbrella; children are M, M, M.""",
)

SPECS["PAP-20"] = dict(
Goal="""Umbrella: extend the Tauri 2 project to iOS and Android so the same web bundle runs as a native mobile app with camera, haptics, secure storage, share sheet and biometrics through one TypeScript shim that degrades gracefully on web. Three children; this issue closes when the integration test passes on both emulators.""",
Scope="""Children:

1. Tauri mobile project init and CI builds (Android debug APK, iOS simulator build; needs the non-Linux runner issue in forge for iOS).
2. Capabilities shim `packages/core/src/native/capabilities.ts` with `NativeCapabilities` and `WebCapabilities`.
3. Mobile plugin wiring and device proofs (camera, haptics, biometric, secure storage, share, geolocation, notification; safe areas; back button).

Out: store submission and signing (signing issue), touch gesture system (PAP-154), push transport.""",
Spec="""* Single crate: `tauri android init` and `tauri ios init` inside `apps/desktop/src-tauri`; `apps/mobile` holds platform assets and scripts (ADR records this).
* Android `minSdk 26`, `targetSdk 35`, ABIs arm64-v8a and x86_64; iOS deployment target 15.0 with Info.plist usage strings.
* Capability file `mobile.json` grants mobile plugins to the main window only.
* Viewport `viewport-fit=cover, interactive-widget=resizes-content`; `env(safe-area-inset-*)` mapped to `--safe-*` tokens.
* Dev: `pnpm dev:android`, `pnpm dev:ios` with Vite bound to `0.0.0.0`, printing LAN IP and a QR.
* Test devices per PAP-14: Pixel 8 emulator, iPhone 15 simulator, iPad 11.""",
**{"Interface contract": """Provides (from `@paperos/core/native`):

* `Capabilities` interface: `camera`, `haptics`, `biometrics`, `secureStore`, `share`, `geo`, `notify`, each `{ available: boolean; request(): Promise<Status>; status: 'granted'|'denied'|'prompt'|'unavailable' }`; hook `useCapability(name)`.
* `getTarget()` returns `'ios'|'android'` (PAP-17 type extended).
* `--safe-top|right|bottom|left` CSS variables consumed by PAP-70 layout components and PAP-154.
* CI artifacts `app-debug.apk` and `PaperOS.app` (simulator) on every PR touching `apps/`.

Consumes: PAP-19 crate and capabilities; `SecretStore` (PAP-17) for `secureStore`; `BREAKPOINTS` (PAP-14) for target sizes; hosted macOS runner from the forge runner issue for iOS builds."""},
**{"Definition of done": """* All three children Done.
* Integration test: on Android emulator and iOS simulator, navigate three routes, scan a QR code, trigger haptics, store and read a secret (recording).
* `docs/shell/mobile.md` covers toolchain, dev loop and the signing hand-off; CHANGELOG; Linear comment with CI artifact links."""},
**{"Test plan": """* Unit: Vitest for capability selection by target and every web fallback (Web Share, `navigator.vibrate`, WebAuthn, MediaDevices).
* Rust: mobile feature build under `clippy -D warnings`.
* Integration: CI builds the debug APK on ubuntu and the simulator app on macos-14.
* E2E: Maestro or Appium flow on the emulator covering the four actions above; skipped with a visible note when biometrics are unavailable.
* Visual: screenshots at 375x812, 390x844, 768x1024 portrait and landscape; safe-area check on a notch device."""},
Demo="""Reviewer runs `pnpm dev:android` with a Pixel emulator open, scans the printed QR from a second device, taps "Scan" on the demo route to read it back, feels the haptic and stores a secret that survives an app restart. Under 2 minutes with the emulator warm.""",
**{"Edge cases": """* Camera denied: `status:'denied'` plus a settings deep link.
* Android back: router `history.back()`; confirm exit at root.
* Keyboard covering inputs: verify `resizes-content` on both WebViews.
* Low-memory WebView kill: route restored from `sessionStorage`.
* Simulator without biometrics: shim returns `available:false`."""},
Dependencies="""PAP-19 (hard), PAP-17 (secure store), PAP-14 (target sizes), forge non-Linux runners (iOS CI). Feeds PAP-154, PAP-157, PAP-37 camera uploads.""",
Agent="""Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for plugin permissions).""",
Size="""L as an umbrella; children are M, S, M.""",
)

SPECS["PAP-21"] = dict(
Goal="""Umbrella: implement the responsive layer from PAP-14 as container queries and a window manager that lets any panel detach into its own OS window, move across monitors, remember placement and re-dock, so staff can spread one app over several screens. Three children; closes on the two-display integration test.""",
Scope="""Children:

1. Container-query breakpoints and hooks (`breakpoints.css`, Tailwind v4 theme variables, `useBreakpoint`, `useContainerSize`; replaces PAP-16 interim media queries).
2. Tauri `WindowManager` (detach, dock, list, focus, `moveToDisplay`, `list_displays` command, topology-hash persistence).
3. Web pop-out fallback and panel affordances (`window.open`, `BroadcastChannel` mirror, "Pop out" button, chips, `/_window/<panelId>` route, docs).

Out: cross-window data coherence (PAP-145), kiosk launch (PAP-23).""",
Spec="""* `@container` names `shell`, `sidebar`, `main`, `inspector`, `panel`; Tailwind utilities `cq-md:` via plugin.
* `WebviewWindowBuilder` per detached panel, label `panel-<id>`; `list_displays` returns `{ id, name, bounds, scale, primary }`.
* Topology hash = sorted `${name}:${w}x${h}@${scale}`; mismatch falls back to primary centre.
* Store `{ panels: { [id]: { state, bounds?, display? } }, presets }`, Zod-validated with `version` migrations, in `localStorage` plus `tauri-plugin-window-state`.
* Closing a detached window docks it; `dock()` closes the child; cap 12 detached windows.
* Keyboard `Ctrl/Cmd+Shift+P` toggles pop-out on the focused panel.""",
**{"Interface contract": """Provides (from `@paperos/core/layout` and `@paperos/core/windows`):

* `useBreakpoint(): BreakpointName`, `useContainerSize(ref)`, CSS custom properties `--bp-xs..--bp-3xl`.
* `WindowManager` with `detach(panelId)`, `dock(panelId)`, `list()`, `focus(id)`, `moveToDisplay(id, displayId)`, `subscribe(cb)`; type `PanelState`.
* Route `/_window/$panelId` in PAP-16's tree with a chrome-less layout.
* Event `paperos:panel-state` on `BroadcastChannel('paperos-windows')`, the channel PAP-145 extends.
* `ops/ci/breakpoints.json` unchanged; PAP-82 switches to it here.

Consumes: `BREAKPOINTS` (PAP-14), Tauri crate and `list_displays` stub (PAP-19), `AppShell` slots (PAP-16)."""},
**{"Definition of done": """* All three children Done.
* Integration test on Linux and macOS: detach inspector, move to display two, quit, relaunch; window returns to display two; unplug display two, relaunch; window recovers to primary (recordings).
* Web: pop-out popup mirrors state via BroadcastChannel (Playwright multi-page).
* Screenshots at all seven widths plus a two-display composite; `docs/shell/windows.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: topology hash, store migrations v1 to v2, dock and detach reducer, breakpoint mapping from container width.
* Rust: `list_displays` against a mocked monitor list.
* Integration: Testing Library asserting `AppShell` switches `data-layout` by container width, not viewport.
* E2E: Playwright multi-page pop-out test; Tauri WebDriver test for detach and dock on Linux.
* Visual: seven widths plus 2560 ultra-wide; two-display composite from the recording."""},
Demo="""Reviewer launches the desktop build, clicks "Pop out" on the inspector, drags it to a second monitor, quits and relaunches; the inspector reopens where it was. Closing the popped-out window docks it back. Under 2 minutes.""",
**{"Edge cases": """* Popup blockers on web: inline hint, panel stays docked.
* Scale change while running: re-query on `scale-changed`.
* Child window crash: main re-docks via `onCloseRequested` or heartbeat.
* Panel needing main-window selection opens with an empty state and message.
* Wayland forbids positioning: persist size only, documented."""},
Dependencies="""PAP-14, PAP-19 (hard), PAP-16 (window route, now encoded). Pairs with PAP-145; consumed by PAP-23, PAP-70.""",
Agent="""Built by Forge (Tauri Smith) with Nova consulting on the sync boundary. Reviewed by Sentinel.""",
Size="""L as an umbrella; children are S, M, M.""",
)

SPECS["PAP-22"] = dict(
Goal="""`paperos create <app>` takes a blank imagine-os repo to a running, tracked, deployable app in one command: clone the template at a pinned tag, rename identifiers, push to GitHub and Forgejo, configure CI, Pages and Coolify, and create a Linear project seeded with starter issues. It is the direct answer to PAP-5 and the entry point the drill (PAP-29) times.""",
Scope="""In:

* `packages/cli` published as `@paperos/cli` (bin `paperos`), `tsup`, `commander` 13, `@clack/prompts`, `execa`, `simple-git`, `octokit`, `@linear/sdk`.
* `create <name> [--repo] [--linear-project] [--no-push] [--template <ref>] [--without <modules>] [--yes] [--dry-run]`, `doctor`, `demo:url`.
* Idempotent state in `.paperos/create.state.json`; logs in `.paperos/create.log`.
* Starter issues from `templates/linear/starter-issues.yaml`.

Out: repo provisioning (repos pre-exist), mirror and secrets wiring (delegated to `forge bootstrap`, PAP-51), template upgrades (forge upgrade-path issue).""",
Spec="""* Steps: validate name; verify repo exists and is empty; `degit` template at tag; rename map over a curated glob list; `pnpm i && pnpm check`; commit; push `main`; `forge bootstrap <repo> --linear-project <id>`; enable Pages; copy `deploy.yml` and `preview.yml` (PAP-26) with app name templated; create Linear project (team PAP, state planned, milestones, starter issues with the `Spec` label); print URLs.
* Name rules: kebab-case 3-40 chars, not reserved; derived `PascalName`, `identifier os.imagine.paperos.<name>`.
* Tokens from env or `SecretStore`; `doctor` reports presence, never values.
* Exit codes 0 success, 2 validation, 3 external API failure with retry hint.
* Clients behind interfaces `GitHubClient`, `ForgejoClient`, `LinearClient` with fakes.
* `--without` passes through to PAP-28 module removal once it lands; until then it warns and continues.""",
**{"Interface contract": """Provides:

* Bin `paperos` with `create`, `doctor`, `demo:url`, later `upgrade` (forge upgrade issue) and `kiosk install` (PAP-23); machine-readable `--json` summary `{ repo: { github, forgejo }, pages, linearProject, steps: [{ name, status, ms }] }` that PAP-29's timer harness reads.
* State file schema `.paperos/create.state.json` v1.
* `templates/linear/starter-issues.yaml` schema `{ title, description, labels[], state }`.

Consumes: `forge bootstrap` CLI contract (PAP-51: exit codes, `[ok]/[changed]/[skip]` lines), Linear label and state ids (PAP-91), Pages settings (PAP-15), `deploy.yml` template (PAP-26), `SecretStore` (PAP-17)."""},
**{"Definition of done": """* Against a throwaway repo: green CI, live Pages URL, staging URL and Linear project within 10 minutes (recording).
* Re-run is a no-op; `--force` redoes steps.
* Vitest: name validation, rename map, state machine, client fakes; nightly e2e against a sandbox repo.
* `paperos doctor` screenshot; generated app at 375, 1024, 1920.
* `docs/cli/create.md`; README quick start; CHANGELOG; Linear comment with the demo app's links."""},
**{"Test plan": """* Unit: name validator table (40 cases), rename map on a fixture template (binary files untouched), state machine resume from each step, exit codes.
* Contract: fake clients record calls; snapshot of the Linear `projectCreate` and `issueCreate` payloads.
* Integration: `--dry-run` prints the plan and performs zero writes (asserted by fakes).
* E2E nightly: real run on `imagine-os/cli-sandbox`, then teardown; duration and step timings posted to the workflow summary.
* Visual: generated app home at 375, 1024, 1920 from its Pages URL."""},
Demo="""Reviewer runs `paperos doctor`, then `paperos create demo-clinic --repo imagine-os/demo-clinic --linear-project --yes`, watches ten steps complete, opens the printed Pages URL and the Linear project with three starter issues. Roughly 8 minutes wall clock; the reviewer watches the first two and last one.""",
**{"Edge cases": """* Target repo not empty: abort without `--force-empty`; never delete history.
* GitHub rate limit: backoff and resume from state.
* Linear project name collision: suffix date and warn.
* Missing Forgejo token: skip mirror, mark `pending`, `forge bootstrap` finishes later.
* Running inside an existing git directory: refuse."""},
Dependencies="""PAP-16 (real template), PAP-47 and PAP-51 (mirror and bootstrap), PAP-91 (labels and states), PAP-15, PAP-26. Feeds PAP-28, PAP-29, PAP-108.""",
Agent="""Built by Forge; Atlas (Dispatcher) reviews the Linear seeding. Reviewed by Sentinel.""",
Size="""M: orchestration of existing pieces with strong tests.""",
)

SPECS["PAP-23"] = dict(
Goal="""From one CLI flag, launch a PaperOS desktop build in kiosk mode on Linux that opens one full-screen synced window per connected display, or several browser windows in parallel-browser mode, so a shop, clinic or warehouse runs staff dashboards and signage from one cheap box.""",
Scope="""In:

* Rust flags `--kiosk`, `--displays all|1,2`, `--routes /board,/queue`, `--parallel-browser`, `--reload-hours 24`, `--watchdog`, `--public`.
* `ops/kiosk/`: systemd user unit, `cage`/`sway` recipe, `unclutter`, auto-login notes for Debian, Ubuntu and Fedora.
* Kiosk window options: fullscreen, always on top, no decorations, not closable, no context menu or devtools, exit chord `Ctrl+Alt+Shift+Q` (disabled with `--public`).
* Watchdog, `/_kiosk/health`, journald logging, nightly reload.
* `paperos kiosk install` in `@paperos/cli`.

Out: signage content, remote fleet management.""",
Spec="""* Startup: parse flags, enumerate displays via PAP-21 `list_displays`, create `WebviewWindow` `kiosk-<n>` per selected display with display bounds, load `${routes[n % routes.length]}?kiosk=1&display=n`.
* `kiosk=1` makes `AppShell` hide nav and command bar and set `data-kiosk` for 10-foot type scale (PAP-14 rules).
* Parallel-browser: spawn `chromium --kiosk --app=<url> --window-position=<x>,<y> --user-data-dir=<tmp/n>` per display via the shell plugin sidecar; supervise children.
* Watchdog thread polls every 10 s; recreate after 2 s backoff, 10 tries, then exit non-zero for systemd.
* Coherence via PAP-145 (`--follow-primary` mirrors selection and filters).""",
**{"Interface contract": """Provides:

* Search params `kiosk=1&display=<n>` and the `data-kiosk` attribute on `<html>` that PAP-16 and PAP-70 style against.
* HTTP `GET /_kiosk/health` on `127.0.0.1:<port>` returning `{ ok, displays, windows, uptimeS }` scraped by PAP-40.
* systemd unit `paperos-kiosk.service` and config `~/.config/paperos/kiosk.toml` (`routes`, `displays`, `reloadHours`, `public`).
* CLI subcommand `paperos kiosk install|status`.

Consumes: `WindowManager.list_displays` (PAP-21), `BroadcastChannel('paperos-windows')` (PAP-145), PWA cache for offline boot (PAP-18)."""},
**{"Definition of done": """* On a two-display Linux box or Xvfb VM, `paperos-desktop --kiosk --displays all --routes /board,/queue` shows both routes fullscreen (recording).
* Kill one window: restored within 5 s (recording).
* Cold boot to app under 60 s on Ubuntu 24.04 via the systemd recipe.
* Rust tests for flag parsing and display assignment; Vitest for kiosk params.
* Screenshots at 1920x1080, 3840x2160 and portrait 1080x1920; `docs/shell/kiosk.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: Rust flag parser table; route cycling for 1, 2, 3 displays with 2 routes; watchdog backoff.
* Integration: Vitest that `kiosk=1` hides nav and sets `data-kiosk`.
* E2E: Xvfb with two screens in CI, launch, assert two windows via `xdotool`, kill one, assert respawn within 5 s.
* Health: `curl /_kiosk/health` asserts `windows: 2`.
* Visual: three display sizes above, light and dark."""},
Demo="""Reviewer runs `paperos-desktop --kiosk --displays all --routes /board,/queue` on a laptop with an external monitor: two fullscreen windows appear, one per screen; `xdotool` kills one and it returns within 5 s; `Ctrl+Alt+Shift+Q` exits. Under 2 minutes.""",
**{"Edge cases": """* Hot-plugged display: monitor-change listener opens or closes windows.
* Zero displays: exit code 4.
* Network down at boot: shell loads from cache, shows banner, retries.
* DPMS blanking disabled in compositor recipe.
* Portrait-rotated display: bounds already rotated; verified."""},
Dependencies="""PAP-21 (window manager, displays), PAP-145 (coherence). Soft: PAP-22 install subcommand, PAP-18.""",
Agent="""Built by Forge (Tauri Smith, Ops Runner for systemd). Reviewed by Sentinel (Edge Case Hunter).""",
Size="""M: Rust launcher plus ops recipes.""",
)

SPECS["PAP-24"] = dict(
Goal="""Write the guide every new Claude Code session reads before touching the template: where things live, how a page goes from spec to route to test, how each target runs and ships, and which conventions are non-negotiable. Docs are checked in CI so they cannot rot.""",
Scope="""In:

* `docs/template-guide.md` (3,000-5,000 words) plus `docs/shell/*` pages cross-linked and indexed.
* Root `CLAUDE.md` rewritten to a 300-word summary with the "never do" list.
* `.claude/rules/*.md`: naming, imports, tests, specs-before-code, no secrets, commit format (PAP-46).
* Worked example `/_app/invoices` end to end with snippets extracted from `docs/examples/` and compiled in CI.
* Target cheat-sheets: web, desktop, mobile, kiosk, Pages, staging.
* Troubleshooting FAQ from real P0 errors.

Out: component guidelines (PAP-77), spec tutorial (PAP-127), character docs (PAP-115).""",
Spec="""* Sections: Purpose; Folder map table (path, owner project, what goes here, what never goes here); Commands; Adding a page (10 numbered steps with paths); Data access (PAP-35); Auth and audiences; Targets; Quality gates; Conventions; Glossary.
* `pnpm docs:check` verifies snippet markers match `docs/examples/` sources, every backticked `pnpm <script>` exists in `package.json`, and token budgets (CLAUDE.md under 1,200 tokens, section 4 under 900).
* Front-matter `title`, `owner`, `updated` for PAP-128 rendering; Mermaid diagrams for folder tree, request flow, release flow.
* Unbuilt references marked `(planned: PAP-n)`.""",
**{"Interface contract": """Provides:

* `docs/template-guide.md`, `CLAUDE.md`, `.claude/rules/*.md` as the onboarding path PAP-108 (skills library) and PAP-93 (session playbook) link to.
* `docs/examples/invoices/` compiled example (spec, route, component, test) that PAP-120 uses as a codegen fixture.
* Script `pnpm docs:check` that PAP-78 Gate 1 runs.
* Front-matter schema `{ title, owner, updated }` shared with PAP-128.

Consumes: real behaviour of PAP-16, PAP-19, PAP-18, PAP-17; commit format from PAP-46; the docs engine (PAP-128) for in-app rendering, GitHub rendering until then."""},
**{"Definition of done": """* Guide, CLAUDE.md, rules and example merged; `pnpm docs:check` green.
* A fresh Claude Code session given only the guide adds the example page and passes Gate 1 without a question (Atlas runs the trial; transcript linked).
* Token counts under budget; Mermaid renders on GitHub.
* Docs screenshots at 375, 1024, 1920; CHANGELOG; Linear comment with the trial transcript."""},
**{"Test plan": """* Static: `docs:check` snippet-marker test, script-name test, token-count test with fixtures that fail.
* Compile: `docs/examples/invoices` typechecks and its Vitest test passes in CI.
* Trial: one scripted Claude Code session (PAP-96 harness or manual) adds a page from the guide; success criterion is Gate 1 green with zero clarifying questions.
* Visual: GitHub render and, once PAP-128 exists, in-app render at 375, 1024, 1920."""},
Demo="""Reviewer opens `CLAUDE.md`, follows section 4 of the guide to add a `/_app/hello` route with a spec, runs `pnpm check`, and sees the page in `pnpm dev`. Under 2 minutes for an experienced reader; the agent trial transcript shows the same path unassisted.""",
**{"Edge cases": """* Renamed command: `docs:check` catches it.
* Section over budget: CI warns above limits.
* Windows separators: POSIX paths with a note.
* No Rust toolchain: desktop section starts with a skip-if check.
* Stale screenshots: stamped with the SHA taken."""},
Dependencies="""PAP-16, PAP-19 (hard). Soft: PAP-17, PAP-18, PAP-46, PAP-93, PAP-128. Consumed by every build issue and PAP-108.""",
Agent="""Written by Quill (Spec and Documentation Lead) with Forge supplying commands. Reviewed by Atlas (trial) and Sentinel.""",
Size="""M: long document plus a checker script.""",
)

SPECS["PAP-25"] = dict(
Goal="""Create the single self-hosted environment that PAP-45, PAP-30, PAP-140, PAP-96, PAP-36 and PAP-88 assume: a Hetzner VPS running Coolify behind Caddy, the `PAPEROS_DOMAIN` zone, object storage for backups, an age/sops key pair, a Resend sending domain and the `imagine-os/paperos-infra` repo holding all of it as code. One Needs Justin item collects every credential ask.""",
Scope="""In:

* Hetzner project and one `cpx31` (Ubuntu 24.04, 8 GB) with an upgrade path documented.
* Coolify with proxy switched to Caddy before any resource; admin for Justin; `COOLIFY_TOKEN` in GitHub secrets and sops.
* DNS records `@`, `app.`, `api.`, `staging.`, `git.`, `collab.`, `sync.`, `orchestrator.`, `s3.`, `*.preview.`; Let's Encrypt via Caddy; DNS-only (no proxying).
* Object Storage buckets `paperos-backups` (restic) and `paperos-files`.
* age key pair; `ops/secrets/*.enc.yaml`; Tailscale for SSH; UFW 80/443 only.
* Resend account with verified domain, SPF and DKIM.

Out: application services (each project deploys its own), Postgres (PAP-30), Forgejo (PAP-45).""",
Spec="""* `ops/bootstrap.sh` idempotent with `--dry-run`.
* `docs/runbooks/host.md`: `production` and `staging` as separate Coolify projects with separate databases, domains and secrets files.
* Resource naming `paperos-<env>-<service>`; label `paperos.owner=<agent>`.
* Health convention `GET /healthz` returning `{ ok, version, sha }`, checked every 30 s.
* `ops/secrets/INVENTORY.md`: name, service, rotation owner, last rotated; CI fails when an `*.enc.yaml` key is missing from it.
* Cost table in the ADR (target under 40 EUR/month).
* Weekly `docker system prune` timer; disk alert at 80 percent.""",
**{"Interface contract": """Provides:

* Env var `PAPEROS_DOMAIN` and the host list above; Coolify API base `https://coolify.PAPEROS_DOMAIN` and token secret name `COOLIFY_TOKEN` (PAP-26, PAP-88).
* sops recipients: `justin` and `orchestrator` age keys; file layout `ops/secrets/<env>-<service>.enc.yaml` (PAP-17 env names are the keys).
* Buckets `paperos-backups` (PAP-30 WAL, PAP-45 restic, the object-storage DR issue) and `paperos-files` (PAP-37 alternative to MinIO).
* SMTP credentials secret `RESEND_API_KEY` and sender `noreply@PAPEROS_DOMAIN` (the email package issue, PAP-57).
* Tailnet hostname `paperos-vps`.

Consumes: nothing. Credential asks (Hetzner, registrar, Resend, Apple and Windows signing are separate) go in one Needs Justin issue filed on day one."""},
**{"Definition of done": """* `git.`, `staging.` and `app.` hosts answer over valid TLS (screenshots at 1280 and 375).
* SSH only over the tailnet; public nmap shows 80 and 443 (output attached).
* `sops -d ops/secrets/example.enc.yaml` works with the orchestrator key; Justin confirms his recovery key once.
* Resend test mail passes SPF and DKIM (headers attached).
* `restic snapshots` lists the first snapshot of `/data/coolify`.
* Runbook, ADR, CHANGELOG, Linear comment with URLs and cost table."""},
**{"Test plan": """* Unit: `bats` tests for `bootstrap.sh --dry-run` idempotency on a `multipass` VM.
* Integration: CI job decrypts a fixture with a CI-scoped age key and asserts the inventory check fails on an unlisted secret.
* Security: nmap from outside; `ssh` attempt from a non-tailnet IP times out (log).
* Ops: Coolify health endpoint for a placeholder service flips red when the container is stopped (screenshot).
* Visual: Coolify dashboard and the TLS placeholder pages at 1280 and 375."""},
Demo="""Reviewer opens `https://staging.PAPEROS_DOMAIN` (valid padlock), `https://coolify.PAPEROS_DOMAIN` (login), runs `sops -d ops/secrets/example.enc.yaml` with the shared key and `restic snapshots`. Under 2 minutes.""",
**{"Edge cases": """* No domain yet: `*.sslip.io` for staging; switching later is one env var and a Caddy reload.
* Hetzner identity verification delay: file the Needs Justin item first, verify scripts in a local VM meanwhile.
* Coolify install fails on the 24.04 kernel: pin the tested version.
* Cloudflare orange cloud breaks ACME and WebSockets: grey cloud everywhere.
* sops key loss: recovery key printed once for Justin; re-key runbook."""},
Dependencies="""None; the earliest infra issue. Unblocks PAP-26, PAP-30, PAP-45, PAP-96, PAP-140, the signing, email, field-encryption and DR issues.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).""",
Size="""M: many small external steps, all scriptable except the credential asks.""",
)

SPECS["PAP-26"] = dict(
Goal="""Turn a merge into a running application: Docker images for `apps/web`, `apps/api` and `apps/worker`, staging on merge to `main`, production on tag, per-PR preview environments and a two-minute rollback, all through Coolify on the PAP-25 host. The release train (PAP-88), e2e flows (PAP-86) and the drill (PAP-29) all deploy through this.""",
Scope="""In:

* `apps/web/Dockerfile` (Turbo prune, Vite build, Caddy static with SPA fallback and immutable caching) and `apps/api/Dockerfile` (Node 22 distroless); `healthz` stub in `apps/api` until PAP-35 replaces it; `apps/worker` image once PAP-43 exists.
* `deploy.yml`: build, tag `sha-<short>` and `main`, push to GHCR and mirror to Forgejo registry (after PAP-50), then Coolify deploy webhooks.
* Production on `v*` tags (PAP-52) deploying the same digest; never rebuild.
* `preview.yml`: `pr-<n>.preview.PAPEROS_DOMAIN`, removed on close.
* Migrations as a pre-deploy step with `drizzle-kit migrate` (PAP-32).
* `pnpm deploy:rollback <env> <sha>`.

Out: Pages static demo (PAP-15), desktop and mobile artifacts (PAP-19, PAP-20).""",
Spec="""* Image budgets: web under 40 MB, api under 200 MB; CI fails above.
* `docker/build-push-action` with GHA cache; no-change rebuild under 3 minutes.
* Deploy job polls Coolify deployment status until `finished`, then asserts `GET /healthz` and `/__version` equals the SHA; failure posts to Linear via PAP-97 when available.
* Concurrency `deploy-<env>` cancels superseded staging deploys; production never cancels.
* Secrets injected by Coolify from sops (`ops/secrets/<env>-api.enc.yaml`); Trivy scan before push (PAP-80).
* `paperos create` copies `deploy.yml` and `preview.yml` with resource names templated.""",
**{"Interface contract": """Provides:

* Images `ghcr.io/imagine-os/<app>-web|api|worker:sha-<short>`; Coolify resources `paperos-<env>-web|api|worker`.
* Endpoints `/healthz` and `/__version` on every service (PAP-25 convention).
* Preview URL pattern `https://pr-<n>.preview.PAPEROS_DOMAIN` consumed by PAP-82, PAP-86, PAP-83.
* Workflow inputs: repository secrets `COOLIFY_TOKEN`, `GHCR_TOKEN`; reusable workflow `imagine-os/paperos-infra/.github/workflows/deploy.yml@main` with inputs `app`, `env`, `sha`.
* Command `pnpm deploy:rollback`.

Consumes: host, domain and token (PAP-25), staging and production databases (PAP-30), `drizzle-kit migrate` (PAP-32), tags (PAP-52), env schema (PAP-17)."""},
**{"Definition of done": """* Merge to `main` deploys `https://staging.PAPEROS_DOMAIN`; `/__version` shows the SHA.
* Tag `v0.0.1-test` deploys the same digest to production (digests compared in the log), then the tag is removed.
* PR preview live within 5 minutes and removed within 5 minutes of close.
* Rollback restores the previous SHA on staging in under 2 minutes (timed log).
* Broken-migration PR blocked before rollout; staging keeps serving.
* `docs/runbooks/deploy.md`, ADR, CHANGELOG, Linear comment."""},
**{"Test plan": """* Unit: Vitest for the deploy script's Coolify status polling and version assertion against a mocked API.
* Build: image size checks and Trivy gate in CI.
* Integration: staging deploy smoke (`/healthz`, `/__version`) after every merge; preview smoke on every PR.
* Failure injection: PR with `SELECT 1/0` migration; assert workflow red, staging version unchanged.
* Timing: rollback timed with `date` in the job log; must be under 120 s."""},
Demo="""Reviewer opens the latest `deploy.yml` run, clicks through to `https://staging.PAPEROS_DOMAIN/__version` and matches the SHA to the merge commit, then opens any PR's `pr-<n>.preview` URL. Under 90 seconds.""",
**{"Edge cases": """* GHCR outage: Forgejo registry as fallback pull source.
* Wrong `BASE_PATH`: web images always use `/`.
* Two merges in a minute: the concurrency group keeps the newest.
* Rotated Coolify token: clear failure pointing at `INVENTORY.md`.
* Fork PR previews skipped with a comment.
* Rollout fails health after a successful migration: previous image redeployed; migration rollback manual and documented."""},
Dependencies="""PAP-13, PAP-25, PAP-30 (hard). Soft: PAP-17, PAP-32, PAP-35, PAP-43, PAP-52, PAP-80. Consumed by PAP-86, PAP-88, PAP-29, PAP-22, PAP-147.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor for secrets handling).""",
Size="""M: two Dockerfiles, two workflows, one rollback script, all provable.""",
)

SPECS["PAP-27"] = dict(
Goal="""Make localisation a template default before pages multiply: ICU message catalogs, locale negotiation, `Intl` helpers, RTL flip, pseudo-locale testing and a translation skill agents run. Retrofitting i18n after 200 pages is the most expensive refactor in this plan, so it lands in P1.""",
Scope="""In:

* `packages/i18n`: Lingui 5 with macros `t`, `Trans`, `plural`, `select`; catalogs `apps/web/src/locales/<locale>/messages.po`; `pnpm i18n:extract|compile` wired into Gate 1.
* Locale negotiation: tenant default (PAP-58 setting), user preference (PAP-57 profile), `Accept-Language`, browser; Tauri reads OS locale.
* Helpers `formatNumber`, `formatCurrency`, `formatDate`, `formatRelative`, `formatList`, `formatUnit`, `parseNumber`.
* RTL via CSS logical properties and `dir` on `<html>`; pseudo-locale `en-XA`.
* Translation skill `.claude/skills/translate` producing catalog PRs.

Out: tenant-authored content translation, machine-translation runtime.""",
Spec="""* Source strings live in code; catalogs are the only translation store.
* Lint bans `toLocaleString` and `new Intl.*` outside the package.
* Auto-generated message IDs with explicit IDs for reusable terms; CI warns above 2 percent fuzzy entries, fails above 10 percent for enabled locales.
* Catalogs lazy-loaded; `en` runtime under 8 KB gzipped.
* Dates stored UTC; tenant timezone from PAP-58; formatting never guesses.
* `ar` uses Arabic-Indic digits only when the tenant opts in.""",
**{"Interface contract": """Provides (from `@paperos/i18n`):

* `useLocale(): { locale, dir, timeZone, currency }`, `LocaleProvider`, macros re-exported from Lingui, `format*` helpers taking `Money = { amountMinor: bigint; currency: string }` from `@paperos/core/money` (the canonical type; JSON wire encoding is a decimal string).
* `parseNumber(input, locale)` used by PAP-164 editors.
* Catalog file convention and `pnpm i18n:*` scripts that PAP-78 runs.
* Skill `translate` in PAP-108 format.

Consumes: tokens per script (PAP-66), tenant settings (PAP-58), user profile (PAP-57); PAP-116 later validates spec strings through the same extractor."""},
**{"Definition of done": """* Template renders in `en`, `es`, `ar`, `en-XA` with a switcher; screenshots at 375 and 1280 per locale; `ar` mirrored with no clipping.
* Adding a literal without extracting fails CI (demo PR).
* Translation skill produces an `es` PR that Quill merges.
* Currency and date table across six locales green.
* Pseudo-locale column green in PAP-82; `docs/platform/i18n.md`, ADR, CHANGELOG, Linear comment."""},
**{"Test plan": """* Unit: format helpers across `en-US`, `de-DE`, `ar-EG`, `ja-JP`, `hi-IN`, `pt-BR`; plural forms for Arabic and Polish; `parseNumber` with comma and dot decimals.
* Static: lint rule tests for banned `Intl` calls and string concatenation next to JSX text.
* Integration: negotiation order test with tenant, user and header permutations.
* E2E: Playwright switches locale, asserts `dir="rtl"` and no horizontal overflow at 375 in `ar`.
* Visual: four locales at 375 and 1280, light and dark."""},
Demo="""Reviewer opens the preview, switches the locale menu to Arabic: layout mirrors, dates and currency reformat; switches to `en-XA` and sees accented, elongated strings revealing any hard-coded text. Under a minute.""",
**{"Edge cases": """* Fragment concatenation detected by lint.
* Long German compounds caught by pseudo-locale expansion.
* Mixed direction: `unicode-bidi: isolate` on data spans.
* Tenant changes default locale mid-session: applies at next navigation.
* Locale enabled without a catalog: fall back to `en` with a staff-visible warning."""},
Dependencies="""PAP-13, PAP-66 (hard). Soft: PAP-57, PAP-58, PAP-116, PAP-164. Consumed by PAP-126, PAP-179, PAP-191, PAP-207.""",
Agent="""Built by Forge (Platform Engineer) with Iris on RTL components. Reviewed by Quill and Sentinel.""",
Size="""M: one package, a lint rule and a skill.""",
)

SPECS["PAP-28"] = dict(
Goal="""Umbrella: make every platform capability a removable module so the brief's "build everything in, remove what an app does not need" is cheap. Capability projects export a manifest, `app.spec.yaml` lists modules, `paperos create --without` omits them, tenants toggle optional ones at runtime, and dead-code checks keep the template honest. Three children; closes on the CI removal matrix.""",
Scope="""Children:

1. Module manifest and registry (`module.ts` contract, Zod schema, `packages/core/modules` loader, dependency resolution, `knip` baseline).
2. Router, spec, permissions, jobs and migrations integration (route tree composition in PAP-16, `modules:` validator rule with PAP-117, per-module migration sets in PAP-32, `permissions` into PAP-59, `jobs` into PAP-43).
3. `paperos create --without`, tenant module toggles and the CI removal matrix (settings page, runtime 404 and API rejection, retained data, purge command behind Needs Justin).

Out: business template seed packs (PAP-207), entitlement pricing (PAP-178).""",
Spec="""* Core modules `shell`, `identity`, `data`, `design-system`, `spec`, `input`, `i18n` are non-removable; everything else declares `optional: true`.
* Cross-module coupling only via `emit()` from `packages/core/events` (data-layer event bus issue) or explicit `dependsOn`; lint bans direct imports across optional boundaries.
* `drizzle/<module>/*.sql` applied for enabled modules only; `_migrations_modules` records them.
* Disabled module data is retained; `pnpm modules:purge <id>` is a separate destructive command.
* `paperos create` writes the module list into the Linear project description.""",
**{"Interface contract": """Provides (from `@paperos/core/modules`):

* `ModuleManifest = { id, title, version, routes, navItems, entities, permissions, jobs, settingsSchema, integrations, dependsOn: string[], optional: boolean }` and `defineModule()`.
* `loadModules(appSpec)` returning `ResolvedModules`; `composeRoutes(modules)` (PAP-16 stub filled here); `useModuleEnabled(id)`.
* Table `tenant_module` (`tenant_id`, `module_id`, `enabled`, `updated_by`) and oRPC `modules.list|toggle`.
* `app.spec.yaml` `modules:` shape agreed with PAP-117: `{ enabled: string[], defaultForNewTenants: string[], tenantToggleable: string[] }`.

Consumes: event bus `emit` (data-layer events issue), `can()` (PAP-59), `defineJob` (PAP-43), migration runner (PAP-32), CLI (PAP-22), validator (PAP-117, PAP-118)."""},
**{"Definition of done": """* All three children Done.
* Integration test: `paperos create demo --without payroll,crm,growth` builds, passes `pnpm check` and shows no CRM or payroll navigation; CI matrix removing each optional module stays green; tenant admin disables `canvas` at runtime and the route 404s, nav item vanishes, API rejects, data survives re-enable.
* `knip` clean; `docs/platform/modules.md`, ADR, CHANGELOG, Linear comment."""},
**{"Test plan": """* Unit: manifest Zod validation, dependency resolution (missing, cyclic, disabled parent), route collision detection.
* Static: boundary lint rule with passing and failing fixtures; `knip` in Gate 1.
* Integration: migration runner applies only enabled modules on a fresh database; `_migrations_modules` asserted.
* E2E: Playwright toggles `canvas` off and on as tenant admin; customer principal cannot see the settings page.
* CI matrix: one job per optional module with `--without <id>`."""},
Demo="""Reviewer opens Settings, Modules as tenant admin, switches off Canvas, sees the nav item disappear and `/canvas` return the not-found page, switches it back on and the data is intact. Under 90 seconds.""",
**{"Edge cases": """* B depends on A, tenant disables A: settings blocks with the dependency list; API enforces the same.
* Already-applied migration of a disabled module: retained and ignorable in `db:check`.
* Storybook globs only enabled packages.
* Two modules claim one route: boot fails naming both.
* Seed pack requiring a module: importer refuses or prompts to enable."""},
Dependencies="""PAP-22, PAP-117 (hard), data-layer event bus issue (coupling rule). Soft: PAP-16, PAP-32, PAP-43, PAP-59, PAP-178. Consumed by PAP-29, PAP-126, PAP-207.""",
Agent="""Built by Forge (Platform Engineer) with Quill on the spec section. Reviewed by Sentinel.""",
Size="""L as an umbrella; children are M, M, M.""",
)

SPECS["PAP-29"] = dict(
Goal="""PAP-5 asks a measurable question: how fast from a blank screen to a running app. This drill creates a new app from the template with agents using only documented tools and stamps wall-clock time and credit cost at five checkpoints. PAP-5 stays open as the standing scoreboard; PAP-95 must not close it (the two specs now agree). Findings become issues; the drill repeats weekly.""",
Scope="""In:

* Protocol `docs/drills/new-app.md`: fixed scenario (clinic booking, two audiences, one table, one comment thread), fixed starting state, roles (Atlas dispatches, Forge builds, Quill writes two specs, Sentinel reviews), and what may not be done by hand.
* Timer harness `pnpm drill:new-app` reading `paperos create --json` step timings, PR merge events and deploy webhooks into `reports/drills/new-app-<date>.json` with spend from PAP-99.
* Video at 375 and 1280 (PAP-84) plus `asciinema` terminal; a 3-minute cut in the docs.
* Report with checkpoint table, cost, top five frictions by minutes lost, issues filed.

Out: fixing the frictions (they become issues).""",
Spec="""* Checkpoints and first-run targets: C1 repo, mirror, CI, Linear project under 10 min; C2 two spec'd pages render locally under 60 min; C3 staging with auth and a seeded tenant under 90 min; C4 Linux and macOS desktop builds launch under 150 min; C5 release-candidate digest in Needs Justin under 240 min; credits under 150 USD.
* Everything through `paperos create`, the spec skill, the orchestrator (PAP-96) and gates 1-4; manual steps logged as frictions.
* Throwaway repo `drill-<date>` removed by PAP-51 after archiving the report.
* Scenario rotates clinic, agency, retail after the second run.""",
**{"Interface contract": """Provides:

* `reports/drills/new-app-<date>.json` schema `{ scenario, startedAt, checkpoints: [{ id, at, ms, status: 'ok'|'blocked' }], creditsUsd: { firstAttempt, retries }, frictions: [{ minutes, issue }] }` rendered by the docs and PAP-88's digest.
* Comment format on PAP-5: checkpoint table plus report link; PAP-95 links here instead of closing PAP-5.
* Recurring Linear issue template "Weekly new-app drill".

Consumes: `paperos create --json` (PAP-22), deploy status (PAP-26), release-candidate flow (PAP-88), codegen (PAP-120), modules (PAP-28), credit metering (PAP-99), video replays (PAP-84)."""},
**{"Definition of done": """* First drill completed with all five checkpoints stamped; report and video in the docs; five or more friction issues filed and linked.
* PAP-5 comment with the table and link; no Needs Justin item.
* Weekly recurrence configured via PAP-88 and the issue template.
* CHANGELOG; Linear comment with the numbers."""},
**{"Test plan": """* Unit: harness parses fixture events into checkpoints; blocked-checkpoint handling; cost split first-attempt versus retries.
* Integration: dry drill against the sandbox repo with fake timings validates the JSON against its schema.
* Review: Sentinel (Edge Case Hunter) checks every manual intervention appears as a friction with minutes.
* Visual: report page at 375 and 1280; 3-minute video plays in the docs engine."""},
Demo="""Reviewer opens the report page, reads the five-row checkpoint table with times and cost, plays the 3-minute cut, then opens PAP-5 and sees the same table as the latest comment. Under 2 minutes.""",
**{"Edge cases": """* Missing feature stalls the drill: stamp `blocked`, file the issue, continue with a documented manual step.
* Retry storms inflate cost: report separates first-attempt from retry cost.
* No Apple credentials: unsigned macOS build counts for C4 with signing status noted.
* Orchestrator concurrency delays: scheduling wait recorded separately from build time.
* Agents memorise the scenario: rotation after run two."""},
Dependencies="""PAP-22, PAP-26, PAP-28, PAP-88, PAP-120 (hard). Soft: PAP-19, PAP-84, PAP-96, PAP-99, PAP-51. Feeds PAP-95 and every project through friction issues.""",
Agent="""Run by Atlas (Dispatcher) with Forge, Quill and Sentinel in their roles.""",
Size="""M: a protocol, a harness and one long run.""",
)
